from unittest import TestCase

from dictionary_for_text import DictionaryForText

from io import StringIO


class Test(TestCase):

    def setUp(self):
        self.stream = None

    def tearDown(self):
        if self.stream is not None and self.stream.closed is not True:
            self.stream.close()

    def test_get_content(self):
        # stream = open("myfile.txt", "r", encoding="utf-8")
        # stream = io.StringIO("some initial text data")
        text = 'Some text date.'
        self.stream = StringIO(text)
        dic = DictionaryForText(self.stream)
        self.assertEqual(text, dic.text)

    def test_get_content_after_close_stream(self):
        text = 'Some text date.'
        self.stream = StringIO(text)
        dic = DictionaryForText(self.stream)
        self.stream.close()

        self.assertEqual(text, dic.text)

    def test_prepare_simple(self):
        self.stream = StringIO('text date \nand more text')
        dic = DictionaryForText(self.stream)
        self.assertEqual(
            {'text': 2, 'date': 1, 'and': 1, 'more': 1},
            dic.prepare()
        )

    def test_prepare_text_with_punctuation_marks(self):
        self.stream = StringIO(
            'text, date. and? more! text: text; text…; text — text'
        )
        dic = DictionaryForText(self.stream)
        self.assertEqual(
            {'text': 6, 'date': 1, 'and': 1, 'more': 1},
            dic.prepare()
        )

