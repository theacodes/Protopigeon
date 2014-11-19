from .sql_converters import converters as default_converters
from protorpc import messages


def model_message(Model, only=None, exclude=None, converters=None, key_field='id'):
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

    # Add in the key field.
    # key_holder = holder()
    # key_holder.name = 'key',
    # key_holder._repeated = False
    # field_dict = {
    #     key_field: converters['Key'].to_field(Model, key_holder, 1)
    # }

    field_dict = {}

    # Add all other fields.
    for count, name in enumerate(field_names, start=2):
        column = columns[name]
        column_type = column.type.__class__.__name__
        converter = converters.get(column_type, None)

        if converter:
            field_dict[name] = converter.to_field(Model, column, count)

    return type(class_name, (messages.Message,), field_dict)
