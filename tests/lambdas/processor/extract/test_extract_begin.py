import os
import unittest
from unittest import TestCase
from unittest.mock import patch

from shared.document import Document
from shared.defines import Stage, State

from processor.extract.begin import ExtractBeginProcessor
from shared.clients import TextractClient


@patch("shared.clients.TextractClient.start_document_analysis")
@patch("shared.database.Database.PutDocument")
@patch("shared.database.Database.GetDocuments")
class TestProcessDocuments(TestCase):
    """Tests that we can catch transient errors in our try begin textract job function"""

    def setUp(self):
        os.environ["SROLE_TEXTRACT_ARN"] = "arn:textract"
        os.environ["TOPIC_TEXTRACT_ARN"] = "arn:topic"
        self.extract_begin_process = ExtractBeginProcessor(
            stage=Stage.EXTRACT, actor=None, retryLimit=5
        )

        self.doc = Document.from_dict(
            {
                "DocumentID": "123",
                "Stage": "EXTRACT",
                "AcquireMap": {
                    "StageS3Uri": {"Bucket": "foo", "Object": "bar"},
                    "Exceptions": [{"something": "wrong"}],
                    "InputS3Url": "s3://...",
                },
            }
        )

    def test_successful_submit(self, get_docs_mock, put_doc_mock, start_mock):
        """Test a successful textract job creation."""
        get_docs_mock.return_value = [self.doc]
        start_mock.return_value = {
            "JobId": "id",
        }

        self.extract_begin_process.processDocuments()

        start_mock.assert_called_once()
        put_doc_mock.assert_called_once()

        doc = put_doc_mock.call_args[0][0]
        self.assertEqual(doc.State, State.RUNNING)

    def test_transient_error(self, get_docs_mock, put_doc_mock, start_mock):
        """Test a transient error textract job creation."""
        get_docs_mock.return_value = [self.doc]

        def raise_err(*args, **kwargs):
            raise TextractClient.exceptions.LimitExceededException(
                operation_name="name", error_response={}
            )

        start_mock.side_effect = raise_err

        self.extract_begin_process.processDocuments()

        start_mock.assert_called_once()
        put_doc_mock.assert_called_once()

        doc = put_doc_mock.call_args[0][0]
        self.assertEqual(doc.State, State.HOLDING)


if __name__ == "__main__":
    unittest.main()
