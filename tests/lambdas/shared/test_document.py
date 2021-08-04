import unittest
from pprint import pprint
from shared.defines import Stage, State
from shared.document import Document, AcquireMap

class TestCase(unittest.TestCase):
    def test_create(self):
        """Verify we can create a document without an exception"""
        doc = Document(DocumentID="123")

    def test_retry_value(self):
        """Verify retry exists in a sub map and has appropriate default after creation"""
        doc = Document(DocumentID="123")
        pprint(doc)
        self.assertEqual(doc.AcquireMap.RetryCount, 0)

    def test_current_map_access(self):
        """Check that we can access member maps through CurrentMap"""
        doc = Document(DocumentID="123")

        doc.AcquireMap.RetryCount = 456
        doc.Stage = Stage.ACQUIRE
        pprint(doc)

        self.assertEqual(doc.CurrentMap.RetryCount, 456)

    def test_dict_generation(self):
        """Check that we can convert to dictionary"""
        doc = Document(DocumentID="123", AcquireMap=AcquireMap(RetryCount=5))
        dict_doc = doc.to_dict()

        self.assertEqual(dict_doc["AcquireMap"]["RetryCount"], 5)


    def test_nested_dict_handling(self):
        """
        Check that we can serialize and deserialize without losing info

        If this has failed and you've added a new stage, please update the serialization
        to add the new class name.
        """

        doc = Document(DocumentID="123", AcquireMap=AcquireMap(RetryCount=5))

        jsonResult = doc.to_json()

        parsedDoc = Document.from_json(jsonResult)

        self.maxDiff = None
        self.assertEqual(doc, parsedDoc)


if __name__ == '__main__':
    unittest.main()
