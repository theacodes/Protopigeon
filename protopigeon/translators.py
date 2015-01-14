try:
    from . import ndb_translators
    NDB_SUPPORT = True
except ImportError:
    NDB_SUPPORT = False

try:
    from . import sql_translators
    SQL_SUPPORT = True
except ImportError:
    SQL_SUPPORT = False


import inspect


def is_ndb(model):
    if not NDB_SUPPORT:
        return False
    if (inspect.isclass(model) and issubclass(model, ndb_translators._ndb_classes)) or isinstance(model, ndb_translators._ndb_classes):
        return True
    return False


def is_sql(model):
    if not SQL_SUPPORT:
        return False
    # there's probably a better test
    if hasattr(model, '__table__'):
        return True
    return False


def to_message(model, message, converters=None, only=None, exclude=None):
    if is_ndb(model):
        return ndb_translators.to_message(model, message, converters, only, exclude)
    if is_sql(model):
        return sql_translators.to_message(model, message, converters, only, exclude)
    raise ValueError("Expected an ndb model or a sqlalchemy model, got %s" % model)


def to_entity(message, model, converters=None, only=None, exclude=None, key_field='id'):
    if is_ndb(model):
        return ndb_translators.to_entity(message, model, converters, only, exclude, key_field)
    if is_sql(model):
        return sql_translators.to_model(message, model, converters, only, exclude)
    raise ValueError("Expected an ndb model or a sqlalchemy model, got %s" % model)


to_model = to_entity


def model_message(Model, only=None, exclude=None, converters=None, key_field='id'):
    if is_ndb(Model):
        return ndb_translators.model_message(Model, only, exclude, converters, key_field)
    if is_sql(Model):
        return sql_translators.model_message(Model, only, exclude, converters)
    raise ValueError("Expected an ndb model or a sqlalchemy model, got %s" % Model)
