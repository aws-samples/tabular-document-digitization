#!/usr/bin/env node

const fs = require("fs");
const path = require("path");

// This script needs to resolve module imports with node, so use
// transpiled suffix.
const buildWorkerTemplate = require("./worker-template.js");

const printUsage = () => {
  console.log(
    "Usage: npx build-worker-template <path/to/index.html> <s3_prefix>"
  );
  console.log(
    "Note: <s3_prefix> is optional if S3_PREFIX is defined in your environment variables"
  );
};

const args = process.argv.slice(2);
if (args.length === 0 || args.includes("-h") || args.includes("--help")) {
  printUsage();
  process.exit(1);
}

const buildIndex = args[0];
const outputFilePath = path.join(
  path.dirname(buildIndex),
  "worker-template.liquid.html"
);

const s3Prefix = args.length > 1 ? args[1] : process.env.S3_PREFIX;
// S3Prefix is the s3 path the frontend build is deployed at. It's used for referring
// to assets that ship with the frontend build (items in public/).
if (!s3Prefix) {
  printUsage();
  process.exit(1);
}

const indexHtmlStr = fs.readFileSync(buildIndex, "utf-8");
const liquidIndexHtml = buildWorkerTemplate(indexHtmlStr, s3Prefix);

fs.writeFileSync(outputFilePath, liquidIndexHtml);
console.log(`Wrote ${outputFilePath}`);

module.exports = printUsage;
