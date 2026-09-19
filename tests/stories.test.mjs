import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { buildStories, parseStory, dateIsValid, rssFeed, articlePage, updateHomepage, START, END } from '../scripts/story-lib.mjs';
import { importStory, previewStory, publicationFiles, createNumberedPost } from '../scripts/publication-lib.mjs';
import { postIdentity } from '../scripts/post-layout.mjs';

const source = (status = 'published', date = '2026-09-18') => `---\ntitle: 'Trees & streets <today>'\nsummary: 'A map & a question.'\ncategory: Trees\nstatus: ${status}\ndate: '${date}'\nideaId: DC001\n---\nA **small finding** with a [source](https://example.com).\n\n![Map](assets/map.svg)\n`;

test('numbered folders scaffold safely and build directly from the editable story', async t => {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'datacuse-numbered-'));
  t.after(async () => {
    assert.ok(path.resolve(root).startsWith(path.resolve(os.tmpdir()) + path.sep) && path.basename(root).startsWith('datacuse-numbered-'));
    await fs.rm(root, { recursive: true, force: true });
  });
  await fs.mkdir(path.join(root, 'templates'));
  await fs.copyFile(new URL('../templates/story.md', import.meta.url), path.join(root, 'templates/story.md'));
  const folder = await createNumberedPost(root, '2_shortest_street');
  for (const name of ['analysis', 'images', 'story']) assert.ok((await fs.stat(path.join(folder, name))).isDirectory());
  const article = path.join(folder, 'story/index.md');
  const draft = await fs.readFile(article, 'utf8');
  assert.match(draft, /status: draft/);
  assert.match(draft, /slug: "shortest-street"/);
  await assert.rejects(createNumberedPost(root, '2_another_name'), /already exists/);
  assert.equal(await fs.readFile(article, 'utf8'), draft);
  for (const name of ['../escape', '0_zero', '02_leading_zero', 'third_post']) assert.throws(() => postIdentity(name), /Post folders/);
  await fs.writeFile(path.join(root, 'content/existing-stories.json'), '[]');
  await fs.writeFile(path.join(root, 'index.html'), `${START}${END}`);
  assert.equal((await buildStories(root, '2026-09-18')).newStories, 0);
  const published = source().replace('assets/map.svg', '../images/map.svg').replace('category: Trees', 'slug: fixed-address\ncategory: Trees');
  await fs.writeFile(article, published);
  await fs.writeFile(path.join(folder, 'images/map.svg'), '<svg/>');
  await fs.writeFile(path.join(folder, 'images/not-for-publication.png'), 'working artwork');
  await fs.writeFile(path.join(folder, 'analysis/private.csv'), 'working data');
  assert.deepEqual(await buildStories(root, '2026-09-18'), { listed: 1, newStories: 1 });
  assert.match(await fs.readFile(path.join(root, 'stories/fixed-address/index.html'), 'utf8'), /assets\/map.svg/);
  assert.deepEqual((await fs.readdir(path.join(root, 'stories/fixed-address/assets'))), ['map.svg']);
  await assert.rejects(fs.access(path.join(root, 'stories/fixed-address/analysis')));
  await fs.writeFile(article, published.replace('A **small finding**', 'An **updated finding**'));
  await buildStories(root, '2026-09-18');
  assert.match(await fs.readFile(path.join(root, 'stories/fixed-address/index.html'), 'utf8'), /updated finding/);
  await fs.writeFile(article, published.replace('status: published', 'status: draft'));
  await buildStories(root, '2026-09-18');
  await assert.rejects(fs.access(path.join(root, 'stories/fixed-address/index.html')));
  assert.doesNotMatch(await fs.readFile(path.join(root, 'stories/feed.xml'), 'utf8'), /fixed-address/);
});

test('drafts and future posts stay unpublished; invalid metadata fails clearly', () => {
  assert.equal(parseStory(source('draft'), 'oak-street', '2026-09-18'), null);
  assert.equal(parseStory(source('published', '2026-09-19'), 'oak-street', '2026-09-18'), null);
  assert.throws(() => parseStory(source('ready'), 'oak-street'), /status/);
  assert.throws(() => parseStory(source('published', '2026-02-30'), 'oak-street'), /real/);
  assert.throws(() => parseStory(source(), '../escape'), /Invalid story/);
  assert.throws(() => parseStory(source().replace("summary: 'A map & a question.'", ''), 'oak-street'), /summary/);
  assert.equal(dateIsValid('2026-05', true), true);
  assert.equal(dateIsValid('2026-05'), false);
});

test('article HTML includes readable Markdown, source links, canonical and RSS discovery', () => {
  const html = articlePage(parseStory(source(), 'oak-street', '2026-09-18'));
  assert.match(html, /<strong>small finding<\/strong>/);
  assert.match(html, /href="https:\/\/example.com"/);
  assert.match(html, /rel="canonical" href="https:\/\/www.datacuse.com\/stories\/oak-street\/"/);
  assert.match(html, /application\/rss\+xml/);
  assert.match(html, /class="story-image" href="assets\/map.svg"/);
  assert.match(html, /Trees &amp; streets &lt;today&gt;/);
  assert.doesNotMatch(html, /DC001/);
});

test('RSS uses absolute stable links, escapes XML, and preserves unknown days', () => {
  const story = parseStory(source(), 'oak-street', '2026-09-18');
  const feed = rssFeed([story, { ...story, url: '/projects/library/', date: '2026-05' }]);
  assert.match(feed, /<title>Trees &amp; streets &lt;today&gt;<\/title>/);
  assert.match(feed, /<guid isPermaLink="true">https:\/\/www.datacuse.com\/stories\/oak-street\/<\/guid>/);
  assert.equal((feed.match(/<pubDate>/g) || []).length, 1);
  assert.equal(rssFeed([story]), rssFeed([story]));
});

test('homepage changes are restricted to markers and show only the latest three', () => {
  const html = `before${START}old${END}after`;
  const stories = Array.from({ length: 5 }, (_, i) => ({ title: `Story ${i}`, summary: 'Summary', category: 'Notes', date: '2026-09-18', url: `/stories/item-${i}/` }));
  const output = updateHomepage(html, stories);
  assert.ok(output.startsWith(`before${START}`));
  assert.ok(output.endsWith(`${END}after`));
  assert.equal((output.match(/<article>/g) || []).length, 3);
  assert.match(output, /Browse all stories/);
  assert.doesNotMatch(output, /Story 3/);
  assert.throws(() => updateHomepage('no markers', stories), /markers/);
});

test('build excludes drafts and assets, is repeatable, and removes only stale generated files', async t => {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'datacuse-stories-'));
  t.after(async () => {
    const resolved = path.resolve(root);
    const temp = path.resolve(os.tmpdir()) + path.sep;
    assert.ok(resolved.startsWith(temp) && path.basename(resolved).startsWith('datacuse-stories-'));
    await fs.rm(resolved, { recursive: true, force: true });
  });
  await fs.mkdir(path.join(root, 'content/stories/oak-street/assets'), { recursive: true });
  await fs.mkdir(path.join(root, 'content/stories/private/assets'), { recursive: true });
  await fs.mkdir(path.join(root, 'content/stories/future'), { recursive: true });
  await fs.writeFile(path.join(root, 'content/existing-stories.json'), '[]');
  await fs.writeFile(path.join(root, 'index.html'), `unchanged before${START}${END}unchanged after`);
  const sourcePath = path.join(root, 'content/stories/oak-street/index.md');
  await fs.writeFile(sourcePath, source());
  await fs.writeFile(path.join(root, 'content/stories/oak-street/assets/map.svg'), '<svg xmlns="http://www.w3.org/2000/svg"/>');
  await fs.writeFile(path.join(root, 'content/stories/private/index.md'), source('draft'));
  await fs.writeFile(path.join(root, 'content/stories/private/assets/private.txt'), 'private');
  await fs.writeFile(path.join(root, 'content/stories/future/index.md'), source('published', '2026-10-01'));
  assert.deepEqual(await buildStories(root, '2026-09-18'), { listed: 1, newStories: 1 });
  await assert.rejects(fs.access(path.join(root, 'stories/private/index.html')));
  await assert.rejects(fs.access(path.join(root, 'stories/private/assets/private.txt')));
  await assert.rejects(fs.access(path.join(root, 'stories/future/index.html')));
  assert.match(await fs.readFile(path.join(root, 'stories/oak-street/assets/map.svg'), 'utf8'), /svg/);
  const feed = await fs.readFile(path.join(root, 'stories/feed.xml'), 'utf8');
  const home = await fs.readFile(path.join(root, 'index.html'), 'utf8');
  await buildStories(root, '2026-09-18');
  assert.equal(await fs.readFile(path.join(root, 'stories/feed.xml'), 'utf8'), feed);
  assert.equal(await fs.readFile(path.join(root, 'index.html'), 'utf8'), home);
  await fs.writeFile(path.join(root, 'stories/handmade.html'), 'keep me');
  await fs.writeFile(sourcePath, source('draft'));
  assert.deepEqual(await buildStories(root, '2026-09-18'), { listed: 0, newStories: 0 });
  await assert.rejects(fs.access(path.join(root, 'stories/oak-street/index.html')));
  await assert.rejects(fs.access(path.join(root, 'stories/oak-street/assets/map.svg')));
  assert.equal(await fs.readFile(path.join(root, 'stories/handmade.html'), 'utf8'), 'keep me');
});

test('deployment excludes source drafts, templates, tests, and the generation manifest', async () => {
  const workflow = await fs.readFile(new URL('../.github/workflows/pages-projects.yml', import.meta.url), 'utf8');
  for (const directory of ['content', 'templates', 'tests', '_preview']) assert.ok(workflow.includes(`--exclude='/${directory}/'`));
  assert.ok(workflow.includes("--exclude='/stories/.generated.json'"));
  assert.ok(workflow.indexOf('npm run build:stories') < workflow.indexOf('rsync -av'));
});

test('workspace import selects publication files; draft preview never changes publication status or feed', async t => {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'datacuse-import-'));
  t.after(async () => {
    assert.ok(path.resolve(root).startsWith(path.resolve(os.tmpdir()) + path.sep) && path.basename(root).startsWith('datacuse-import-'));
    await fs.rm(root, { recursive: true, force: true });
  });
  const sourceDir = path.join(root, 'workspace/publish');
  const repo = path.join(root, 'repo');
  await fs.mkdir(path.join(sourceDir, 'assets'), { recursive: true });
  await fs.mkdir(path.join(sourceDir, 'analysis'), { recursive: true });
  await fs.mkdir(path.join(repo, 'content'), { recursive: true });
  await fs.mkdir(path.join(repo, 'public'), { recursive: true });
  const draft = source('draft');
  await fs.writeFile(path.join(sourceDir, 'index.md'), draft);
  await fs.writeFile(path.join(sourceDir, 'assets/map.svg'), '<svg/>');
  await fs.writeFile(path.join(sourceDir, 'analysis/private.csv'), 'do not publish');
  await fs.writeFile(path.join(sourceDir, 'working-image.png'), 'do not import');
  await fs.writeFile(path.join(repo, 'content/existing-stories.json'), '[]');
  await fs.writeFile(path.join(repo, 'index.html'), `${START}${END}`);
  for (const css of ['home.css', 'stories.css']) await fs.writeFile(path.join(repo, 'public', css), 'body{}');
  const imported = await importStory(repo, sourceDir, 'oak-street');
  assert.equal(imported.files, 2);
  await assert.rejects(fs.access(path.join(imported.destination, 'analysis/private.csv')));
  await assert.rejects(fs.access(path.join(imported.destination, 'working-image.png')));
  assert.equal(await fs.readFile(path.join(imported.destination, 'index.md'), 'utf8'), draft);
  await buildStories(repo, '2026-09-18');
  const originalFeed = await fs.readFile(path.join(repo, 'stories/feed.xml'), 'utf8');
  const preview = await previewStory(repo, sourceDir, 'oak-street');
  assert.match(await fs.readFile(path.join(preview, 'index.html'), 'utf8'), /noindex, nofollow/);
  assert.match(await fs.readFile(path.join(preview, 'assets/map.svg'), 'utf8'), /svg/);
  assert.equal(await fs.readFile(path.join(sourceDir, 'index.md'), 'utf8'), draft);
  assert.equal(await fs.readFile(path.join(repo, 'stories/feed.xml'), 'utf8'), originalFeed);
  await assert.rejects(fs.access(path.join(repo, 'stories/oak-street/index.html')));
  await fs.unlink(path.join(sourceDir, 'assets/map.svg'));
  await importStory(repo, sourceDir, 'oak-street');
  await assert.rejects(fs.access(path.join(imported.destination, 'assets/map.svg')));
});

test('organized workspace imports only referenced images and rejects missing or escaping paths', async t => {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'datacuse-organized-'));
  t.after(async () => {
    assert.ok(path.resolve(root).startsWith(path.resolve(os.tmpdir()) + path.sep) && path.basename(root).startsWith('datacuse-organized-'));
    await fs.rm(root, { recursive: true, force: true });
  });
  for (const folder of ['content', 'images', 'analysis']) await fs.mkdir(path.join(root, folder));
  const markdown = source('draft').replace('assets/map.svg', '../images/map.svg');
  const article = path.join(root, 'content/index.md');
  await fs.writeFile(article, markdown);
  await fs.writeFile(path.join(root, 'images/map.svg'), '<svg/>');
  await fs.writeFile(path.join(root, 'images/unused.png'), 'not selected');
  await fs.writeFile(path.join(root, 'analysis/private.csv'), 'private');
  const files = await publicationFiles(root);
  assert.deepEqual([...files.keys()], ['index.md', 'assets/map.svg']);
  assert.match(files.get('index.md'), /\]\(assets\/map.svg\)/);
  assert.equal(await fs.readFile(article, 'utf8'), markdown);
  await fs.writeFile(article, markdown.replace('../images/map.svg', '../images/../analysis/private.csv'));
  await assert.rejects(publicationFiles(root), /Invalid public image/);
  await fs.writeFile(article, markdown.replace('../images/map.svg', '../images/missing.png'));
  await assert.rejects(publicationFiles(root), /ENOENT/);
});
