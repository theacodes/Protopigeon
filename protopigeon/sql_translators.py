from .sql_converters import converters as default_converters
from protorpc import messages
import inspect


def model_message(Model, only=None, exclude=None, converters=None):
    class_name = Model.__name__ + 'Message'

    columns = Model.__table__.columns
    field_names = [x.name for x in columns]

    if exclude:
        field_names = [x for x in field_names if x not in exclude]

    if only:
        field_names = [x for x in field_names if x in only]

    converters = (
        dict(default_converters.items() + converters.items())
        if converters else default_converters)

    field_dict = {}

    for count, name in enumerate(field_names, start=1):
        column = columns[name]
        column_type = column.type.__class__.__name__
        converter = converters.get(column_type, None)

        if converter:
            field_dict[name] = converter.to_field(Model, column, count)

    return type(class_name, (messages.Message,), field_dict)


def to_message(model, message, converters=None, only=None, exclude=None):
    message_fields, _, fields = _common_fields(model, message, only, exclude)

    converters = dict(default_converters.items() + converters.items()) if converters else default_converters

    columns = model.__table__.columns

    values = {}

    for field in fields:
        if field not in columns:
            continue

        column = columns[field]
        message_field = message.field_by_name(field)
        value = getattr(model, field)

        converter = converters[column.type.__class__.__name__]

        if converter:
            if value is not None:  # only try to convert if the value is meaningful, otherwise leave it as Falsy.
                value = converter.to_message(model, column, message_field, value)
            values[field] = value

    if inspect.isclass(message):
        return message(**values)
    else:
        for name, value in values.iteritems():
            setattr(message, name, value)
        return message


def to_model(message, model, converters=None, only=None, exclude=None):
    message_fields, _, fields = _common_fields(model, message, only, exclude)

    converters = dict(default_converters.items() + converters.items()) if converters else default_converters

    values = {}

    columns = model.__table__.columns

    # Other fields
    for field in fields:
        if field not in columns:
            continue

        column = columns[field]

        converter = converters[column.type.__class__.__name__]

        if not converter:
            continue

        message_field = message.field_by_name(field)
        value = getattr(message, field)

        if value is not None:
            value = converter.to_model(message, column, message_field, value)

        values[field] = value

    if inspect.isclass(model):
        return model(**values)
    else:
        for k, v in values.iteritems():
            setattr(model, k, v)
        return model


def _common_fields(entity, message, only=None, exclude=None):
    message_fields = [x.name for x in message.all_fields()]
    column_names = [x.name for x in entity.__table__.columns]

    fields = set(message_fields) & set(column_names)

    if only:
        fields = set(only) & set(fields)

    if exclude:
        fields = [x for x in fields if x not in exclude]

    return message_fields, column_names, fields
