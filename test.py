from unittest import TestCase

from dictionary_for_text import DictionaryForText

from io import StringIO


class Test(TestCase):

    def test_get_content(self):
        # stream = open("myfile.txt", "r", encoding="utf-8")
        # stream = io.StringIO("some initial text data")
        text = 'Some text date.'
        stream = StringIO(text)
        dic = DictionaryForText(stream)
        self.assertEqual(text, dic.text)
        stream.close()

    def test_prepare_simple(self):
        text = 'text date \nand more text'
        stream = StringIO(text)
        dic = DictionaryForText(stream)
        self.assertEqual(
            {'text': 2, 'date': 1, 'and': 1, 'more': 1},
            dic.prepare()
        )
        stream.close()