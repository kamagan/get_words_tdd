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

    def get_drop_end_es(self):
        return self.__drop['end_es']

    def get_drop_end_ed(self):
        return self.__drop['end_ed']

    def get_drop_uppercase(self):
        return self.__drop['uppercase']

    def prepare(self):
        row = re.split('[\-\'’]*[^a-zA-Z\-\'’]+[\-\'’]*', self.text)

        words = {}
        for word in row:
            if word in words:
                words[word] += 1
            else:
                words[word] = 1

        words = self._prepare_camel_case_words(words)

        words, self.__drop['short'] = self._drop_short_words(words)
        words, self.__drop['proper_name'] = self._drop_proper_name(words)

        words, self.__drop['uppercase'] = self._drop_upper_case(words)

        words, self.__drop['end_apostrophe_s'] = self._drop_end_apostrophe_s(words)
        words, self.__drop['end_s'] = self._drop_end_s(words)
        words, self.__drop['end_ies'] = self._drop_end_ies(words)
        words, self.__drop['end_es'] = self._drop_end_es(words)
        words, self.__drop['end_ed'] = self._drop_end_ed(words)

        return words

    @staticmethod
    def _get_content(stream):
        return stream.read()

    @staticmethod
    def _short_checker(word):
        return re.match('.*[a-zA-Z]{3,}.*', word) is None

    @classmethod
    def _drop_short_words(cls, words):
        drop, keep = cls._separate_by_checker(words, cls._short_checker)
        return keep, drop

    @staticmethod
    def _proper_name_checker(word):
        return re.match('^[A-Z]{1}[a-z]+$', word) is not None

    @classmethod
    def _drop_proper_name(cls, words):
        for_check, keep = cls._separate_by_checker(words, cls._proper_name_checker)
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
        return word[-1:] == 's' and word[-2:-1] != 's'

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
    def _end_es_checker(word):
        return word[-2:] == 'es'

    @classmethod
    def _drop_end_es(cls, words):
        return cls._drop_ends(words, cls._end_es_checker, slice(0, -2))

    @staticmethod
    def _end_ed_checker(word):
        return word[-2:] == 'ed'

    @classmethod
    def _drop_end_ed(cls, words):
        return cls._drop_ends(words, cls._end_ed_checker, slice(0, -2), ('e', ''))

    @staticmethod
    def _check_has_uppercase(word):
        return re.match('^.*[A-Z]+.*$', word) is not None

    @classmethod
    def _drop_upper_case(cls, words):
        for_check, keep = cls._separate_by_checker(words, cls._check_has_uppercase)
        drop = {}

        for word in for_check:
            word_finding = word.lower()
            if word_finding in keep:
                keep[word_finding] += words[word]
                drop[word] = word_finding
            else:
                keep[word] = words[word]

        return keep, drop


    @classmethod
    def _drop_ends(cls, words, checker, excision, substitute=''):
        if not isinstance(substitute, tuple):
            substitute = (substitute,)

        for_check, keep = cls._separate_by_checker(words, checker)
        drop = {}

        for word in for_check:
            word_is_dropped = False
            for add_to_end in substitute:
                word_finding = word[excision] + add_to_end
                if word_finding in keep:
                    keep[word_finding] += words[word]
                    drop[word] = word_finding
                    word_is_dropped = True
                    break

            if not word_is_dropped:
                keep[word] = words[word]

        return keep, drop

    @staticmethod
    # заглавная не только в начале, есть сторочные символы
    def _camel_case_checker(word):
        return (
            re.match('^.+[A-Z]+.+$', word) is not None
            and
            re.match('^.*[a-z]+.*$', word) is not None
        )

    @staticmethod
    def _cut_camel_case_word(word):
        # режем по загловной букве, если после неё идёт строчная
        separated = re.sub('(?<=[a-zA-Z])([A-Z][a-z]+)', r' \1', word);

        # или по первой заглавной, если после неё идут только заглавные
        separated = re.sub('([a-z]+)([A-Z]{2,})', r'\1 \2', separated);

        return separated.split()

    @classmethod
    def _prepare_camel_case_words(cls, words):
        for_cut, keep = cls._separate_by_checker(words, cls._camel_case_checker)

        for word in for_cut:
            parts = cls._cut_camel_case_word(word)
            count = words[word]

            for part in parts:
                if part in keep:
                    keep[part] += count
                else:
                    keep[part] = count

        return keep

    @staticmethod
    def _separate_by_checker(words, checker):
        match = {k: v for k, v in words.items() if checker(k)}
        not_match = {k: v for k, v in words.items() if not checker(k)}
        return match, not_match

