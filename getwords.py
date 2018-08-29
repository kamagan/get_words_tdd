import re


def prepare(stream):
    content = get_content(stream)
    row = re.split('[\s]+', content)

    words = {}
    for word in row:
        if word in words:
            words[word] += 1
        else:
            words[word] = 1

    return words


def get_content(stream):
    return stream.read()

