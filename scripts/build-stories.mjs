import { fileURLToPath } from 'node:url';
import { buildStories } from './story-lib.mjs';

try {
  const result = await buildStories(fileURLToPath(new URL('../', import.meta.url)));
  console.log(`Built ${result.newStories} Markdown stories; ${result.listed} stories in the archive and RSS feed.`);
} catch (error) {
  console.error(error.message);
  process.exitCode = 1;
}
