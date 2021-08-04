import { queryInputs } from "./InputProvider";
import { JSDOM } from "jsdom";

const dummySrc = "https://www.test.com/asset.png";
const dummyLocalSrc = "/my/source.png";

const escapedHitlJson = `{&quot;hello&quot;: &quot;world&quot;}`;
const hitlJson = { hello: "world" };
const escapedLocalJson = `{&quot;myEscaped&quot;: &quot;json&quot;}`;
const localJson = { myEscaped: "json" };

test("queries the dom for input elements", async () => {
  const testCases = [
    {
      description: "asset input",
      input: `<input class="asset" data-name="myAsset" data-src="${dummySrc}">`,
      expectedHitl: {
        myAsset: dummySrc,
      },
      expectedLocal: {
        myAsset: dummySrc,
      },
    },
    {
      description: "s3-file input",
      input: `<input class="s3-file" data-name="myS3File" data-src="${dummySrc}" data-local="${dummyLocalSrc}">`,
      expectedHitl: {
        myS3File: dummySrc,
      },
      expectedLocal: {
        myS3File: dummyLocalSrc,
      },
    },
    {
      description: "literal escaped json",
      input: `<input class="json-var" data-name="myJson" data-src="${escapedHitlJson}" data-local="${escapedLocalJson}">`,
      expectedHitl: {
        myJson: hitlJson,
      },
      expectedLocal: {
        myJson: localJson,
      },
    },
  ];

  for (const tc of testCases) {
    const { document } = new JSDOM(tc.input).window;
    const hitlQuery = await queryInputs(document, true);
    const localQuery = await queryInputs(document, false);

    expect(hitlQuery).toEqual(tc.expectedHitl);
    expect(localQuery).toEqual(tc.expectedLocal);
  }
});
