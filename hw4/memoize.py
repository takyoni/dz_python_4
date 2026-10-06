# Задание 4. Кэширование через замыкание.

import time


def memoize(func):
    cache = {}

    def wrapper(*args, **kwargs):
        key = (args, tuple(sorted(kwargs.items())))
        try:
            hash(key)
        except TypeError:
            return func(*args, **kwargs)
        if key in cache:
            wrapper.hits += 1
            return cache[key]
        wrapper.misses += 1
        result = cache[key] = func(*args, **kwargs)
        return result

    def cache_clear():
        cache.clear()
        wrapper.hits = wrapper.misses = 0

    wrapper.hits = 0
    wrapper.misses = 0
    wrapper.cache_clear = cache_clear
    wrapper.__name__ = func.__name__
    wrapper.__qualname__ = getattr(func, '__qualname__', func.__name__)
    wrapper.__doc__ = func.__doc__
    wrapper.__wrapped__ = func
    return wrapper


def fib(n):
    return n if n < 2 else fib(n - 1) + fib(n - 2)


def run_fib_experiment(n=30):
    global fib
    original = fib

    fast_fib = memoize(fib)
    start = time.perf_counter()
    result_a = fast_fib(n)
    time_a = time.perf_counter() - start
    print(f'A: fast_fib = memoize(fib)  fib({n}) = {result_a}  misses = {fast_fib.misses}  '
          f'время {time_a * 1000:.1f} мс')

    fib = memoize(fib)
    try:
        start = time.perf_counter()
        result_b = fib(n)
        time_b = time.perf_counter() - start
        print(f'B: fib = memoize(fib)       fib({n}) = {result_b}  misses = {fib.misses}  '
              f'время {time_b * 1000:.3f} мс  (быстрее в ~{time_a / time_b:.0f} раз)')
        return fast_fib.misses, fib.misses
    finally:
        fib = original


if __name__ == '__main__':
    calls = []

    def slow_square(x, power=2):
        '''Возводит в степень.'''
        calls.append(x)
        return x ** power

    sq = memoize(slow_square)
    assert sq(3) == 9 and sq(3) == 9 and sq(3, power=3) == 27
    assert calls == [3, 3]
    assert (sq.hits, sq.misses) == (1, 2)
    assert sq.__name__ == 'slow_square' and sq.__doc__ == 'Возводит в степень.'
    total = memoize(sum)
    assert total([1, 2, 3]) == 6 and total([1, 2, 3]) == 6
    assert (total.hits, total.misses) == (0, 0)
    sq.cache_clear()
    assert (sq.hits, sq.misses) == (0, 0)
    sq(3)
    assert calls[-1] == 3

    def f(a, b=0, *, c=0):
        calls.append((a, b, c))
        return a + b + c

    mf = memoize(f)
    assert mf(1, b=2) == 3 and mf(1, b=3) == 4
    assert mf(1, b=2, c=1) == mf(1, c=1, b=2) == 4
    assert (mf.hits, mf.misses) == (1, 3)
    assert memoize(len)((1, 2)) == 2
    assert memoize(len)(((1, [2]),)) == 1
    none_calls = []
    mn = memoize(lambda: none_calls.append(1))
    mn(), mn()
    assert none_calls == [1] and mn.hits == 1
    boom = memoize(lambda x: 1 / x)
    try:
        boom(0)
        assert False, 'ожидали ZeroDivisionError'
    except ZeroDivisionError:
        pass
    assert boom.misses == 1 and boom(1) == 1.0
    type_err = memoize(lambda x: x + 'a')
    try:
        type_err(1)
        assert False, 'ожидали TypeError'
    except TypeError:
        pass
    assert 'hits' in sq.__dict__ and sq.__wrapped__ is slow_square

    misses_a, misses_b = run_fib_experiment(30)
    assert misses_a == 1 and misses_b == 31
    print('memoize: OK')

# A почти не помогает: рекурсия внутри fib вызывает глобальную fib, а она без кэша (misses = 1).
# В B мы заменили глобальное имя fib на обертку. Имя fib ищется в момент вызова: в L и E его нет,
# находится в G, а там уже обертка. Поэтому рекурсия идет через кэш, misses = 31.
# У меня A ~70 мс, B ~0.05 мс.
