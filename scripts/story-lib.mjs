import fs from 'node:fs/promises';
import path from 'node:path';
import { marked, Renderer } from 'marked';
import { parse as parseYaml } from 'yaml';
import { postIdentity } from './post-layout.mjs';

export const SITE = 'https://www.datacuse.com';
export const BLURB = 'Small discoveries, curious maps, and stories about Syracuse—one question at a time.';
export const START = '<!-- stories:start -->';
export const END = '<!-- stories:end -->';
export const escape = value => String(value).replace(/[&<>"']/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[char]);
export const validSlug = slug => /^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(slug) && !['assets', 'index', 'feed'].includes(slug);
export const today = () => new Intl.DateTimeFormat('en-CA', { timeZone: 'America/New_York', year: 'numeric', month: '2-digit', day: '2-digit' }).format(new Date());

export function dateIsValid(value, allowMonth = false) {
  if (typeof value !== 'string' || !(allowMonth ? /^\d{4}-\d{2}(?:-\d{2})?$/ : /^\d{4}-\d{2}-\d{2}$/).test(value)) return false;
  const full = value.length === 7 ? `${value}-01` : value;
  const date = new Date(`${full}T12:00:00Z`);
  return !Number.isNaN(date.valueOf()) && date.toISOString().slice(0, 10) === full;
}

export function dateLabel(value) {
  const full = value.length === 7 ? `${value}-01` : value;
  return new Intl.DateTimeFormat('en-US', { year: 'numeric', month: 'long', ...(value.length === 10 ? { day: 'numeric' } : {}), timeZone: 'UTC' }).format(new Date(`${full}T12:00:00Z`));
}

function validateMetadata(data, name, legacy = false) {
  for (const key of ['title', 'summary', 'category']) {
    if (typeof data[key] !== 'string' || !data[key].trim()) throw new Error(`${name}: ${key} is required.`);
  }
  if (!dateIsValid(data.date, legacy)) throw new Error(`${name}: date must be a real ${legacy ? 'YYYY-MM or ' : ''}YYYY-MM-DD date.`);
}

export function parseStory(text, slug, asOf = today()) {
  if (!validSlug(slug)) throw new Error(`Invalid story directory: ${slug}`);
  const match = text.replace(/^\uFEFF/, '').match(/^---\r?\n([\s\S]*?)\r?\n---(?:\r?\n|$)([\s\S]*)$/);
  if (!match) throw new Error(`${slug}: start with YAML metadata between --- lines.`);
  const data = parseYaml(match[1]);
  if (!data || !['draft', 'published'].includes(data.status)) throw new Error(`${slug}: status must be draft or published.`);
  if (data.status === 'draft') return null;
  validateMetadata(data, slug);
  if (data.date > asOf) return null;
  if (!match[2].trim()) throw new Error(`${slug}: published story has no body.`);
  const renderer = new Renderer();
  renderer.image = ({ href, title, text }) => {
    return `<a class="story-image" href="${escape(href)}" aria-label="Open full-size image: ${escape(text)}"><img src="${escape(href)}" alt="${escape(text)}"${title ? ` title="${escape(title)}"` : ''} loading="lazy"></a>`;
  };
  return { title: data.title.trim(), summary: data.summary.trim(), category: data.category.trim(), date: data.date, ideaId: data.ideaId || '', slug, url: `/stories/${slug}/`, html: marked.parse(match[2], { async: false, renderer }), body: match[2] };
}

export async function readStories(root, asOf = today()) {
  const legacy = JSON.parse(await fs.readFile(path.join(root, 'content/existing-stories.json'), 'utf8'));
  if (!Array.isArray(legacy)) throw new Error('existing-stories.json must be a list.');
  for (const story of legacy) {
    validateMetadata(story, 'Existing story', true);
    if (!/^\/projects\/[a-z0-9-]+\/$/.test(story.url)) throw new Error(`Invalid existing story URL: ${story.url}`);
  }
  const source = path.join(root, 'content/stories');
  const entries = await fs.readdir(source, { withFileTypes: true }).catch(error => { if (error.code === 'ENOENT') return []; throw error; });
  const published = [];
  const numbered = await fs.readdir(path.join(root, 'content'), { withFileTypes: true });
  const numbers = new Set();
  const slugs = new Set();
  for (const entry of numbered) {
    if (!/^\d/.test(entry.name)) continue;
    if (entry.isSymbolicLink()) throw new Error('Post directories must not be symlinks.');
    if (!entry.isDirectory()) continue;
    postIdentity(entry.name);
    const directory = path.join(root, 'content', entry.name);
    const markdown = await fs.readFile(path.join(directory, 'story/index.md'), 'utf8');
    const identity = postIdentity(entry.name, markdown);
    if (numbers.has(identity.number)) throw new Error(`Duplicate post number: ${identity.number}`);
    if (slugs.has(identity.slug)) throw new Error(`Duplicate post slug: ${identity.slug}`);
    numbers.add(identity.number);
    slugs.add(identity.slug);
    // Incomplete draft images must not block the published-site build.
    if (!parseStory(markdown, identity.slug, asOf)) continue;
    const { publicationFiles } = await import('./publication-lib.mjs');
    const files = await publicationFiles(directory);
    const story = parseStory(files.get('index.md'), identity.slug, asOf);
    story.assets = new Map([...files].filter(([name]) => name !== 'index.md'));
    published.push(story);
  }
  for (const entry of entries) {
    if (entry.isSymbolicLink()) throw new Error('Story sources must not be symlinks.');
    if (!entry.isDirectory()) continue;
    const text = await fs.readFile(path.join(source, entry.name, 'index.md'), 'utf8');
    const story = parseStory(text, entry.name, asOf);
    if (slugs.has(entry.name)) throw new Error(`Duplicate source for ${entry.name}; remove the old imported copy.`);
    if (story) published.push(story);
  }
  const all = [...legacy.filter(story => story.date <= asOf), ...published];
  if (new Set(all.map(story => story.url)).size !== all.length) throw new Error('Duplicate story URL.');
  all.sort((a, b) => b.date.localeCompare(a.date) || a.url.localeCompare(b.url));
  return { all, published };
}

export function storyCards(stories) {
  return stories.map(story => `<article><p class="label">${escape(story.category)} &middot; <time datetime="${story.date}">${dateLabel(story.date)}</time></p><h3><a href="${escape(story.url)}">${escape(story.title)}</a></h3><p>${escape(story.summary)}</p></article>`).join('\n');
}

function shell({ title, description, url, body, article }) {
  const canonical = `${SITE}${url}`;
  const structured = article ? `<script type="application/ld+json">${JSON.stringify({ '@context': 'https://schema.org', '@type': 'BlogPosting', headline: title, description, datePublished: article.date, mainEntityOfPage: canonical, author: { '@type': 'Person', name: 'Sam Edelstein', url: 'https://samedelstein.com/about/' } }).replaceAll('<', '\\u003c')}</script>` : '';
  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${escape(title)} | DataCuse</title>
  <meta name="description" content="${escape(description)}">
  <link rel="canonical" href="${canonical}">
  <link rel="alternate" type="application/rss+xml" title="DataCuse Stories &amp; Notes" href="${SITE}/stories/feed.xml">
  <meta property="og:type" content="${article ? 'article' : 'website'}">
  <meta property="og:site_name" content="DataCuse">
  <meta property="og:title" content="${escape(title)}">
  <meta property="og:description" content="${escape(description)}">
  <meta property="og:url" content="${canonical}">
  <meta name="twitter:card" content="summary">
  ${article ? `<meta property="article:published_time" content="${article.date}">` : ''}
  ${structured}
  <link rel="stylesheet" href="/public/home.css">
  <link rel="stylesheet" href="/public/stories.css">
</head>
<body>
  <a class="skip-link" href="#main-content">Skip to main content</a>
  <header class="site-header"><nav class="wrap navigation" aria-label="Primary"><a class="brand" href="/">Data<span>Cuse</span></a><div><a href="/#projects">Tools</a><a href="/stories/" aria-current="${article ? 'false' : 'page'}">Stories</a><a href="/#about">About</a></div></nav></header>
  <main id="main-content" class="wrap story-wrap">${body}</main>
  <footer class="site-footer"><div class="wrap"><p>Independent work by <a href="https://samedelstein.com/about/">Sam Edelstein</a></p><nav aria-label="More"><a href="/stories/">All stories</a><a href="/stories/feed.xml">RSS feed</a><a href="mailto:sam.i.edelstein@gmail.com">Contact</a></nav></div></footer>
</body>
</html>
`;
}

export function archivePage(stories) {
  return shell({ title: 'Stories & notes', description: BLURB, url: '/stories/', body: `<header class="story-heading"><h1>Stories &amp; notes</h1><p class="story-deck">${escape(BLURB)}</p><p><a href="/stories/feed.xml">Subscribe by RSS</a> <span class="note">— add this feed to your preferred reader.</span></p></header><section class="story-list" aria-label="All stories, newest first">${storyCards(stories) || '<p>The first stories are on their way.</p>'}</section>` });
}

export function articlePage(story) {
  return shell({ title: story.title, description: story.summary, url: story.url, article: story, body: `<article><header class="story-heading"><p class="label">${escape(story.category)} &middot; <time datetime="${story.date}">${dateLabel(story.date)}</time></p><h1>${escape(story.title)}</h1><p class="story-deck">${escape(story.summary)}</p><p class="byline">By <a href="https://samedelstein.com/about/">Sam Edelstein</a></p></header><div class="story-body">${story.html}</div><aside class="story-end"><p><a href="/stories/">More stories about Syracuse</a> &middot; <a href="/stories/feed.xml">Subscribe by RSS</a></p><p class="note">Have a correction or a local question? <a href="mailto:sam.i.edelstein@gmail.com">Send a note.</a></p></aside></article>` });
}

export function rssFeed(stories) {
  const items = stories.map(story => {
    const url = `${SITE}${story.url}`;
    // Month-only legacy dates remain month-only on the site; RSS pubDate is
    // optional, so do not invent a day for them.
    const date = story.date.length === 10 ? `<pubDate>${new Date(`${story.date}T12:00:00Z`).toUTCString()}</pubDate>` : '';
    return `<item><title>${escape(story.title)}</title><link>${url}</link><guid isPermaLink="true">${url}</guid><description>${escape(story.summary)}</description><category>${escape(story.category)}</category>${date}</item>`;
  }).join('\n');
  return `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom"><channel>
<title>DataCuse Stories &amp; Notes</title><link>${SITE}/stories/</link><description>${escape(BLURB)}</description><language>en-us</language>
<atom:link href="${SITE}/stories/feed.xml" rel="self" type="application/rss+xml"/>
${items}
</channel></rss>
`;
}

export function updateHomepage(home, stories) {
  if (home.split(START).length !== 2 || home.split(END).length !== 2 || home.indexOf(START) > home.indexOf(END)) throw new Error('Homepage must have one ordered pair of stories:start / stories:end markers.');
  const block = `${START}\n      <p class="section-intro">${escape(BLURB)}</p>\n      <div class="story-list">\n${storyCards(stories.slice(0, 3))}\n      </div>\n      <p class="source-links"><a href="/stories/">Browse all stories</a><a href="/stories/feed.xml">Subscribe by RSS</a></p>\n      ${END}`;
  return home.slice(0, home.indexOf(START)) + block + home.slice(home.indexOf(END) + END.length);
}

export async function publicAssets(directory, relative = '') {
  const entries = await fs.readdir(directory, { withFileTypes: true }).catch(error => { if (error.code === 'ENOENT') return []; throw error; });
  const files = [];
  for (const entry of entries) {
    if (entry.isSymbolicLink()) throw new Error(`Asset symlinks are not supported: ${entry.name}`);
    const name = path.posix.join(relative, entry.name);
    if (entry.isDirectory()) files.push(...await publicAssets(path.join(directory, entry.name), name));
    else if (entry.isFile()) files.push(name);
  }
  return files;
}

export async function buildStories(root, asOf = today()) {
  const { all, published } = await readStories(root, asOf);
  const homePath = path.join(root, 'index.html');
  const home = updateHomepage(await fs.readFile(homePath, 'utf8'), all);
  const output = new Map([['stories/index.html', archivePage(all)], ['stories/feed.xml', rssFeed(all)]]);
  for (const story of published) {
    output.set(`stories/${story.slug}/index.html`, articlePage(story));
    if (story.assets) {
      for (const [file, contents] of story.assets) output.set(`stories/${story.slug}/${file}`, contents);
    } else {
      const assets = path.join(root, 'content/stories', story.slug, 'assets');
      for (const file of await publicAssets(assets)) output.set(`stories/${story.slug}/assets/${file}`, await fs.readFile(path.join(assets, file)));
    }
  }
  const manifestPath = path.join(root, 'stories/.generated.json');
  const previous = await fs.readFile(manifestPath, 'utf8').then(JSON.parse).catch(error => { if (error.code === 'ENOENT') return []; throw error; });
  // Delete only specific files recorded by the previous build. Never recursively
  // remove a directory; preserve hand-authored pages and unrelated assets.
  for (const file of previous) {
    if (typeof file !== 'string' || !file.startsWith('stories/') || file.includes('\\') || file.split('/').some(part => !part || part === '.' || part === '..')) throw new Error('Invalid generated-file manifest.');
  }
  for (const [file, contents] of output) {
    const destination = path.join(root, file);
    await fs.mkdir(path.dirname(destination), { recursive: true });
    await fs.writeFile(destination, contents);
  }
  for (const file of previous) {
    if (!output.has(file)) await fs.unlink(path.join(root, file)).catch(error => { if (error.code !== 'ENOENT') throw error; });
  }
  await fs.writeFile(manifestPath, JSON.stringify([...output.keys()], null, 2) + '\n');
  await fs.writeFile(homePath, home);
  return { listed: all.length, newStories: published.length };
}
