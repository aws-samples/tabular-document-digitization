export const CROWD_SRC = "https://assets.crowd.aws/crowd-html-elements.js";

interface CrowdFormSerializedFields {
  [fieldName: string]: string;
}

// Exported for testing.
export const crowdFormBuildSubmittableForm = (
  submissionFields: CrowdFormSerializedFields
): HTMLFormElement => {
  // Inject crowd script tag if missing.
  const crowdScript = document.head.querySelector(`script[src='${CROWD_SRC}']`);
  if (!crowdScript) {
    const newScript = document.createElement("script");
    newScript.src = "https://assets.crowd.aws/crowd-html-elements.js";
    newScript.async = false;
    document.head.appendChild(newScript);
  }

  // Inject a crowd-form element if missing.
  if (!document.body.querySelector("crowd-form")) {
    document.body.insertAdjacentHTML(
      "beforeend",
      `
      <crowd-form style="display: none">
        <input
          style="display: block"
          type="submit"
          value="Submit"
        />
      </crowd-form>
    `
    );
  }

  const crowdForm = document.querySelector("crowd-form") as HTMLFormElement;

  // Inject all crowd-form inputs then submit the form.
  for (const [fieldName, fieldValue] of Object.entries(submissionFields)) {
    const fieldId = `crowd-form-${fieldName}`;

    // Check if fieldName already exists in the object.
    let inputElement = document.getElementById(
      fieldId
    ) as HTMLInputElement | null;
    if (!inputElement) {
      inputElement = document.createElement("input") as HTMLInputElement;
      inputElement.type = "hidden";
      inputElement.id = fieldId;
      inputElement.name = fieldName;
    }

    inputElement.value = fieldValue;

    crowdForm.appendChild(inputElement);
  }

  return crowdForm;
};

// Submits a crowd-form on the page, creating one if not provided by the user interface.
export const crowdFormSubmit = async (
  submissionFields: CrowdFormSerializedFields
) => {
  const crowdForm = crowdFormBuildSubmittableForm(submissionFields);
  // Must wait for crowd-form to be defined before submitting.
  await customElements.whenDefined("crowd-form");
  // Make visible for local debugging.
  crowdForm.style.display = "block";
  crowdForm.submit();
};
