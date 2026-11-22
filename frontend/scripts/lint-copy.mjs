#!/usr/bin/env node
/**
 * Banned-words lint: fails if parent-facing copy contains a technical term.
 *
 * Scans lib/copy.ts (every string) and the parent screens/components (JSX text and the text
 * attributes aria-label, title, alt, placeholder). Banned words come from lib/bannedWords.ts.
 * Usage: node scripts/lint-copy.mjs [--self-test]
 */
import { readFileSync, readdirSync, statSync } from 'node:fs';
import { join, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = resolve(fileURLToPath(import.meta.url), '..', '..');

export function loadBanned() {
  const src = readFileSync(join(root, 'lib/bannedWords.ts'), 'utf8');
  return [...src.matchAll(/'([^']+)'/g)].map((m) => m[1]);
}

export function findBanned(text, banned) {
  const hits = [];
  for (const word of banned) {
    const re = new RegExp(
      `(^|[^\\w])${word.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}($|[^\\w])`,
      'i'
    );
    if (re.test(text)) hits.push(word);
  }
  return hits;
}

/** Pull out the human-readable strings from a source file. */
export function extractCopy(file, source) {
  const out = [];
  if (file.endsWith('lib/copy.ts')) {
    for (const m of source.matchAll(/'((?:[^'\\]|\\.)*)'/g)) out.push(m[1]);
    return out;
  }
  for (const m of source.matchAll(/>([^<>{}]+)</g))
    if (m[1].trim() && !/[;]|===|&&|\|\|/.test(m[1])) out.push(m[1].trim());
  for (const m of source.matchAll(/\b(?:aria-label|title|alt|placeholder)="([^"]*)"/g))
    out.push(m[1]);
  return out;
}

function walk(dir) {
  return readdirSync(dir).flatMap((name) => {
    const p = join(dir, name);
    return statSync(p).isDirectory() ? walk(p) : [p];
  });
}

/** Parent screens: the new shell, states and every route/component added for them. */
const TARGETS = [
  'lib/copy.ts',
  'components/parent',
  'app/week',
  'app/this-week',
  'app/how-its-going',
  'app/login',
];

export function targetFiles() {
  const files = [];
  for (const t of TARGETS) {
    const p = join(root, t);
    try {
      if (statSync(p).isDirectory()) files.push(...walk(p));
      else files.push(p);
    } catch {
      /* optional target not present */
    }
  }
  return files.filter((f) => /\.(tsx?|ts)$/.test(f));
}

function main() {
  const banned = loadBanned();
  if (process.argv.includes('--self-test')) {
    const bad = findBanned('Your mastery of the API schema', banned);
    if (bad.length < 3) throw new Error('self-test failed');
    if (findBanned('Got it, shaky, or lost it', banned).length)
      throw new Error('self-test false hit');
    console.log('lint-copy self-test ok');
    return;
  }
  const problems = [];
  const files = targetFiles();
  for (const file of files) {
    const source = readFileSync(file, 'utf8');
    for (const text of extractCopy(file, source)) {
      for (const word of findBanned(text, banned))
        problems.push(`${relative(root, file)}: "${word}" in "${text}"`);
    }
  }
  if (problems.length) {
    console.error(`Banned words found:\n${problems.join('\n')}`);
    process.exit(1);
  }
  console.log(`lint-copy: ${files.length} files clean (${banned.length} banned words)`);
}

if (process.argv[1] === fileURLToPath(import.meta.url)) main();
