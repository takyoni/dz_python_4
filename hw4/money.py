# Задание 2. Хешируемый неизменяемый класс-значение.


class Money:
    __slots__ = ('amount', 'currency')

    def __init__(self, amount, currency):
        if not isinstance(amount, int) or isinstance(amount, bool):
            raise TypeError('amount должен быть целым числом копеек')
        if not isinstance(currency, str):
            raise TypeError('currency должна быть строкой')
        object.__setattr__(self, 'amount', amount)
        object.__setattr__(self, 'currency', currency)

    def __setattr__(self, name, value):
        raise AttributeError(f'{type(self).__name__} неизменяемый: нельзя установить {name!r}')

    def __delattr__(self, name):
        raise AttributeError(f'{type(self).__name__} неизменяемый: нельзя удалить {name!r}')

    def __eq__(self, other):
        if not isinstance(other, Money):
            return NotImplemented
        return (self.amount, self.currency) == (other.amount, other.currency)

    def __hash__(self):
        return hash((self.amount, self.currency))

    def __add__(self, other):
        if not isinstance(other, Money):
            return NotImplemented
        if self.currency != other.currency:
            raise ValueError(f'нельзя сложить {self.currency} и {other.currency}')
        return Money(self.amount + other.amount, self.currency)

    def __repr__(self):
        return f'Money({self.amount}, {self.currency!r})'


def total_by_currency(payments):
    totals = {}
    for m in payments:
        totals[m.currency] = totals[m.currency] + m if m.currency in totals else m
    return totals


if __name__ == '__main__':
    assert len({Money(100, 'RUB'), Money(100, 'RUB'), Money(100, 'USD')}) == 2
    prices = {Money(100, 'RUB'): 'сто рублей'}
    assert prices[Money(100, 'RUB')] == 'сто рублей'
    assert Money(100, 'RUB') + Money(50, 'RUB') == Money(150, 'RUB')
    for action in (lambda m: setattr(m, 'amount', 5), lambda m: setattr(m, 'extra', 1)):
        try:
            action(Money(1, 'RUB'))
            assert False, 'ожидали AttributeError'
        except AttributeError:
            pass
    try:
        Money(1, 'RUB') + Money(1, 'USD')
        assert False, 'ожидали ValueError'
    except ValueError:
        pass
    pays = [Money(100, 'RUB'), Money(5, 'USD'), Money(250, 'RUB')]
    assert total_by_currency(pays) == {'RUB': Money(350, 'RUB'), 'USD': Money(5, 'USD')}

    m = Money(1500, 'RUB')
    assert repr(m) == "Money(1500, 'RUB')"
    assert m != Money(1500, 'USD') and m != Money(1501, 'RUB')
    assert m.__eq__(1500) is NotImplemented and m != 1500 and m != (1500, 'RUB')
    assert hash(m) == hash(Money(1500, 'RUB'))
    a, b = Money(1, 'RUB'), Money(2, 'RUB')
    c = a + b
    assert c is not a and c is not b and (a.amount, b.amount) == (1, 2)
    assert Money(-100, 'RUB') + Money(100, 'RUB') == Money(0, 'RUB')
    assert not hasattr(m, '__dict__')
    for action in (lambda: delattr(m, 'amount'), lambda: m + 1):
        try:
            action()
            assert False, 'ожидали исключение'
        except (AttributeError, TypeError):
            pass
    for bad in ((1.5, 'RUB'), ('100', 'RUB'), (100, None)):
        try:
            Money(*bad)
            assert False, 'ожидали TypeError'
        except TypeError:
            pass
    assert total_by_currency([]) == {}
    print('money: OK')

# Если поменять поле, когда объект уже лежит в set или в ключах dict, хеш станет другим,
# а объект останется в старой корзине и его уже не найти. Как с Point на лекции: после p.x = 100
# p in visited дает False. Поэтому Money неизменяемый.
