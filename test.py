
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
        self.stream = StringIO('''
            text, «date». and? {more}! [text]: "text"; text…; (text)
            “text” — text 2date
        ''')
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

    def test_prepare_drop_hyphen_and_apostrophe_at_start_or_end_word(self):
        self.stream = StringIO(
            'date some- \'text ’date text'
        )
        dic = DictionaryForText(self.stream)
        words = dic.prepare()
        self.assertEqual({'some': 1, 'text': 2, 'date': 2}, words)

    def test_proper_name_checker(self):
        self.assertTrue(DictionaryForText._proper_name_checker('Murzik'))
        self.assertFalse(DictionaryForText._proper_name_checker('RDX'))
        self.assertFalse(DictionaryForText._proper_name_checker('ClickEvent'))
        self.assertFalse(DictionaryForText._proper_name_checker('clickEvent'))
        self.assertFalse(DictionaryForText._proper_name_checker('mouse'))

    def test_drop_proper_name(self):
        keep, drop = DictionaryForText._drop_proper_name(
            {'Two': 1, 'two': 2, 'cat': 3, 'Venik': 1}
        )
        self.assertEqual({'two': 3, 'cat': 3}, keep)
        self.assertEqual({'Venik': 1}, drop)

    def test_prepare_drop_proper_name(self):
        self.stream = StringIO('Two cats are two tails, Murzik and Venik.')
        dic = DictionaryForText(self.stream)
        words = dic.prepare()
        self.assertEqual(
            {'two': 2, 'cats': 1, 'are': 1, 'tails': 1, 'and': 1},
            words
        )
        self.assertEqual({'Murzik': 1, 'Venik': 1}, dic.get_drop_proper_name())

    def test_end_s_checker(self):
        self.assertTrue(DictionaryForText._end_s_checker('items'))
        self.assertTrue(DictionaryForText._end_s_checker('drives'))
        self.assertFalse(DictionaryForText._end_s_checker('item'))
        self.assertFalse(DictionaryForText._end_s_checker('class'))

    def test_drop_end_s(self):
        end_key = 'end_s'
        keep, drop = DictionaryForText._drop_ends(
            {'items': 2, 'item': 3, 'class': 4, 'drive': 5, 'drives': 6},
            end_key
        )
        self.assertEqual({'item': 5, 'class': 4, 'drive': 11}, keep)
        self.assertEqual({'items': 'item', 'drives': 'drive'}, drop[end_key])

    def test_prepare_drop_end_s(self):
        self.stream = StringIO('two cats are cat and cat')
        dic = DictionaryForText(self.stream)
        words = dic.prepare()
        self.assertEqual(
            {'two': 1, 'cat': 3, 'are': 1, 'and': 1},
            words
        )
        self.assertEqual({'cats': 'cat'}, dic.get_drop_end_s())

    def test_end_apostrophe_s_checker(self):
        self.assertTrue(DictionaryForText._end_apostrophe_s_checker('item\'s'))
        self.assertTrue(DictionaryForText._end_apostrophe_s_checker('item’s'))
        self.assertFalse(DictionaryForText._end_apostrophe_s_checker('items'))

    def test_drop_end_apostrophe_s(self):
        end_key = 'end_apostrophe_s'
        keep, drop = DictionaryForText._drop_ends(
            {'item\'s': 2, 'item': 3, 'class': 4, 'item’s': 5}, end_key
        )
        self.assertEqual({'item': 10, 'class': 4}, keep)
        self.assertEqual({'item\'s': 'item', 'item’s': 'item'}, drop[end_key])

    def test_prepare_drop_end_apostrophe_s(self):
        self.stream = StringIO('that cat and this cat are cat\'s cats')
        dic = DictionaryForText(self.stream)
        words = dic.prepare()
        self.assertEqual(
            {'that': 1, 'cat': 4, 'and': 1, 'this': 1, 'are': 1},
            words
        )
        self.assertEqual({'cat\'s': 'cat'}, dic.get_drop_end_apostrophe_s())

    def test_end_ies_checker(self):
        self.assertTrue(DictionaryForText._end_ies_checker('entities'))
        self.assertFalse(DictionaryForText._end_ies_checker('items'))

    def test_drop_end_ies(self):
        end_key = 'end_ies'
        keep, drop = DictionaryForText._drop_ends(
            {'entity': 2, 'entities': 3, 'class': 4}, end_key
        )
        self.assertEqual({'entity': 5, 'class': 4}, keep)
        self.assertEqual({'entities': 'entity'}, drop[end_key])

    def test_prepare_drop_end_ies(self):
        self.stream = StringIO(
            'those goodies are one goody for you and one one for you'
        )
        dic = DictionaryForText(self.stream)
        words = dic.prepare()
        self.assertEqual(
            {
                'those': 1, 'are': 1, 'one': 3, 'goody': 2, 'for': 2,
                'you': 2, 'and': 1
            },
            words
        )
        self.assertEqual({'goodies': 'goody'}, dic.get_drop_end_ies())

    def test_end_es_checker(self):
        self.assertTrue(DictionaryForText._end_es_checker('classes'))
        self.assertTrue(DictionaryForText._end_es_checker('does'))
        self.assertFalse(DictionaryForText._end_es_checker('items'))

    def test_drop_end_es(self):
        end_key = 'end_es'
        keep, drop = DictionaryForText._drop_ends(
            {'drive': 2, 'drives': 3, 'class': 4, 'classes': 5}, end_key
        )
        self.assertEqual({'drive': 2, 'drives': 3, 'class': 9}, keep)
        self.assertEqual({'classes': 'class'}, drop[end_key])

    def test_prepare_drop_end_es(self):
        self.stream = StringIO(
            'classes are object of class class'
        )
        dic = DictionaryForText(self.stream)
        words = dic.prepare()
        self.assertEqual(
            {'are': 1, 'object': 1, 'class': 3},
            words
        )
        self.assertEqual({'classes': 'class'}, dic.get_drop_end_es())

    def test_camel_case(self):
        checker = DictionaryForText._camel_case_checker

        self.assertTrue(checker('BreakEvent'))
        self.assertTrue(checker('BlockBreakMessage'))
        self.assertTrue(checker('IDBlock'))
        self.assertTrue(checker('IdBlock'))
        self.assertTrue(checker('idBlock'))
        self.assertTrue(checker('BlockID'))
        self.assertTrue(checker('blockID'))
        self.assertTrue(checker('blockId'))
        self.assertTrue(checker('eventTNTExplosion'))

        self.assertFalse(checker('items'))
        self.assertFalse(checker('Items'))
        self.assertFalse(checker('ItemS'))
        self.assertFalse(checker('itemS'))
        self.assertFalse(checker('ITEMS'))

    def test_cut_camel_case_word(self):
        cuter = DictionaryForText._cut_camel_case_word

        self.assertEqual(['Break', 'Event'], cuter('BreakEvent'))
        self.assertEqual(
            ['Block', 'Break', 'Message'], cuter('BlockBreakMessage')
        )

        self.assertEqual(['ID', 'Block'], cuter('IDBlock'))
        self.assertEqual(['Id', 'Block'], cuter('IdBlock'))
        self.assertEqual(['id', 'Block'], cuter('idBlock'))
        self.assertEqual(['Block', 'ID'], cuter('BlockID'))
        self.assertEqual(['block', 'ID'], cuter('blockID'))
        self.assertEqual(['block', 'Id'], cuter('blockId'))

        self.assertEqual(
            ['event', 'TNT', 'Explosion'], cuter('eventTNTExplosion')
        )

    def test_prepare_camel_case_words(self):
        words = DictionaryForText._prepare_camel_case_words(
            {
                'BlockBreakEvent': 1, 'Event': 1, 'when': 1,
                'Block': 1, 'Break': 1
            }
        )
        self.assertEqual(
            {'Block': 2, 'Break': 2, 'Event': 2, 'when': 1}, words
        )

    def test_has_uppercase(self):
        self.assertTrue(DictionaryForText._check_has_uppercase('CAT'))
        self.assertTrue(DictionaryForText._check_has_uppercase('Cat'))
        self.assertTrue(DictionaryForText._check_has_uppercase('cAt'))
        self.assertTrue(DictionaryForText._check_has_uppercase('caT'))
        self.assertFalse(DictionaryForText._check_has_uppercase('cat'))

    def test_drop_uppercase(self):
        keep, drop = DictionaryForText._drop_upper_case(
            {'cat': 2, 'Cat': 3, 'item': 4}
        )
        self.assertEqual({'cat': 5, 'item': 4}, keep)
        self.assertEqual({'Cat': 'cat'}, drop)

    def test_has_end_ed(self):
        self.assertTrue(DictionaryForText._end_ed_checker('called'))
        self.assertTrue(DictionaryForText._end_ed_checker('created'))
        self.assertTrue(DictionaryForText._end_ed_checker('dropped'))

        self.assertFalse(DictionaryForText._end_ed_checker('call'))
        self.assertFalse(DictionaryForText._end_ed_checker('create'))
        self.assertFalse(DictionaryForText._end_ed_checker('cat'))

    def test_drop_end_ed(self):
        end_key = 'end_ed'
        keep, drop = DictionaryForText._drop_ends(
            {
                'called': 2, 'call': 3,
                'word': 1,
                'create': 4, 'created': 5,
                'drop': 1, 'dropped': 1
            },
            end_key
        )
        self.assertEqual({'call': 5, 'word': 1, 'create': 9, 'drop': 2}, keep)
        self.assertEqual(
            {
                'called': 'call',
                'created': 'create',
                'dropped': 'drop'
            }, drop[end_key]
        )

    def test_prepare_drop_end_ed(self):
        self.stream = StringIO(
            'the call called. create it. it will be created.'
        )
        dic = DictionaryForText(self.stream)
        words = dic.prepare()
        self.assertEqual(2, words['call'])
        self.assertEqual(2, words['create'])
        self.assertFalse('called' in words)
        self.assertFalse('created' in words)
        self.assertEqual(
            {'called': 'call', 'created': 'create'}, dic.get_drop_end_ed()
        )

    def test_has_end_ing(self):
        self.assertTrue(DictionaryForText._end_ing_checker('making'))
        self.assertTrue(DictionaryForText._end_ing_checker('dropping'))

        self.assertFalse(DictionaryForText._end_ing_checker('make'))
        self.assertFalse(DictionaryForText._end_ing_checker('drop'))

    def test_drop_end_ing(self):
        end_key = 'end_ing'
        keep, drop = DictionaryForText._drop_ends(
            {
                'make': 1, 'making': 1,
                'running': 2, 'run': 2,
                'craft': 4, 'crafting': 4,
                'string': 5
            },
            end_key
        )
        self.assertEqual({'make': 2, 'run': 4, 'craft': 8, 'string': 5}, keep)
        self.assertEqual(
            {
                'making': 'make',
                'running': 'run',
                'crafting': 'craft'
            }, drop[end_key]
        )

    def test_prepare_drop_end_ing(self):
        self.stream = StringIO(
            'th the thing are running during I am run too. Music is dur'
        )
        dic = DictionaryForText(self.stream)
        words = dic.prepare()
        self.assertEqual(1, words['thing'])
        self.assertEqual(1, words['during'])
        self.assertEqual(2, words['run'])

        self.assertFalse('running' in words)
        self.assertEqual(
            {'running': 'run'}, dic.get_drop_end_ing()
        )

    def test_exceptions(self):
        keep, drop = DictionaryForText._drop_ends(
            {
                'seed': 2, 'see': 3, 'seeds': 1, 'spe': 4, 'speed': 5,
                'bee': 2, 'bees': 3, 'be': 4, 'goods': 2, 'good': 3,
                'http': 2, 'https': 3
            },
            ('end_ed', 'end_s', 'end_es')
        )
        self.assertEqual(
            {
                'seed': 3, 'see': 3, 'spe': 4, 'speed': 5, 'bee': 5, 'be': 4,
                'goods': 2, 'good': 3, 'http': 2, 'https': 3
            },
            keep
        )
        self.assertEqual({'seeds': 'seed', 'bees': 'bee'}, drop['end_s'])
        self.assertEqual({}, drop['end_ed'])
