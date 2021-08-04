import { JSDOM } from "jsdom";

import buildWorkerTemplate from "./worker-template";

const testS3Prefix = "s3://frontend/deploy";

const genHtml = (input: string) =>
  `<html lang="en"><head></head><body>${input}</body></html>`;

test("converts to liquid", () => {
  const testCases = [
    {
      description: "skeleton passes through untouched",
      input: `<p>hello world</p>`,
      expected: `<p>hello world</p>`,
    },
    {
      description: "javascript with href gets liquid tag",
      input: `<link href="/mypath">`,
      expected: `<link href="{{ "${testS3Prefix}/mypath" | grant_read_access }}">`,
    },
    {
      description: "input with asset class gets liquid tag",
      input: `<input class="asset" data-name="myName" data-src="/myPath">`,
      expected: `<input class="asset" data-name="myName" data-src="{{ "${testS3Prefix}/myPath" | grant_read_access }}">`,
    },
    {
      description:
        "input with s3-file class and literal s3 file gets literal liquid tag",
      input: `<input class="s3-file" data-name="myName" data-src="s3://hello/world">`,
      expected: `<input class="s3-file" data-name="myName" data-src="{{ "s3://hello/world" | grant_read_access }}">`,
    },
    {
      description:
        "input with s3-file class and variable input gets variable liquid tag",
      input: `<input class="s3-file" data-name="myName" data-src="task.input.taskObject">`,
      expected: `<input class="s3-file" data-name="myName" data-src="{{ task.input.taskObject | grant_read_access }}">`,
    },
    {
      description: "data-local is stripped in worker template for s3-file",
      input: `<input class="s3-file" data-name="myName" data-src="task.input.taskObject" data-local="test">`,
      expected: `<input class="s3-file" data-name="myName" data-src="{{ task.input.taskObject | grant_read_access }}">`,
    },
    {
      description: "input with json-var class and variable liquid tag",
      input: `<input class="json-var" data-name="myName" data-src="task.input.taskObject">`,
      expected: `<input class="json-var" data-name="myName" data-src="{{ task.input.taskObject | to_json | escape }}">`,
    },
    {
      description: "data-local is stripped in worker template for s3-file",
      input: `<input class="json-var" data-name="myName" data-src="task.input.taskObject" data-local="test">`,
      expected: `<input class="json-var" data-name="myName" data-src="{{ task.input.taskObject | to_json | escape }}">`,
    },
  ];

  testCases.forEach((tc) => {
    const inputHtml = genHtml(tc.input);
    const expectedHtml = genHtml(tc.expected);
    const output = buildWorkerTemplate(inputHtml, testS3Prefix);
    expect(output).toEqual(expectedHtml);
  });
});
