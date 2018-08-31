import re


class DictionaryForText:

    def __init__(self, stream):
        self._text = self.get_content(stream)

    def get_text(self):
        return self._text

    text = property(get_text, None, None, '')

    def prepare(self):
        row = re.split('[\s.,:;—!?…]+', self.text)

        words = {}
        for word in row:
            if word in words:
                words[word] += 1
            else:
                words[word] = 1

        return words

    @staticmethod
    def get_content(stream):
        return stream.read()
