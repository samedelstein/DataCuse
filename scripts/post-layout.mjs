import { parse } from 'yaml';

export function postIdentity(name, markdown = '') {
  const match = name.match(/^([1-9]\d*)_([a-z0-9]+(?:_[a-z0-9]+)*)$/);
  if (!match || !Number.isSafeInteger(Number(match[1]))) throw new Error('Post folders must use a positive number and lowercase underscore-separated words, such as 2_shortest_street.');
  const front = markdown.replace(/^\uFEFF/, '').match(/^---\r?\n([\s\S]*?)\r?\n---(?:\r?\n|$)/);
  const metadata = front ? parse(front[1]) : {};
  const slug = metadata?.slug ?? match[2].replaceAll('_', '-');
  if (typeof slug !== 'string' || !/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(slug) || ['index', 'feed', 'assets'].includes(slug)) throw new Error(`${name}: invalid URL slug.`);
  return { number: Number(match[1]), slug };
}
