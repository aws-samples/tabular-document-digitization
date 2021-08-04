from unittest      import main, TestCase
from unittest.mock import patch, Mock

from shared.database import Database
from shared.document import Document

class TestCase(TestCase):
    @patch('shared.database.Database.Table.get_item')
    def test_get_document(self, get_item):
        """Fetch a document by id"""

        doc = Document(DocumentID = '123')
        doc.AcquireMap.RetryCount = 5


        get_item.return_value = {
            'Item': doc.to_dict(),
            'ResponseMetadata': {
                'HTTPStatusCode': 200,
            },
        }

        response_doc = Database.GetDocument('123')

        self.assertEqual(doc, response_doc)


if  __name__ == '__main__':

    main()
