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