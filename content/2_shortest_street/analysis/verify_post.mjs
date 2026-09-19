import fs from 'node:fs/promises';
import path from 'node:path';
import assert from 'node:assert/strict';
import { fileURLToPath } from 'node:url';
import { publicationFiles } from '../../../scripts/publication-lib.mjs';
import { parseStory, articlePage } from '../../../scripts/story-lib.mjs';

const directory = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const repository = path.resolve(directory, '../..');
const files = await publicationFiles(directory);
const markdown = files.get('index.md');
assert.match(markdown, /status: draft/);
assert.equal(parseStory(markdown, 'syracuse-shortest-street'), null);
// Validate and render in memory as the repository preview does; source stays draft.
const story = parseStory(markdown.replace('status: draft', 'status: published'), 'syracuse-shortest-street', '9999-12-31');
assert.ok(story);
assert.match(story.html, /Fay Road and Lea Lane/);
assert.match(story.html, /assets\/shortest-streets-map-blog.png/);
const expectedImages = [
  'shortest-streets-map-blog.png',
  'shortest-names-letterboard.png',
  'street-suffixes-long-way.png',
  'short-streets-same-ruler.png',
  'oak-street-pieces-and-whole.png',
];
assert.deepEqual([...files.keys()].filter(name => name !== 'index.md').sort(), expectedImages.map(name => `assets/${name}`).sort());
assert.equal((story.html.match(/<img /g) || []).length, expectedImages.length);
const preview = path.join(directory, '_preview');
const output = path.join(preview, 'stories', story.slug);
await fs.mkdir(path.join(output, 'assets'), { recursive: true });
await fs.mkdir(path.join(preview, 'public'), { recursive: true });
await fs.writeFile(path.join(output, 'index.html'), articlePage(story));
for (const [name, bytes] of files) {
  if (name !== 'index.md') await fs.writeFile(path.join(output, name), bytes);
}
for (const name of ['home.css', 'stories.css']) {
  await fs.copyFile(path.join(repository, 'public', name), path.join(preview, 'public', name));
}
const prose = story.body.split('\n---\n')[0].replace(/!\[[\s\S]*?\]\([^)]*\)/g, '').replace(/\*\*/g, '');
console.log(JSON.stringify({ article: 'story/index.md', status: 'draft', bodyWords: prose.trim().split(/\s+/).length, packagedFiles: [...files.keys()], preview: path.join(output, 'index.html') }, null, 2));
