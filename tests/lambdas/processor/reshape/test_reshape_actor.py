import json
import os
from unittest import TestCase
from unittest.mock import patch, call

from processor.reshape import actor
from shared.defines import FAIL, PASS
from shared.document import Document
from shared.message import ReshapeMapUpdates

PWD = os.path.dirname(__file__)
STATEMENT_1_TEXTRACT_PATH = f"{PWD}/data/0001_NationalBank_2Pages_TextractOutput_1.json"
STATEMENT_2_1_TEXTRACT_PATH = f"{PWD}/data/0002_NationalBank_6Pages_TextractOutput_1.json"
STATEMENT_2_2_TEXTRACT_PATH = f"{PWD}/data/0002_NationalBank_6Pages_TextractOutput_2.json"
STATEMENT_2_3_TEXTRACT_PATH = f"{PWD}/data/0002_NationalBank_6Pages_TextractOutput_3.json"
ERROR_TEXTRACT_PATH = f"{PWD}/data/0000_error.textract.json"
JOB_ID_ONE_PAGE_TWO_TABLES = "job-id-1-page-2-tables"
JOB_ID_SIX_PAGES = "job-id-six-pages"
JOB_ID_SIX_PAGES_NEXT_TOKEN_PART_2 = "next-token-part2"
JOB_ID_SIX_PAGES_NEXT_TOKEN_PART_3 = "next-token-part3"
JOB_ID_ERROR = "job-id-error"


class TestReshape(TestCase):
    def setUp(self):
        five_pages_part1 = json.loads(open(STATEMENT_2_1_TEXTRACT_PATH).read())
        five_pages_part2 = json.loads(open(STATEMENT_2_2_TEXTRACT_PATH).read())
        five_pages_part3 = json.loads(open(STATEMENT_2_3_TEXTRACT_PATH).read())
        self.mock_textract_jobs = {
            JOB_ID_ONE_PAGE_TWO_TABLES: json.loads(
                open(STATEMENT_1_TEXTRACT_PATH).read()
            ),
            JOB_ID_SIX_PAGES: five_pages_part1,
            f"{JOB_ID_SIX_PAGES}{JOB_ID_SIX_PAGES_NEXT_TOKEN_PART_2}": five_pages_part2,
            f"{JOB_ID_SIX_PAGES}{JOB_ID_SIX_PAGES_NEXT_TOKEN_PART_3}": five_pages_part3,
            JOB_ID_ERROR: json.loads(open(ERROR_TEXTRACT_PATH).read()),
        }

        self.textract_output_s3_prefix_uri = "s3://some-bucket-name/some/path"
        self.mock_textract_s3_uris = {
            f"{self.textract_output_s3_prefix_uri}/1": five_pages_part1,
            f"{self.textract_output_s3_prefix_uri}/2": five_pages_part2,
            f"{self.textract_output_s3_prefix_uri}/3": five_pages_part3,
        }

        def mock_get_document_analysis(**kwargs):
            """Mock call to textract API"""
            job_id = kwargs["JobId"]
            next_token = kwargs.get("NextToken", "")
            job_id_and_next_token = f"{job_id}{next_token}"
            return self.mock_textract_jobs[job_id_and_next_token]

        def MockBusPutPass(stage: str, message_body: str):
            message = ReshapeMapUpdates.from_dict(json.loads(message_body))
            self.assertEqual(message.ActorGrade, PASS)

        def MockBusPutFail(stage: str, message_body: str):
            message = ReshapeMapUpdates.from_dict(json.loads(message_body))
            self.assertEqual(message.ActorGrade, FAIL)

        self.MockBusPutPass = MockBusPutPass
        self.MockBusPutFail = MockBusPutFail
        self.mock_get_document_analysis = mock_get_document_analysis

    @patch("processor.reshape.actor.S3Uri")
    @patch("shared.services.textract_client")
    @patch("processor.reshape.actor.Bus")
    def test_two_pages_two_tables(self, MockBus, mock_textract_client, MockS3Uri):
        """
        Tests sending textract output with two pages and two tables per page through reshape
        """
        document_id = "test-reshape-document"
        def mock_put_json_object_s3(data):
            """Mock call to S3 API"""
            # Ensure there are two pages
            assert data["numPages"] == 2
            assert len(data["pages"]) == 2
            # Ensure there are two tables on the page
            assert len(data["pages"][0]["tables"]) == 2
            # Ensure tables each table has a "rows" key
            assert len(data["pages"][0]["tables"][0]["rows"]) > 0
            assert len(data["pages"][0]["tables"][1]["rows"]) > 0

        # Configure S3 & Textract mocks
        MockS3Uri.PutJSON.side_effect = mock_put_json_object_s3
        mock_textract_client.get_document_analysis.side_effect = (
            self.mock_get_document_analysis
        )
        MockBus.PutMessage.side_effect = self.MockBusPutPass

        # Run reshape actor lambda handler
        document = Document()
        document.DocumentID = document_id
        document.ExtractMap.textract_document_analysis_job_id = (
            JOB_ID_ONE_PAGE_TWO_TABLES
        )
        actor.lambda_handler(
            document.to_dict(),
            {},
        )

        # Ensure our mock methods were called
        mock_textract_client.get_document_analysis.assert_called_with(
            JobId=JOB_ID_ONE_PAGE_TWO_TABLES
        )
        MockS3Uri.PutJSON.assert_called_once()
        MockBus.PutMessage.assert_called()

    @patch("processor.reshape.actor.S3Uri")
    @patch("shared.services.textract_client")
    @patch("processor.reshape.actor.Bus")
    def test_six_pages(self, MockBus, mock_textract_client, MockS3Uri):
        """
        Tests sending textract output with six pages through reshape
        """
        document_id = "test-reshape-document"
        def mock_put_json_object_s3(data):
            """Mock call to S3 API"""
            # Ensure there are five pages
            assert data["numPages"] == 6
            assert len(data["pages"]) == 6
            # Ensure there are two tables on the first page
            assert len(data["pages"][0]["tables"]) == 2

        # Configure S3 & Textract mocks
        MockS3Uri.PutJSON.side_effect = mock_put_json_object_s3
        mock_textract_client.get_document_analysis.side_effect = (
            self.mock_get_document_analysis
        )
        MockBus.PutMessage.side_effect = self.MockBusPutPass

        # Run reshape actor lambda handler
        document = Document()
        document.DocumentID = document_id
        document.ExtractMap.textract_document_analysis_job_id = JOB_ID_SIX_PAGES
        actor.lambda_handler(
            document.to_dict(),
            {},
        )

        # Ensure our mock methods were called
        mock_textract_client.get_document_analysis.assert_has_calls(
            [
                call(JobId=JOB_ID_SIX_PAGES),
                call(
                    JobId=JOB_ID_SIX_PAGES,
                    NextToken=JOB_ID_SIX_PAGES_NEXT_TOKEN_PART_2,
                ),
                call(
                    JobId=JOB_ID_SIX_PAGES,
                    NextToken=JOB_ID_SIX_PAGES_NEXT_TOKEN_PART_3,
                ),
            ]
        )
        MockS3Uri.PutJSON.assert_called_once()
        MockBus.PutMessage.assert_called()

    @patch("processor.reshape.actor.S3Uri")
    @patch("shared.services.textract_client")
    @patch("processor.reshape.actor.Bus")
    def test_convert_to_hil_from_s3(self, MockBus, mock_textract_client, MockS3Uri):
        five_pages_part3 = json.loads(open(STATEMENT_1_TEXTRACT_PATH).read())
        print(f"len of five_page_part3: {len(five_pages_part3)}")
        from processor.reshape.actor import convert_textract_json_to_hil
        hil = convert_textract_json_to_hil(five_pages_part3)
        assert hil['numPages'] == 2
        assert len(hil['pages']) == 2
        assert hil['pages'][0]['tables'][0]['rows'][0][0]['text'] == "Ending "

    @patch("processor.reshape.actor.S3Uri")
    @patch("shared.services.textract_client")
    @patch("processor.reshape.actor.Bus")
    def test_six_pages_from_s3(self, MockBus, mock_textract_client, MockS3Uri):
        """
        Tests sending textract output with six pages through reshape
        """
        document_id = "test-reshape-document"
        def mock_get_json_object_s3(s3_uri):
            return self.mock_textract_s3_uris[s3_uri]

        def mock_put_json_object_s3(data):
            """Mock call to S3 API"""
            # Ensure there are six pages
            assert data["numPages"] == 6
            assert len(data["pages"]) == 6
            # Ensure there are two tables on the first page
            assert len(data["pages"][0]["tables"]) == 2

        # Configure S3 & Textract mocks
        s3_uris = list(self.mock_textract_s3_uris.keys())
        s3_uris.sort(key=lambda item: int(os.path.basename(item)))
        s3_keys = [s3_helper.split_uri(s3_uri)[1] for s3_uri in s3_uris]

        # Mock s3_helper actions EXCEPT split_uri
        mock_s3_helper.split_uri.side_effect = s3_helper.split_uri
        mock_s3_helper.List.return_value = s3_keys
        mock_s3_helper.GetJSON.side_effect = mock_get_json_object_s3
        mock_s3_helper.PutJSON.side_effect = mock_put_json_object_s3
        MockBus.PutMessage.side_effect = self.MockBusPutPass

        # Run reshape actor lambda handler
        document = Document()
        document.DocumentID = document_id
        document.ExtractMap.textract_document_analysis_job_id = JOB_ID_SIX_PAGES
        document.ExtractMap.textract_output_s3_prefix_uri = (
            self.textract_output_s3_prefix_uri
        )
        actor.lambda_handler(
            document.to_dict(),
            {},
        )

        # Ensure our mock methods were called
        mock_s3_helper.get_json_object_s3.assert_has_calls(
            [call(s3_uri=s3_uri) for s3_uri in s3_uris]
        )
        mock_s3_helper.put_json_object_s3.assert_called_once()
        MockBus.PutMessage.assert_called()

    @patch("processor.reshape.actor.S3Uri")
    @patch("shared.services.textract_client")
    @patch("processor.reshape.actor.Bus")
    def test_error(self, MockBus, mock_textract_client, MockS3Uri):
        """
        Tests retrieving an error document
        """
        # Configure mocks
        mock_textract_client.get_document_analysis.side_effect = (
            self.mock_get_document_analysis
        )
        MockBus.PutMessage.side_effect = self.MockBusPutFail

        # Run reshape actor lambda handler
        document = Document()
        document.DocumentID = "test-reshape-document"
        document.ExtractMap.textract_document_analysis_job_id = JOB_ID_ERROR
        actor.lambda_handler(
            document.to_dict(),
            {},
        )
        # Ensure our mock methods were called
        mock_textract_client.get_document_analysis.assert_called_with(
            JobId=JOB_ID_ERROR
        )
        MockS3Uri.PutJSON.assert_not_called()
        MockBus.PutMessage.assert_called()

    