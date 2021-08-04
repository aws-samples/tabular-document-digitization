import { TabularHil, useStoreActions } from "appstore";
import { useEffect } from "react";
import { useInput } from "sagemaker-worker";

export default () => {
  const initializeAnnotations = useStoreActions((s) => s.initializeAnnotations);
  const pdfUrl = useInput("pdfUrl") as string;
  const taskObject = useInput("taskObject") as TabularHil;

  useEffect(() => {
    if (pdfUrl && taskObject) {
      initializeAnnotations({ pdfUrl, taskObject });
    }
  }, [initializeAnnotations, pdfUrl, taskObject]);

  return null;
};
