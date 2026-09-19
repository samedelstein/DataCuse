import { fileURLToPath } from 'node:url';
import { createNumberedPost } from './publication-lib.mjs';

try {
  if (process.argv.length !== 3) throw new Error('Usage: npm run story:new -- 2_shortest_street');
  const directory = await createNumberedPost(fileURLToPath(new URL('../', import.meta.url)), process.argv[2]);
  console.log(`Created ${directory} with analysis/, images/, and story/index.md.\nKeep status: draft while writing. No import step is needed.`);
} catch (error) {
  console.error(error.message);
  process.exitCode = 1;
}
