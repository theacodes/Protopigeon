import copy
from protorpc import messages


def list_message(message_type):
    name = message_type.__name__ + 'Collection'
    fields = {
        'items': messages.MessageField(message_type, 1, repeated=True),
        'nextPageToken': messages.StringField(2)
    }
    return type(name, (messages.Message,), fields)


collection_message = list_message


def compose(*args):
    fields = {}
    name = 'Composed'

    for message_cls in args:
        name += message_cls.__name__
        for field in message_cls.all_fields():
            fields[field.name] = field

    for n, orig_field in enumerate(fields.values(), 1):
        field = copy.copy(orig_field)
        # This is so ridiculously hacky. I'm not proud of it, but the alternative to doing this is trying to reconstruct each
        # field by figuring out the arguments originally passed into __init__. I think this is honestly a little cleaner.
        object.__setattr__(field, 'number', n)
        fields[field.name] = field

    return type(name, (messages.Message,), fields)
