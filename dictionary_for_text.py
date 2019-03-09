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

    def get_drop_end_ing(self):
        return self.__drop['end_ing']

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
        words, drop = self._drop_ends(words)
        self.__drop.update(drop)

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
        for_check, keep = cls._separate_by_checker(
            words, cls._proper_name_checker
        )
        drop = {}

        for word in for_check:
            word_finding = word.lower()
            if word_finding in keep:
                keep[word_finding] += words[word]
            else:
                drop[word] = words[word]

        return keep, drop

    @staticmethod
    def _end_s_checker(word):
        return word[-1:] == 's' and word[-2:-1] != 's'

    @staticmethod
    def _end_apostrophe_s_checker(word):
        return word[-2:] in ['\'s', '’s']

    @staticmethod
    def _end_ies_checker(word):
        return word[-3:] == 'ies'

    @staticmethod
    def _end_es_checker(word):
        return word[-2:] == 'es'

    @staticmethod
    def _end_ed_checker(word):
        return word[-2:] == 'ed'

    @staticmethod
    def _end_ing_checker(word):
        return word[-3:] == 'ing'

    @staticmethod
    def _check_has_uppercase(word):
        return re.match('^.*[A-Z]+.*$', word) is not None

    @staticmethod
    def _droper_last_repeated_letter(word):
        double_last_letters = (
            len(word) > 1
            and
            word[-1] == word[-2]
        )
        return slice(0, -1) if (double_last_letters) else slice(0, len(word))

    @classmethod
    def _drop_upper_case(cls, words):
        for_check, keep = cls._separate_by_checker(
            words, cls._check_has_uppercase
        )
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
    def _drop_ends(cls, words, kind=None):
        if isinstance(kind, str):
            kind = (kind, )

        ends = {
            'end_apostrophe_s': {
                'checker': cls._end_apostrophe_s_checker,
                'excision': slice(0, -2)
            },
            'end_ies': {
                'checker': cls._end_ies_checker,
                'excision': slice(0, -3),
                'substitute': ('y', )
            },
            'end_es': {
                'checker': cls._end_es_checker,
                'excision': slice(0, -2),
                'exception': ('bees', )
            },
            'end_s': {
                'checker': cls._end_s_checker,
                'excision': slice(0, -1),
                'exception': ('goods', 'https')
            },
            'end_ed': {
                'checker': cls._end_ed_checker,
                'excision': slice(0, -2),
                'substitute': ('e', ''),
                'exception': ('seed', 'speed')
            },
            'end_ing': {
                'checker': cls._end_ing_checker,
                'excision': slice(0, -3),
                'excision_add': cls._droper_last_repeated_letter,
                'substitute': ('e', ''),
                'exception': ('thing', 'during')
            }
        }

        if kind is None:
            actual_ends = ends
        else:
            actual_ends = {k: v for k, v in ends.items() if k in kind}

        drop = {}
        for end_key in actual_ends:
            end = actual_ends[end_key]
            checker = end['checker']
            excision = end['excision']
            excision_add = end['excision_add'] if 'excision_add' in end else None
            substitute = end['substitute'] if 'substitute' in end else ('', )
            exception = end['exception'] if 'exception' in end else ('', )

            words, drop[end_key] = cls._drop_end(
                words, checker, excision, excision_add, substitute, exception
            )

        return words, drop

    @classmethod
    def _drop_end(
        cls, words, checker, excision, excision_add, substitute, exception
    ):
        for_check, keep = cls._separate_by_checker(words, checker)
        drop = {}

        for word in for_check:
            if word in exception:
                keep[word] = words[word]
                continue

            word_is_dropped = False
            excised = word[excision]
            words_for_find = [excised + end for end in substitute]
            if excision_add is not None:
                words_for_find.append(excised[excision_add(excised)])

            for word_finding in words_for_find:
                if word_finding in keep:
                    keep[word_finding] += words[word]
                    drop[word] = word_finding
                    word_is_dropped = True
                    break

            if not word_is_dropped:
                keep[word] = words[word]

        return keep, drop

    # заглавная не только в начале, есть сторочные символы
    @staticmethod
    def _camel_case_checker(word):
        return (
            re.match('^.+[A-Z]+.+$', word) is not None
            and
            re.match('^.*[a-z]+.*$', word) is not None
        )

    @staticmethod
    def _cut_camel_case_word(word):
        # режем по загловной букве, если после неё идёт строчная
        separated = re.sub('(?<=[a-zA-Z])([A-Z][a-z]+)', r' \1', word)

        # или по первой заглавной, если после неё идут только заглавные
        separated = re.sub('([a-z]+)([A-Z]{2,})', r'\1 \2', separated)

        return separated.split()

    @classmethod
    def _prepare_camel_case_words(cls, words):
        for_cut, keep = cls._separate_by_checker(
            words, cls._camel_case_checker
        )

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
