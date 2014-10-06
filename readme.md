ProtoPigeon
===========

Protopigeon provides utilities for generating [protorpc Messages](https://cloud.google.com/appengine/docs/python/tools/protorpc/#Working_with_Messages) from [ndb Models]()https://cloud.google.com/appengine/docs/python/ndb/. It can generate Message classes from Models, translate entities to message instances and vice-verse. It can also compose multiple message classes together.


Usage
=====

Generating Message classes from a Model
---------------------------------------

If you have a model:

```python
class Actor(ndb.Model)
    name = ndb.StringProperty()
    shows = ndb.StringProperty(repeated=True)
    rating = ndb.IntegerProperty()
```

You can easily generate a message class:

```python
ActorMessage = protopigeon.model_message(Actor)
```

You can also exclude fields, or specify which particular fields:

```python
ActorWithoutRatingMessage = protopigeon.model_message(Action, exclude=('rating',))
ActorRatingMessage = protopigeon.model_message(Action, only=('rating',))
```

Translating between Entities and Messages
-----------------------------------------

Playing on the previous example, if you have an entity (an instance of a Model) and want to make a message:

```python
doctor = Actor(name='Matt Smith', shows=('Doctor Who', 'Moses Jones'), rating=90)

doctor_message = protopigeon.to_message(doctor, ActorMessage)
doctor_no_rating = protopigeon.to_message(doctor, ActorWithoutRatingMessage)
doctor_rating = protopigeon.to_message(doctor, ActorRatingMessage)
```

If you have an instance of a message and you want an entity:

```python
doctor = protopigeon.to_entity(doctor_message, Actor)
```

You can even use this to update an existing entity (this works vice-versa with existing message instances too):

```python
new_doctor = protopigeon.to_entity(doctor_no_rating, Actor)  # all fields but rating populated
protopigeon.to_entity(doctor_rating, new_doctor) # rating has been populated now, it's a complete entity.
```

Composing Messages
------------------

If you have two or more messages classes that you'd like to combine into one message, we can do that too.

```python
class Origin(Message)
    year = IntegerField(1)
    location = StringField(2)

class Traveler(Message):
    name = StringField(1)
    species = StringField(1)

class Tag(Message)
    urlsafe = StringField(1)

TravelerWithOriginAndTag = protopigeon.compose(Origin, Destination, Tag)

instance = TravelerWithOriginAndTag(
    name='The Doctor',
    year=2013,
    location='Gallifrey'
    species='Time Lord',
    urlsafe='the_doctor'
)
```

Things That Don't Work
======================

At the moment, I do not have a clever solution for supporting computed properties. I may take the approach seen in the endpoints-proto-datastore and add a TypedComputedProperty. However, my goal was to not modify any Model classes if I didn't absolutely have to. I'm open to suggestions on this.

In the meantime it's pretty easy to fill in the data yourslf using the above method of composing messages.


Installation
============

You can install easily with pip:

    pip install --target lib protopigeon


Contributing
============

I graciously accept bugs and pull requests.


License
=======

Apache License, Version 2.0


Thanks
======

Special thanks to Danny Hermes and his [endpoints-proto-datastore](https://github.com/GoogleCloudPlatform/endpoints-proto-datastore) library, which helped me figure out a few quirky bits of ndb-to-message mapping. It's a much more comprehensive library and great if you want a more direct and magical approach to integrating protorpc, ndb, and endpoints.
