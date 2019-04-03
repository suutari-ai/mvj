from typing import Tuple

from django.db import models

from .intset import IntegerSetSpecifier


class IntegerSetSpecifierField(models.CharField):
    def __init__(
            self,
            *,
            value_range: Tuple[int, int],
            **kwargs: object,
    ) -> None:
        assert isinstance(value_range, tuple)
        assert len(value_range) == 2
        assert all(isinstance(x, int) for x in value_range)
        self.value_range: Tuple[int, int] = tuple(value_range)
        kwargs.setdefault('max_length', 200)
        super().__init__(**kwargs)

    def deconstruct(self):
        (name, path, args, kwargs) = super().deconstruct()
        kwargs['value_range'] = self.value_range
        if kwargs.get('max_length') == 200:
            del kwargs['max_length']
        return (name, path, args, kwargs)

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        return IntegerSetSpecifier(value, *self.value_range)

    def to_python(self, value):
        if value is None or isinstance(value, IntegerSetSpecifier):
            return value
        spec = super().to_python(value)
        return IntegerSetSpecifier(spec, *self.value_range)

    def get_prep_value(self, value):
        return value.spec


class NullableIntegerSetSpecifierField(IntegerSetSpecifierField):
    def __init__(
            self,
            *,
            value_range: Tuple[int, int],
            **kwargs: object,
    ) -> None:
        kwargs['null'] = True
        kwargs['blank'] = True
        super().__init__(value_range=value_range, **kwargs)

    def deconstruct(self):
        (name, path, args, kwargs) = super().deconstruct()
        kwargs.pop('null', None)
        kwargs.pop('blank', None)
        return (name, path, args, kwargs)
