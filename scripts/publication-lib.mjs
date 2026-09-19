import fs from 'node:fs/promises';
import path from 'node:path';
import { parse as parseYaml, stringify } from 'yaml';
import { marked } from 'marked';
import { articlePage, parseStory, publicAssets, validSlug } from './story-lib.mjs';
import { postIdentity } from './post-layout.mjs';
import { today } from './story-lib.mjs';

export async function publicationFiles(source) {
  const stat = await fs.lstat(source);
  if (!stat.isDirectory() || stat.isSymbolicLink()) throw new Error('Choose a real publication directory containing index.md and assets/.');
  const hasStory = await fs.access(path.join(source, 'story/index.md')).then(() => true).catch(error => { if (error.code === 'ENOENT') return false; throw error; });
  const hasContent = await fs.access(path.join(source, 'content/index.md')).then(() => true).catch(error => { if (error.code === 'ENOENT') return false; throw error; });
  if (hasStory && hasContent) throw new Error('Both story/index.md and content/index.md exist; choose one authoring source.');
  const organized = hasStory || hasContent;
  const index = path.join(source, hasStory ? 'story/index.md' : hasContent ? 'content/index.md' : 'index.md');
  if ((await fs.lstat(index)).isSymbolicLink()) throw new Error('The article must not be a symlink.');
  let markdown = await fs.readFile(index, 'utf8');
  const files = new Map([['index.md', markdown]]);
  if (organized) {
    const references = new Set();
    marked.walkTokens(marked.lexer(markdown), token => {
      if ((token.type === 'image' || token.type === 'link') && token.href.startsWith('../images/')) references.add(token.href);
      else if (token.type === 'image' && !/^(https?:|data:)/.test(token.href)) throw new Error('Local article images must use ../images/filename links.');
    });
    const imageRoot = path.join(source, 'images');
    for (const reference of references) {
      const relative = reference.slice('../images/'.length);
      if (!relative || relative.includes('\\') || relative.split('/').some(part => !part || part === '..' || part === '.') || /[?#%]/.test(relative)) throw new Error(`Invalid public image reference: ${reference}`);
      const file = path.join(imageRoot, relative);
      const real = await fs.realpath(file);
      const allowed = await fs.realpath(imageRoot);
      if (!real.startsWith(allowed + path.sep)) throw new Error('Referenced image must stay within images/.');
      files.set(`assets/${relative}`, await fs.readFile(file));
      markdown = markdown.replaceAll(reference, `assets/${relative}`);
    }
    files.set('index.md', markdown);
    return files;
  }
  const assets = path.join(source, 'assets');
  const assetStat = await fs.lstat(assets).catch(error => { if (error.code === 'ENOENT') return null; throw error; });
  if (assetStat?.isSymbolicLink()) throw new Error('The assets directory must not be a symlink.');
  for (const file of await publicAssets(assets)) files.set(`assets/${file}`, await fs.readFile(path.join(assets, file)));
  return files;
}

export async function createNumberedPost(root, name) {
  const identity = postIdentity(name);
  const content = path.join(root, 'content');
  await fs.mkdir(content, { recursive: true });
  const entries = await fs.readdir(content, { withFileTypes: true });
  for (const entry of entries) {
    if (!entry.isDirectory() || !/^\d/.test(entry.name)) continue;
    const other = postIdentity(entry.name);
    if (other.number === identity.number) throw new Error(`Post number ${identity.number} already exists: ${entry.name}`);
  }
  const template = await fs.readFile(path.join(root, 'templates/story.md'), 'utf8');
  const directory = path.join(content, name);
  await fs.mkdir(directory);
  for (const folder of ['analysis', 'images', 'story']) await fs.mkdir(path.join(directory, folder));
  for (const folder of ['analysis', 'images']) await fs.writeFile(path.join(directory, folder, '.gitkeep'), '');
  await fs.writeFile(path.join(directory, 'story/index.md'), template.replace('{{date}}', today()).replace('{{slug}}', identity.slug));
  await fs.writeFile(path.join(directory, 'README.md'), `# ${name}\n\nWrite in [story/index.md](story/index.md). Put research in analysis/ and images in images/. Link selected images with ../images/filename.png.\n\nFrom the repo root, run npm run story:preview -- ${name} or npm run build:stories.\n\nKeep status: draft until ready. Keep the slug stable after publication. Folder numbers order projects; ideaId links to the separate idea tracker.\n`);
  return directory;
}

export async function importStory(root, source, slug) {
  if (!validSlug(slug)) throw new Error('Use a lowercase, hyphenated story slug.');
  const destination = path.join(root, 'content/stories', slug);
  if (path.resolve(source) === path.resolve(destination)) throw new Error('Source is already the story directory.');
  const files = await publicationFiles(source);
  parseStory(files.get('index.md'), slug);
  const manifest = path.join(destination, '.imported.json');
  let previous = [];
  try {
    previous = JSON.parse(await fs.readFile(manifest, 'utf8'));
  } catch (error) {
    if (error.code !== 'ENOENT') throw error;
    try {
      await fs.access(path.join(destination, 'index.md'));
      throw new Error('A manually authored story already uses this slug; choose another slug.');
    } catch (existing) { if (existing.code !== 'ENOENT') throw existing; }
  }
  for (const file of previous) {
    if (typeof file !== 'string' || (file !== 'index.md' && !file.startsWith('assets/')) || file.includes('\\') || file.split('/').some(part => !part || part === '..' || part === '.')) throw new Error('Invalid import manifest.');
  }
  for (const [file, value] of files) {
    await fs.mkdir(path.dirname(path.join(destination, file)), { recursive: true });
    await fs.writeFile(path.join(destination, file), value);
  }
  for (const file of previous) if (!files.has(file)) await fs.unlink(path.join(destination, file)).catch(error => { if (error.code !== 'ENOENT') throw error; });
  await fs.writeFile(manifest, JSON.stringify([...files.keys()], null, 2) + '\n');
  return { files: files.size, destination };
}

export async function previewStory(root, source, slug) {
  if (!validSlug(slug)) throw new Error('Use a lowercase, hyphenated story slug.');
  const files = await publicationFiles(source);
  const match = files.get('index.md').replace(/^\uFEFF/, '').match(/^---\r?\n([\s\S]*?)\r?\n---(?:\r?\n|$)([\s\S]*)$/);
  if (!match) throw new Error('The article needs YAML metadata.');
  const data = parseYaml(match[1]);
  if (!data || !['draft', 'published'].includes(data.status)) throw new Error('Status must be draft or published.');
  const story = parseStory(`---\n${stringify({ ...data, status: 'published' })}---\n${match[2]}`, slug, '9999-12-31');
  const output = path.join(root, '_preview');
  const destination = path.join(output, 'stories', slug);
  await fs.mkdir(destination, { recursive: true });
  const html = articlePage(story).replace('<meta charset="UTF-8">', '<meta charset="UTF-8">\n  <meta name="robots" content="noindex, nofollow">');
  await fs.writeFile(path.join(destination, 'index.html'), html);
  for (const [file, value] of files) {
    if (file === 'index.md') continue;
    await fs.mkdir(path.dirname(path.join(destination, file)), { recursive: true });
    await fs.writeFile(path.join(destination, file), value);
  }
  await fs.mkdir(path.join(output, 'public'), { recursive: true });
  for (const css of ['home.css', 'stories.css']) await fs.copyFile(path.join(root, 'public', css), path.join(output, 'public', css));
  for (const file of ['index.html', 'feed.xml']) {
    await fs.copyFile(path.join(root, 'stories', file), path.join(output, 'stories', file));
  }
  return destination;
}
