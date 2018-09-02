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

    def test_prepare_text_with_punctuation_marks_and_other_symbols(self):
        self.stream = StringIO(
            'text, «date». and? {more}! [text]: "text"; text…; (text) “text” — text 2date'
        )
        dic = DictionaryForText(self.stream)
        self.assertEqual(
            {'text': 7, 'date': 2, 'and': 1, 'more': 1},
            dic.prepare()
        )

    def test_prepare_text_with_punctuation_mark_at_end(self):
        self.stream = StringIO(
            'text, date. and? more! text: text; text…; text — text.'
        )
        dic = DictionaryForText(self.stream)
        self.assertEqual(
            {'text': 6, 'date': 1, 'and': 1, 'more': 1},
            dic.prepare()
        )

    def test_short_checker(self):
        self.assertTrue(DictionaryForText._short_checker(''))
        self.assertTrue(DictionaryForText._short_checker('a'))
        self.assertTrue(DictionaryForText._short_checker('ab'))
        self.assertFalse(DictionaryForText._short_checker('abc'))

    def test_drop_short_words(self):
        keep, drop = DictionaryForText._drop_short_words(
            {'word': 2, 'a': 3, '': 4, 'cat': 5, 'as': 6}
        )
        self.assertEqual({'word': 2, 'cat': 5}, keep)
        self.assertEqual({'a': 3, '': 4, 'as': 6}, drop)

    def test_prepare_text_drop_short_words(self):
        self.stream = StringIO(
            'cat is a word'
        )
        dic = DictionaryForText(self.stream)
        words = dic.prepare()
        self.assertEqual({'cat': 1, 'word': 1}, words)

        self.assertEqual({'is': 1, 'a': 1}, dic.get_drop_short())

    def test_drop_hyphen_and_apostrophe_at_start_or_end_word(self):
        self.stream = StringIO(
            'date some- \'text ’date text'
        )
        dic = DictionaryForText(self.stream)
        words = dic.prepare()
        self.assertEqual({'some': 1, 'text': 2, 'date':2}, words)


