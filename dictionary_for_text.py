import re


class DictionaryForText:

    def __init__(self, stream):
        self.__text = self._get_content(stream)
        self.__drop = {}

    def get_text(self):
        return self.__text

    text = property(get_text, None, None, '')

    def get_drop_short(self):
        return self.__drop['short']

    def get_drop_proper_name(self):
        return self.__drop['proper_name']

    def get_drop_end_s(self):
        return self.__drop['end_s']

    def get_drop_end_apostrophe_s(self):
        return self.__drop['end_apostrophe_s']

    def get_drop_end_ies(self):
        return self.__drop['end_ies']

    def prepare(self):
        row = re.split('[\-\'’]*[^a-zA-Z\-\'’]+[\-\'’]*', self.text)

        words = {}
        for word in row:
            if word in words:
                words[word] += 1
            else:
                words[word] = 1

        words, self.__drop['short'] = self._drop_short_words(words)
        words, self.__drop['proper_name'] = self._drop_proper_name(words)
        words, self.__drop['end_s'] = self._drop_end_s(words)
        words, self.__drop['end_apostrophe_s'] = self._drop_end_apostrophe_s(words)
        words, self.__drop['end_ies'] = self._drop_end_ies(words)

        return words

    @staticmethod
    def _get_content(stream):
        return stream.read()

    @staticmethod
    def _short_checker(word):
        return re.match('.*[a-zA-Z]{3,}.*', word) is None

    @classmethod
    def _drop_short_words(cls, words):
        keep = {k: v for k, v in words.items() if not cls._short_checker(k)}
        drop = {k: v for k, v in words.items() if cls._short_checker(k)}
        return keep, drop

    @staticmethod
    def _proper_name_checker(word):
        return re.match('^[A-Z]{1}[a-z]+$', word) is not None

    @classmethod
    def _drop_proper_name(cls, words):
        keep = {k: v for k, v in words.items() if not cls._proper_name_checker(k)}
        for_check = {k: v for k, v in words.items() if cls._proper_name_checker(k)}
        drop = {}

        for word in for_check:
            word_lower = word.lower()
            if word_lower in keep:
                keep[word_lower] += words[word]
            else:
                drop[word] = words[word]

        return keep, drop

    @staticmethod
    def _end_s_checker(word):
        return re.match('^.*[a-rt-z]{1}s$', word) is not None

    @classmethod
    def _drop_end_s(cls, words):
        return cls._drop_ends(words, cls._end_s_checker, slice(0, -1))

    @staticmethod
    def _end_apostrophe_s_checker(word):
        return word[-2:] in ['\'s', '’s']

    @classmethod
    def _drop_end_apostrophe_s(cls, words):
        return cls._drop_ends(
            words,
            cls._end_apostrophe_s_checker,
            slice(0, -2)
        )

    @staticmethod
    def _end_ies_checker(word):
        return word[-3:] == 'ies'

    @classmethod
    def _drop_end_ies(cls, words):
        return cls._drop_ends(words, cls._end_ies_checker, slice(0, -3), 'y')

    @staticmethod
    def _drop_ends(words, checker, excision, substitute=''):
        keep = {k: v for k, v in words.items() if not checker(k)}
        for_check = {k: v for k, v in words.items() if checker(k)}
        drop = {}

        for word in for_check:
            word_finding = word[excision] + substitute
            if word_finding in keep:
                keep[word_finding] += words[word]
                drop[word] = word_finding
            else:
                keep[word] = words[word]

        return keep, drop
