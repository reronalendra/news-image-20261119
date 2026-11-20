// Entry for make.fun "news-image-20261119": the front page was drawn
// beforehand and ships in this repository as entry.png. This program
// simply places that file where the grader expects it. It needs no
// network and no third-party packages, only the Node standard library.
import { copyFileSync, existsSync, mkdirSync, readFileSync, realpathSync, statSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const repoRoot = dirname(fileURLToPath(import.meta.url));
// An empty or whitespace-only variable must fall back, not mkdir("").
const outputDir = process.env.MAKEFUN_OUTPUT_DIR?.trim() || "/output";
const source = join(repoRoot, "entry.png");
const target = join(outputDir, "entry.png");

if (!existsSync(source) || !statSync(source).isFile()) {
  throw new Error(`entry image missing: ${source}`);
}
if (existsSync(outputDir) && !statSync(outputDir).isDirectory()) {
  throw new Error(`output path is not a directory: ${outputDir}`);
}

// resolve() only compares paths lexically; a symlinked outputDir would
// slip through and copy the file onto itself. Compare real paths instead.
let sameFile = false;
if (existsSync(outputDir)) {
  try {
    sameFile = realpathSync(target) === realpathSync(source);
  } catch {
    sameFile = false; // target does not exist yet: not the same file
  }
}
if (sameFile) {
  // The output directory IS the repository folder: nothing to copy,
  // copying a file onto itself could truncate it.
  console.log(`entry.png already in place at ${source} (${readFileSync(source).length} bytes)`);
} else {
  mkdirSync(outputDir, { recursive: true });
  copyFileSync(source, target);

  // Confirm the copy landed intact, byte for byte.
  const written = readFileSync(target);
  const original = readFileSync(source);
  if (!written.equals(original)) {
    throw new Error("copied entry.png does not match the repository file");
  }
  console.log(`wrote ${target} (${written.length} bytes)`);
}
