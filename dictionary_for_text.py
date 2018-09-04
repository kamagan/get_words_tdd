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

