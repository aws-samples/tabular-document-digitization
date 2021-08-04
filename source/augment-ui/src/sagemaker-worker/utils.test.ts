import { CROWD_SRC, crowdFormBuildSubmittableForm } from "./utils";

test("injects crowd-form and inputs", () => {
  const form = crowdFormBuildSubmittableForm({
    colors: JSON.stringify({ blue: true }),
  });

  const result = form.querySelector(
    "input[name='colors']"
  ) as HTMLInputElement | null;
  const val = result ? result.value : "";
  expect(JSON.parse(val)).toEqual({ blue: true });

  // Check that crowd-form element was added.
  expect(document.body.querySelector("crowd-form")).toBeTruthy();

  // Check that script tag was added.
  expect(
    document.head.querySelector(`script[src='${CROWD_SRC}']`)
  ).toBeTruthy();
});
