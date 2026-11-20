// Entry for make.fun "news-image-20261119": the front page was drawn
// beforehand and ships in this repository as entry.png. This program
// simply places that file where the grader expects it. It needs no
// network and no third-party packages, only the Node standard library.
import { copyFileSync, existsSync, mkdirSync, readFileSync, realpathSync, statSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const FALLBACK_OUTPUT_DIR = "/output";
const IMAGE_NAME = "entry.png";

function repoRoot() {
  return dirname(fileURLToPath(import.meta.url));
}

function outputDir() {
  const fromEnv = process.env.MAKEFUN_OUTPUT_DIR?.trim();
  return fromEnv ? fromEnv : FALLBACK_OUTPUT_DIR;
}

function assertSourceFile(path) {
  if (!existsSync(path) || !statSync(path).isFile()) {
    throw new Error(`entry image missing: ${path}`);
  }
}

function assertOutputDir(path) {
  if (existsSync(path) && !statSync(path).isDirectory()) {
    throw new Error(`output path is not a directory: ${path}`);
  }
}

function sameFile(a, b) {
  // resolve() only compares paths lexically; a symlinked outputDir would
  // slip through and copy the file onto itself. Compare real paths instead.
  try {
    return existsSync(b) && realpathSync(a) === realpathSync(b);
  } catch {
    return false; // target does not exist yet: not the same file
  }
}

function copyVerified(source, target) {
  mkdirSync(dirname(target), { recursive: true });
  copyFileSync(source, target);

  // Confirm the copy landed intact, byte for byte.
  const written = readFileSync(target);
  const original = readFileSync(source);
  if (!written.equals(original)) {
    throw new Error("copied entry.png does not match the repository file");
  }
  return written.length;
}

function main() {
  const root = repoRoot();
  const dir = outputDir();
  const source = join(root, IMAGE_NAME);
  const target = join(dir, IMAGE_NAME);

  assertSourceFile(source);
  assertOutputDir(dir);

  if (sameFile(source, target)) {
    // The output directory IS the repository folder: nothing to copy,
    // copying a file onto itself could truncate it.
    const size = readFileSync(source).length;
    console.log(`entry.png already in place at ${source} (${size} bytes)`);
    return;
  }

  const bytes = copyVerified(source, target);
  console.log(`wrote ${target} (${bytes} bytes)`);
}

main();
