import json
import os
from unittest import TestCase
from unittest.mock import patch

import botocore

from processor.augment import actor
from shared.defines import FAIL, PASS
from shared.document import Document
from shared.environ import ENV_A2I_FLOW_DEFINITION_ARN
from shared.message import AugmentMapUpdates

PWD = os.path.dirname(__file__)
SAMPLE_FINAL_HIL_OUTPUT_PATH = f"{PWD}/data/sample_final_hil_output.json"

class TestAugmentActor(TestCase):
    def setUp(self):
        self.sample_final_hil_output = json.loads(open(SAMPLE_FINAL_HIL_OUTPUT_PATH).read())
        
        def MockBusPutPass(stage: str, message_body: str):
            message = AugmentMapUpdates.from_dict(json.loads(message_body))
            self.assertEqual(message.ActorGrade, PASS)

        def MockBusPutFail(stage: str, message_body: str):
            message = AugmentActorOutpuAugmentMapUpdatestMessage.from_dict(json.loads(message_body))
            self.assertEqual(message.ActorGrade, FAIL)

        self.MockBusPutPass = MockBusPutPass
        self.MockBusPutFail = MockBusPutFail

    @patch.dict(os.environ, {ENV_A2I_FLOW_DEFINITION_ARN: "MY_FLOW_DEFINITION"}, clear=True)
    @patch("processor.augment.actor.s3_helper")
    @patch("processor.augment.actor.a2i")
    @patch("processor.augment.actor.Bus")
    def test_augment_starts_human_loop(self, MockBus, mock_a2i, mock_s3_helper):
        """
        Tests sending textract output with one page and two tables through the actor
        """
        document_id = "test-augment-document"

        def mock_start_human_loop(**kwargs):
            # Ensure our sample hil file was passed to start_human_loop
            self.assertEqual(
                kwargs['HumanLoopInput']['InputContent'],
                json.dumps(self.sample_final_hil_output)
            )
            # Ensure the flow definition arn was pulled from the environment
            self.assertEqual(
                kwargs['FlowDefinitionArn'],
                'MY_FLOW_DEFINITION'
            )
            return {
                "HumanLoopArn" : "my-human-loop-arn-123"
            }

        def mock_get_json_object_s3(s3_uri):
            """Mock call to S3 API"""
            return self.sample_final_hil_output

        # Configure S3 & Textract mocks
        mock_s3_helper.get_json_object_s3.side_effect = mock_get_json_object_s3
        mock_a2i.start_human_loop.side_effect = mock_start_human_loop
        
        MockBus.PutMessage.side_effect = self.MockBusPutPass

        # Run actor lambda handler
        document = Document()
        document.DocumentID = document_id
        document.OperateMap.hil_final_output_s3_uri = 's3://some-bucket/path/to/file.json'
        actor.lambda_handler(
            document.to_dict(),
            {},
        )

        # Ensure our mock methods were called
        mock_s3_helper.get_json_object_s3.assert_called_once()
        mock_a2i.start_human_loop.assert_called_once()
        MockBus.PutMessage.assert_called_once()

    @patch.dict(os.environ, {ENV_A2I_FLOW_DEFINITION_ARN: "MY_FLOW_DEFINITION"}, clear=True)
    @patch("processor.augment.actor.s3_helper")
    @patch("processor.augment.actor.a2i")
    @patch("processor.augment.actor.Bus")
    def test_error(self, MockBus, mock_a2i, mock_s3_helper):
        """
        Tests retrieving an error document
        """
        def mock_get_json_object_s3(s3_uri):
            """Mock call to S3 API"""
            return self.sample_final_hil_output
        
        # Configure mocks
        mock_s3_helper.get_json_object_s3.side_effect = mock_get_json_object_s3
        mock_a2i.start_human_loop.side_effect = botocore.exceptions.ClientError(
            error_response={"Error": {"Code": 123, "Message": "MyError"}},
            operation_name="Operation",
        )
        MockBus.PutMessage.side_effect = self.MockBusPutFail

        # Run actor lambda handler
        document = Document()
        document.DocumentID = "test-document"
        document.OperateMap.hil_final_output_s3_uri = 's3://some-bucket/path/to/file.json'
        actor.lambda_handler(
            document.to_dict(),
            {},
        )
        # Ensure our mock methods were called
        mock_a2i.start_human_loop.assert_called_once()
        mock_s3_helper.get_json_object_s3.assert_called_once()
        MockBus.PutMessage.assert_called()
