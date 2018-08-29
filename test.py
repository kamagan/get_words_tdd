from unittest import TestCase

import getwords

from io import StringIO


class Test(TestCase):

    def test_get_content(self):
        # stream = open("myfile.txt", "r", encoding="utf-8")
        # stream = io.StringIO("some initial text data")
        text = 'Some text date.'
        stream = StringIO(text)
        self.assertEqual(text, getwords.get_content(stream))
        stream.close()

    def test_prepare_simple(self):
        text = 'text date \nand more text'
        stream = StringIO(text)
        self.assertEqual(
            {'text': 2, 'date': 1, 'and': 1, 'more': 1},
            getwords.prepare(stream)
        )
        stream.close()