import inspect
from protorpc import messages
from .ndb_converters import converters as default_ndb_converters
from google.appengine.ext import ndb
from google.appengine.ext.ndb import polymodel


class holder(object):
    pass


default_converters = default_ndb_converters

_ndb_classes = (ndb.Model, ndb.Expando, polymodel.PolyModel)


def _model_fields(model):
    if (inspect.isclass(model) and issubclass(model, _ndb_classes)) or isinstance(model, _ndb_classes):
        return [k for k, v in model._properties.iteritems()]
    else:
        raise ValueError("Not an ndb model")


def _is_dynamic_model(model):
    return (inspect.isclass(model) and not issubclass(model, ndb.Expando)) and not isinstance(model, ndb.Expando)


def _common_fields(entity, message, only=None, exclude=None):
    message_fields = [x.name for x in message.all_fields()]
    model_fields = _model_fields(entity)

    if _is_dynamic_model:
        fields = set(message_fields) & set(model_fields)
    else:
        fields = set(message_fields) - set(['key'])

    if only:
        fields = set(only) & set(fields)

    if exclude:
        fields = [x for x in fields if x not in exclude]

    return message_fields, model_fields, fields


def to_message(entity, message, converters=None, only=None, exclude=None, key_field='id'):
    message_fields, entity_properties, fields = _common_fields(entity, message, only, exclude)

    converters = dict(default_converters.items() + converters.items()) if converters else default_converters

    # Key first
    values = {}

    # Key first
    if key_field is not False:
        values[key_field] = converters['Key'].to_message(entity, 'key', key_field, entity.key) if entity.key else None

    # Other fields
    for field in fields:
        if field not in entity._properties:
            continue

        property = entity._properties[field]
        message_field = message.field_by_name(field)
        value = getattr(entity, field)

        converter = converters[property.__class__.__name__]

        if converter:
            if value is not None:  # only try to convert if the value is meaningful, otherwise leave it as Falsy.
                if property._repeated:
                    value = [converter.to_message(entity, property, message_field, x) if x else x for x in value]
                else:
                    value = converter.to_message(entity, property, message_field, value)
            values[field] = value

    if inspect.isclass(message):
        return message(**values)
    else:
        for name, value in values.iteritems():
            setattr(message, name, value)
        return message


def to_entity(message, model, converters=None, only=None, exclude=None, key_field='id'):
    message_fields, entity_properties, fields = _common_fields(model, message, only, exclude)

    converters = dict(default_converters.items() + converters.items()) if converters else default_converters

    values = {}

    # Key first, if it's there
    if key_field is not False and hasattr(message, key_field) and getattr(message, key_field):
        values['key'] = converters['Key'].to_model(messages, 'key', key_field, getattr(message, key_field))

    # Other fields
    for field in fields:
        if field in model._properties:
            property = model._properties[field]
        elif (inspect.isclass(model) and issubclass(model, ndb.Expando)) or isinstance(model, ndb.Expando):
            property = ndb.GenericProperty(field)
        else:
            continue

        converter = converters[property.__class__.__name__]
        message_field = message.field_by_name(field)
        value = getattr(message, field)

        if converter:
            if value is not None:
                if property._repeated:
                    value = [converter.to_model(message, property, message_field, x) if x else x for x in value]
                else:
                    value = converter.to_model(message, property, message_field, value)
            elif property._repeated:
                value = []

            values[field] = value

    if inspect.isclass(model):
        return model(**values)
    else:
        model.populate(**values)
        return model


def model_message(Model, only=None, exclude=None, converters=None, key_field='id'):
    class_name = Model.__name__ + 'Message'

    props = Model._properties
    sorted_props = sorted(props.iteritems(), key=lambda prop: prop[1]._creation_counter)
    field_names = [x[0] for x in sorted_props if x[0]]

    if exclude:
        field_names = [x for x in field_names if x not in exclude]

    if only:
        field_names = [x for x in field_names if x in only]

    converters = dict(default_converters.items() + converters.items()) if converters else default_converters

    # Add in the key field.
    key_holder = holder()
    key_holder.name = 'key',
    key_holder._repeated = False
    field_dict = {
        key_field: converters['Key'].to_field(Model, key_holder, 1)
    }

    # Add all other fields.
    for count, name in enumerate(field_names, start=2):
        prop = props[name]
        converter = converters.get(prop.__class__.__name__, None)

        if converter:
            field_dict[name] = converter.to_field(Model, prop, count)

    return type(class_name, (messages.Message,), field_dict)