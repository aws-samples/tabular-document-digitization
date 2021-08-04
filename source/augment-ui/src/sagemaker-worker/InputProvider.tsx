import React, {
  createContext,
  useContext,
  useLayoutEffect,
  useState,
} from "react";

/*
 * InputProvider
 *
 * Provides all asset URLs, s3 URLs, and taskObject input variables to the frontend
 * by querying for hidden <input> elements in the DOM with attributes that contain
 * the input data.
 *
 * This provider works regardless of if we're in a HITL environment (ie an A2I or
 * GT job) or running the frontend locally for development by parsing local overrides
 * from the data-local attribute.
 */

type InputMap = {
  [key: string]: any;
};

const InputContext = createContext({} as InputMap);

const getAttrOrFail = (el: Element, attr: string): string => {
  const attrVal = el.getAttribute(attr);
  if (!attrVal) {
    throw new Error(`${attr} must be specified on ${el.outerHTML}`);
  }
  return attrVal;
};

export const queryInputs = async (doc: HTMLDocument, isHitl: boolean) => {
  const inputs: InputMap = {};

  Array.from(doc.querySelectorAll("input.asset")).forEach((el) => {
    const name = getAttrOrFail(el, "data-name");
    const src = getAttrOrFail(el, "data-src");
    inputs[name] = src;
  });

  Array.from(doc.querySelectorAll("input.s3-file")).forEach((el) => {
    const name = getAttrOrFail(el, "data-name");
    inputs[name] = isHitl
      ? getAttrOrFail(el, "data-src")
      : getAttrOrFail(el, "data-local");
  });

  for (const el of Array.from(doc.querySelectorAll("input.json-var"))) {
    const name = getAttrOrFail(el, "data-name");
    if (isHitl) {
      const srcAttr = getAttrOrFail(el, "data-src");
      try {
        const parsed = JSON.parse(srcAttr);
        inputs[name] = parsed;
        continue;
      } catch (e) {
        throw new Error(`${srcAttr} can't be parsed as JSON: ${e}`);
      }
    }

    const localAttr = getAttrOrFail(el, "data-local");
    // LocalAttr is either valid literal JSON or a path to a file with valid JSON.
    try {
      const parsed = JSON.parse(localAttr);
      inputs[name] = parsed;
      continue;
    } catch (e) {
      // Do nothing, this field must be a file path.
    }

    // LocalAttr must be a URL to JSON since the previous try failed.
    const res = await fetch(localAttr);
    const parsedJson = await res.json();

    inputs[name] = parsedJson;
  }

  return inputs;
};

const InputProvider: React.FC = (props) => {
  const [inputs, setInputs] = useState({});

  // Wait until the dom has fully loaded before trying to query inputs from the DOM.
  useLayoutEffect(() => {
    const runEffect = async () => {
      const doc = window.document;
      const isHitl = Boolean(process.env.REACT_APP_HITL);
      const queriedInputs = await queryInputs(doc, isHitl);

      setInputs(queriedInputs);
    };
    runEffect();
  }, []);

  return (
    <InputContext.Provider value={inputs}>
      {props.children}
    </InputContext.Provider>
  );
};

export const useInput = (name: string) => {
  return useContext(InputContext)[name];
};

export default InputProvider;
