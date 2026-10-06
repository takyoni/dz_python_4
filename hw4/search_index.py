# Задание 3. Поиск по документам с инвертированным индексом.

import heapq
import re
from collections import Counter


def tokenize(text):
    return re.findall(r'\w+', text.lower())


class SearchIndex:
    # _index: слово -> множество id документов, по нему идет поиск
    # _docs: id -> Counter слов документа, чтобы remove и повторный add не обходили весь индекс
    # _totals: общий счетчик слов для top_words

    def __init__(self):
        self._index = {}
        self._docs = {}
        self._totals = Counter()

    def add(self, doc_id, text):
        if doc_id in self._docs:
            self.remove(doc_id)
        counts = Counter(tokenize(text))
        self._docs[doc_id] = counts
        for word in counts:
            self._index.setdefault(word, set()).add(doc_id)
        self._totals.update(counts)

    def remove(self, doc_id):
        counts = self._docs.pop(doc_id)
        for word, n in counts.items():
            ids = self._index[word]
            ids.discard(doc_id)
            if not ids:
                del self._index[word]
            self._totals[word] -= n
            if self._totals[word] == 0:
                del self._totals[word]

    def _sets(self, words):
        return [self._index.get(w.lower(), set()) for w in words]

    def search_all(self, *words):
        if not words:
            return set()
        sets = sorted(self._sets(words), key=len)
        result = set(sets[0])
        for s in sets[1:]:
            if not result:
                break
            result &= s
        return result

    def search_any(self, *words):
        return set().union(*self._sets(words))

    def top_words(self, n):
        return heapq.nsmallest(n, self._totals.items(), key=lambda p: (-p[1], p[0]))

    def __len__(self):
        return len(self._docs)


if __name__ == '__main__':
    idx = SearchIndex()
    idx.add(1, 'Python is a programming language.')
    idx.add(2, 'A dict is a hash table; a set is a hash table too!')
    idx.add(3, 'Python dict and set are fast.')
    assert idx.search_all('python') == {1, 3}
    assert idx.search_all('dict', 'set') == {2, 3}
    assert idx.search_all('python', 'hash') == set()
    assert idx.search_any('language', 'fast') == {1, 3}
    assert idx.search_all('PYTHON') == {1, 3}
    assert idx.search_all('nothing') == set()
    assert idx.top_words(2) == [('a', 5), ('is', 3)]

    idx.remove(1)
    assert idx.search_all('python') == {3}
    assert idx.search_any('language', 'programming') == set()
    idx.add(3, 'Totally new text')
    assert idx.search_all('python') == set()
    assert idx.search_all('new') == {3}

    assert 'python' not in idx._index and 'language' not in idx._index
    assert idx.search_all() == set() and idx.search_any() == set()
    assert idx.top_words(100) == sorted(idx.top_words(100), key=lambda p: (-p[1], p[0]))
    assert idx.top_words(0) == []
    r = idx.search_all('hash')
    r.add(999)
    assert idx.search_all('hash') == {2}
    idx.add(4, '')
    assert len(idx) == 3 and idx.search_any('new', 'hash') == {2, 3}
    idx.remove(2)
    idx.remove(3)
    idx.remove(4)
    assert idx._index == {} and idx.top_words(5) == [] and len(idx) == 0
    try:
        idx.remove(42)
        assert False, 'ожидали KeyError'
    except KeyError:
        pass
    print('search_index: OK')
