ProtoPigeon
===========

ProtoPigeon provides utilities for generating protorpc Messages from ndb Models. It can generate Message classes from Models, translate entities to message instances and vice-verse. It can also compose multiple message classes together.


Usage
=====

Generating Message classes from a Model
---------------------------------------

If you have a model:

    class Actor(ndb.Model)
        name = ndb.StringProperty()
        shows = ndb.StringProperty(repeated=True)
        rating = ndb.IntegerProperty()

You can easily generate a message class:

    ActorMessage = protopigeon.model_message(Actor)

You can also exclude fields, or specify which particular fields:

    ActorWithoutRatingMessage = protopigeon.model_message(Action, exclude=('rating',))
    ActorRatingMessage = protopigeon.model_message(Action, only=('rating',))


Translating between Entities and Messages
-----------------------------------------

Playing on the previous example, if you have an entity (an instance of a Model) and want to make a message:

    doctor = Actor(name='Matt Smith', shows=('Doctor Who', 'Moses Jones'), rating=90)

    doctor_message = protopigeon.to_message(doctor, ActorMessage)
    doctor_no_rating = protopigeon.to_message(doctor, ActorWithoutRatingMessage)
    doctor_rating = protopigeon.to_message(doctor, ActorRatingMessage)

If you have an instance of a message and you want an entity:

    doctor = protopigeon.to_entity(doctor_message, Actor)

You can even use this to update an existing entity (this works vice-versa with existing message instances too):

    new_doctor = protopigeon.to_entity(doctor_no_rating, Actor)  # all fields but rating populated
    protopigeon.to_entity(doctor_rating, new_doctor) # rating has been populated now, it's a complete entity.


Composing Messages
------------------

If you have two or more messages classes that you'd like to combine into one message, we can do that too.

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


Installation
============

ProtoPigeon is intended to be used with App Engine projects. To use, simply copy the protopigeon folder into the root of your App Engine project, or if you have a 3rd-party package directory setup, in there. That's it!
