import path from 'node:path';
import fs from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { previewStory } from './publication-lib.mjs';
import { postIdentity } from './post-layout.mjs';

try {
  const root = fileURLToPath(new URL('../', import.meta.url));
  let source, slug;
  if (process.argv.length === 3) {
    postIdentity(process.argv[2]);
    source = path.join(root, 'content', process.argv[2]);
    slug = postIdentity(process.argv[2], await fs.readFile(path.join(source, 'story/index.md'), 'utf8')).slug;
  } else if (process.argv.length === 4) {
    source = path.resolve(process.argv[2]);
    slug = process.argv[3];
  } else throw new Error('Usage: npm run story:preview -- 1_oak_street_trees');
  await previewStory(root, source, slug);
  console.log(`Local preview created. Serve it with:\npython -m http.server 8000 --bind 127.0.0.1 --directory _preview\nThen open http://127.0.0.1:8000/stories/${slug}/\nDraft status and the public archive/feed are unchanged.`);
} catch (error) {
  console.error(error.message);
  process.exitCode = 1;
}
