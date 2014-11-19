import datetime
from protorpc import messages, message_types, util
from .types import DateMessage, TimeMessage
from .converter import Converter


class StringConverter(Converter):
    @staticmethod
    def to_field(Model, property, count):
        return messages.StringField(count)


class BooleanConverter(Converter):
    @staticmethod
    def to_field(Model, property, count):
        return messages.BooleanField(count)


class IntegerConverter(Converter):
    @staticmethod
    def to_field(Model, property, count):
        return messages.IntegerField(count)


class FloatConverter(Converter):
    @staticmethod
    def to_field(Model, property, count):
        return messages.FloatField(count)


class DateTimeConverter(Converter):
    @staticmethod
    def to_field(Model, property, count):
        return message_types.DateTimeField(count)


converters = {
    'String': StringConverter,
    'Unicode': StringConverter,
    'Text': StringConverter,
    'UnicodeText': StringConverter,
    'Boolean': BooleanConverter,
    'Integer': IntegerConverter,
    'BigInteger': IntegerConverter,
    'SmallInteger': IntegerConverter,
}
