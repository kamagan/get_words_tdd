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

    def prepare(self):
        row = re.split('[\s.,:;—!?…\(\)\{\}\[\]\"«»“”]+', self.text)

        words = {}
        for word in row:
            if word in words:
                words[word] += 1
            else:
                words[word] = 1

        words, self.__drop['short'] = self._drop_short_words(words)

        return words

    @staticmethod
    def _get_content(stream):
        return stream.read()

    @staticmethod
    def _short_checker(word):
        return len(word) < 3

    @classmethod
    def _drop_short_words(cls, words):
        keep = {k: v for k, v in words.items() if not cls._short_checker(k)}
        drop = {k: v for k, v in words.items() if cls._short_checker(k)}
        return keep, drop
