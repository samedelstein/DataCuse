import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { importStory } from './publication-lib.mjs';

try {
  if (process.argv.length !== 4) throw new Error('Usage: npm run story:import -- "path/to/story-folder" story-slug');
  const result = await importStory(fileURLToPath(new URL('../', import.meta.url)), path.resolve(process.argv[2]), process.argv[3]);
  console.log(`Imported ${result.files} publication files to ${result.destination}.\nRun npm run build:stories. Draft status is preserved; this command does not deploy.`);
} catch (error) {
  console.error(error.message);
  process.exitCode = 1;
}
