import json
import os
from unittest import TestCase
from unittest.mock import patch

import botocore

from processor.operate import actor
from shared.defines import FAIL, PASS
from shared.document import Document
from shared.message import OperateMapUpdates

PWD = os.path.dirname(__file__)
STATEMENT_1_HIL_PATH = f"{PWD}/data/0001_bank_statement.hil.json"
STATEMENT_6_HIL_PATH = f"{PWD}/data/0006_combined.hil.json"


class TestOperate(TestCase):
    def setUp(self):
        self.document_1_one_page = json.loads(open(STATEMENT_1_HIL_PATH).read())
        self.document_6_five_pages = json.loads(open(STATEMENT_6_HIL_PATH).read())

        def mock_get_document_analysis(**kwargs):
            """Mock call to textract API"""
            job_id = kwargs["JobId"]
            next_token = kwargs.get("NextToken", "")
            job_id_and_next_token = f"{job_id}{next_token}"
            return self.mock_textract_jobs[job_id_and_next_token]

        self.mock_get_document_analysis = mock_get_document_analysis

    @patch("processor.operate.actor.s3_helper")
    @patch("processor.operate.actor.Bus")
    def test_operates_on_document(self, MockBus, mock_s3_helper):
        """
        Tests that operate properly adds column headers to a given document
        """

        def mock_get_json_object_s3(s3_uri):
            return self.document_1_one_page

        def mock_put_json_object_s3(s3_uri, data):
            """Mock call to S3 API"""
            # Ensure column types were added
            self.assertTrue(len(data["tableTypes"]) > 0)
            for page in data["pages"]:
                for table in page["tables"]:
                    self.assertTrue( "tableType" in table)
                    self.assertTrue( "headerColumnTypes" in table)

        def MockPutMessage(stage: str, message_body: str):
            message = OperateMapUpdates.from_dict(json.loads(message_body))
            self.assertEqual(message.ActorGrade, PASS)

        # Mock s3_helper actions & bus
        mock_s3_helper.get_json_object_s3.side_effect = mock_get_json_object_s3
        mock_s3_helper.put_json_object_s3.side_effect = mock_put_json_object_s3
        MockBus.PutMessage.side_effect = MockPutMessage

        # Run reshape actor lambda handler
        document = Document()
        document.DocumentID = "test-operate-document"
        document.ReshapeMap.hil_output_s3_uri = "s3://some-bucket/some-path"
        document.OperateMap.hil_final_output_s3_uri = (
            "s3://some-bucket/some-output-path.hil-final.json"
        )
        actor.lambda_handler(
            document.to_dict(),
            {},
        )

        # Ensure our mock methods were called
        MockBus.PutMessage.assert_called_once()
        mock_s3_helper.get_json_object_s3.assert_called_once()
        mock_s3_helper.put_json_object_s3.assert_called_once()

    @patch("processor.operate.actor.s3_helper")
    @patch("processor.operate.actor.Bus")
    def test_fails_when_s3_get_fails(self, MockBus, mock_s3_helper):
        """
        Tests that operate sets status to failed when it encounters an error
        """
        document_id = "test-operate-document"
        def MockPutMessage(stage: str, message_body: str):
            message = OperateMapUpdates.from_dict(json.loads(message_body))
            self.assertEqual(message.ActorGrade, FAIL)

        # Mock s3_helper actions & bus
        mock_s3_helper.get_json_object_s3.side_effect = botocore.exceptions.ClientError(
            error_response={"Error": {"Code": 500, "Message": "MyInternalError"}},
            operation_name="Operation",
        )
        MockBus.PutMessage.side_effect = MockPutMessage

        # Run reshape actor lambda handler
        document = Document()
        document.DocumentID = document_id
        document.ReshapeMap.hil_output_s3_uri = "s3://some-bucket/some/path/file.json"
        actor.lambda_handler(
            document.to_dict(),
            {},
        )

        # Ensure our mock methods were/were not called
        MockBus.PutMessage.assert_called_once()
        mock_s3_helper.get_json_object_s3.assert_called_once()
        mock_s3_helper.put_json_object_s3.assert_not_called()
