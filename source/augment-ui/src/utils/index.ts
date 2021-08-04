import { TabularHil } from "appstore";
import { DocumentModel } from "appstore/models";
import { lighten } from "polished";
import { crowdFormSubmit } from "sagemaker-worker";

const Utils = {
  convertTabularHil(documentModel: DocumentModel, reject: boolean, rejectReason: string): TabularHil {
    // Converts from frontend application model to tabular hil data format.
    // This allows the data payload to be re-entrant into A2I.
    return {
      numPages: documentModel.numPages,
      tableTypes: documentModel.tableTypes,
      pages: documentModel.documentPages,
      metadata: { ...documentModel.metadata, rejected: reject, rejectedReason:  rejectReason},
    };
  },

  async submit(documentModel: DocumentModel) {
    await Utils.doSubmit(Utils.convertTabularHil(documentModel, false, ""))
  },

  async submitReject(documentModel: DocumentModel, reason: string) {
    await Utils.doSubmit(Utils.convertTabularHil(documentModel, true, reason))
  },

  async doSubmit(tabularHil: TabularHil) {
    await crowdFormSubmit({
      submission: JSON.stringify(tabularHil),
    });
  },

  getConfidenceScoreHeatmapRange() {
    return [
      {
        color: lighten(0.175, "#f75d64"),
        score: 0.6,
      },
      {
        color: lighten(0.225, "#f75d64"),
        score: 0.7,
      },
      {
        color: lighten(0.25, "#f75d64"),
        score: 0.8,
      },
      {
        color: lighten(0.275, "#f75d64"),
        score: 0.9,
      },
      {
        color: lighten(0.3, "#f75d64"),
        score: 0.95,
      },
      {
        color: "#ffffff",
        score: 0.98,
      },
    ];
  },
};

export default Utils;
