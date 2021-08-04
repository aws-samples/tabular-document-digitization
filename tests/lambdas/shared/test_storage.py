import json
import unittest
import botocore
import io

from unittest      import TestCase
from unittest.mock import patch, Mock

from shared.storage import S3Uri

class TestServices(TestCase):

    def setUp(self):
        pass

    @patch('shared.clients.S3Resource')
    def test_put_s3(self, mock_s3_resource):
        """
        Tests successful s3 put
        """

        s3_bucket_name = 'my-test-bucket-123'
        s3_key         = 'some/key.json'
        s3_uri         = f's3://{s3_bucket_name}/{s3_key}'
        data           = {'MyData': 'MyValue'}

        def mock_put(Body, ContentType):
            """Mock call to S3 API"""
            assert ContentType == 'application/json'
            assert Body == json.dumps(data).encode()

        # Configure S3 mocks
        s3_object_mock = Mock()
        s3_object_mock.bucket_name = s3_bucket_name
        s3_object_mock.key = s3_key
        s3_object_mock.put.side_effect = mock_put
        mock_s3_resource.Object.return_value = s3_object_mock

        # Run s3 put

        S3Uri(Bucket = s3_bucket_name, Object = s3_key).PutJSON(data)

        # Ensure our mock methods were called
        s3_object_mock.put.assert_called_once()
        mock_s3_resource.Object.assert_called_with(s3_bucket_name, s3_key)

    @patch('shared.clients.S3Resource')
    def test_put_s3_failed(self, mock_s3_resource):
        """
        Tests failed s3 put
        """

        s3_bucket_name = 'my-test-bucket-123'
        s3_key         = 'some/key.json'
        s3_uri         = f's3://{s3_bucket_name}/{s3_key}'
        data           = json.dumps({'MyData': 'MyValue'})

        # Configure S3 mocks
        s3_object_mock = Mock()
        s3_object_mock.put.side_effect = botocore.exceptions.ClientError(
            error_response = {'Error': {'Code': 123, 'Message': 'MyError'}},
            operation_name = 'Operation',
        )

        mock_s3_resource.Object.return_value = s3_object_mock

        # Run s3 put
        try:
            S3Uri(Bucket = s3_uri, Object = s3_key).PutJSON(data)
            self.fail('s3 put should have failed')
        except botocore.exceptions.ClientError as e:
            self.assertIn('MyError', str(e))

        # Ensure our mock methods were called
        s3_object_mock.put.assert_called_once()
        mock_s3_resource.Object.assert_called_with(s3_bucket_name, s3_key)

    @patch('shared.clients.S3Resource')
    def test_get_object_from_s3(self, mock_s3_resource):
        """
        Tests successful s3 get
        """
        s3_bucket_name = 'my-test-bucket-123'
        s3_key         = 'some/key.json'
        data           = {'MyData': 'MyValue'}

        def mock_get():
            """Mock call to S3 API"""
            return {'Body': io.BytesIO(json.dumps(data).encode())}

        # Configure S3 mocks
        s3_object_mock                 = Mock()
        s3_object_mock.bucket_name     = s3_bucket_name
        s3_object_mock.key             = s3_key
        s3_object_mock.get.side_effect = mock_get

        mock_s3_resource.Object.return_value = s3_object_mock

        # Run s3 get

        result = S3Uri(Bucket = s3_bucket_name, Object = s3_key).GetJSON()

        assert result == data

        # Ensure our mock methods were called
        s3_object_mock.get.assert_called_once()

    @patch('shared.clients.S3Resource')
    def test_get_object_from_s3_failed(self, mock_s3_resource):
        """
        Tests failed s3 get
        """
        s3_bucket_name = 'my-test-bucket-123'
        s3_key = 'some/key.json'
        s3_url = f's3://{s3_bucket_name}/{s3_key}'

        # Configure S3 mocks
        s3_object_mock = Mock()
        s3_object_mock.get.side_effect = botocore.exceptions.ClientError(
            error_response={'Error': {'Code': 500, 'Message': 'MyInternalError'}},
            operation_name='Operation',
        )
        mock_s3_resource.Object.return_value = s3_object_mock

        # Run s3 get testing internal error
        try:
            S3Uri(Bucket = s3_bucket_name, Object = s3_key).GetJSON()
            self.fail('s3 put should have failed')
        except botocore.exceptions.ClientError as ve:
            self.assertIn('MyInternalError', str(ve))

        # Ensure our mock methods were called
        s3_object_mock.get.assert_called_once()

if  __name__ == '__main__':

    unittest.main()