# Задание 1. Своя хеш-таблица с цепочками.

import time


class MyDict:
    def __init__(self, size=8):
        self._buckets = [[] for _ in range(size)]
        self._len = 0

    def _bucket(self, key):
        return self._buckets[hash(key) % len(self._buckets)]

    def _resize(self):
        old = self._buckets
        self._buckets = [[] for _ in range(len(old) * 2)]
        for bucket in old:
            for key, value in bucket:
                self._bucket(key).append((key, value))

    def __setitem__(self, key, value):
        bucket = self._bucket(key)
        for i, (k, _) in enumerate(bucket):
            if k == key:
                bucket[i] = (key, value)
                return
        bucket.append((key, value))
        self._len += 1
        if self._len > len(self._buckets) * 2 / 3:
            self._resize()

    def __getitem__(self, key):
        for k, v in self._bucket(key):
            if k == key:
                return v
        raise KeyError(key)

    def __delitem__(self, key):
        bucket = self._bucket(key)
        for i, (k, _) in enumerate(bucket):
            if k == key:
                bucket.pop(i)
                self._len -= 1
                return
        raise KeyError(key)

    def __contains__(self, key):
        for k, _ in self._bucket(key):
            if k == key:
                return True
        return False

    def __len__(self):
        return self._len

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def stats(self):
        longest = max(len(b) for b in self._buckets)
        return len(self._buckets), self._len, longest

    def __repr__(self):
        pairs = [f'{k!r}: {v!r}' for bucket in self._buckets for k, v in bucket]
        return 'MyDict({' + ', '.join(pairs) + '})'


class BadKey:
    # ключ с одинаковым хешем для эксперимента

    def __init__(self, n):
        self.n = n

    def __eq__(self, other):
        return isinstance(other, BadKey) and self.n == other.n

    def __hash__(self):
        return 42


def experiment(n=1000):
    for name, make in (('str', lambda i: f'key{i}'), ('hash=42', BadKey)):
        keys = [make(i) for i in range(n)]
        d = MyDict()
        start = time.perf_counter()
        for i, k in enumerate(keys):
            d[k] = i
        elapsed = time.perf_counter() - start
        print(f'{name:8} stats={d.stats()}  вставка {n} ключей: {elapsed * 1000:.1f} мс')


if __name__ == '__main__':
    d = MyDict()
    for i in range(1000):
        d[f'key{i}'] = i
    assert len(d) == 1000
    assert d['key42'] == 42
    assert 'key7' in d and 'nope' not in d
    d['key42'] = -1
    assert d['key42'] == -1 and len(d) == 1000
    del d['key42']
    assert 'key42' not in d and len(d) == 999
    assert d.get('nope') is None and d.get('nope', 0) == 0
    for bad in (lambda: d['nope'], lambda: d.__delitem__('nope')):
        try:
            bad()
            assert False, 'ожидали KeyError'
        except KeyError:
            pass
    buckets, size, longest = d.stats()
    assert size == 999 and size <= buckets * 2 / 3
    print(d.stats())

    e = MyDict(size=1)
    assert len(e) == 0 and 'x' not in e and repr(e) == 'MyDict({})'
    e['x'] = 1
    assert e.stats()[0] == 2 and e['x'] == 1
    e[1] = 'int'
    e[1.0] = 'float'
    assert len(e) == 2 and e[1] == 'float'
    e[None] = 0
    e[(1, 2)] = 'tuple'
    assert e.get(None) == 0 and e[(1, 2)] == 'tuple'
    try:
        e[[1, 2]] = 'list'
        assert False, 'ожидали TypeError'
    except TypeError:
        pass

    experiment()

# Ответы
#
# 1. Номер корзины это hash % число корзин. Число корзин поменялось, значит у ключа будет другая
# корзина, и если просто скопировать пары, то ключ потом не найдется.
#
# 2. Для строк stats() показывает (2048, 1000, 4-6), корзины короткие. Если hash всегда 42, то все
# ключи в одной корзине: (2048, 1000, 1000), и каждая вставка идет по всему списку.
# У меня вставка 1000 таких ключей ~25 мс, а строк ~1 мс.
