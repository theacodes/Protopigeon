from ferrisnose import AppEngineTest
from google.appengine.ext import ndb
import protopigeon
import datetime


class InnerModel(ndb.Model):
    one = ndb.StringProperty()
    two = ndb.IntegerProperty()


class MessageModelTest(ndb.Model):
    string = ndb.StringProperty()
    repeated_string = ndb.StringProperty(repeated=True)
    text = ndb.TextProperty()
    repeated_text = ndb.TextProperty(repeated=True)
    blob = ndb.BlobProperty()
    repeated_blob = ndb.BlobProperty(repeated=True)
    key_prop = ndb.KeyProperty()
    repeated_key = ndb.KeyProperty(repeated=True)
    boolean = ndb.BooleanProperty()
    repeated_boolean = ndb.BooleanProperty(repeated=True)
    integer = ndb.IntegerProperty()
    repeated_integer = ndb.IntegerProperty(repeated=True)
    float = ndb.FloatProperty()
    repeated_float = ndb.FloatProperty(repeated=True)
    datetime = ndb.DateTimeProperty()
    repeated_datetime = ndb.DateTimeProperty(repeated=True)
    time = ndb.TimeProperty()
    date = ndb.DateProperty()
    geopt = ndb.GeoPtProperty()
    repeated_geopt = ndb.GeoPtProperty(repeated=True)
    blobkey = ndb.BlobKeyProperty()
    repeated_blobkey = ndb.BlobKeyProperty(repeated=True)
    structured = ndb.StructuredProperty(InnerModel)
    repeated_structured = ndb.StructuredProperty(InnerModel, repeated=True)


class TestTranslation(AppEngineTest):
    def test_model_message(self):
        WidgetMessage = protopigeon.model_message(MessageModelTest)

        properties = MessageModelTest._properties.keys()
        fields = dir(WidgetMessage)

        for prop in properties:
            assert prop in fields

    def make_test_model(self):
        WidgetMessage = protopigeon.model_message(MessageModelTest)

        widget = MessageModelTest(
            string='a',
            repeated_string=['a', 'b', 'c'],
            key_prop=ndb.Key('Moew', 'Test'),
            repeated_key=[ndb.Key('One', 'Cat'), ndb.Key('Two', 'Cat')],
            text='a',
            repeated_text=['a', 'b', 'c'],
            blob='abc',
            repeated_blob=['abc', 'abc', '123'],
            boolean=True,
            repeated_boolean=[False, True, False],
            integer=5,
            repeated_integer=[1, 2, 3, 4, 5],
            float=3.14,
            repeated_float=[3.14, 1.23, 10.4],
            datetime=datetime.datetime.utcnow(),
            date=datetime.date.today(),
            time=datetime.datetime.utcnow().time(),
            repeated_datetime=[datetime.datetime.utcnow(), datetime.datetime.now()],
            geopt=ndb.GeoPt(5, 5),
            repeated_geopt=[ndb.GeoPt(5, 7), ndb.GeoPt(7, 8)],
            blobkey=ndb.BlobKey('oEFRyChdYLJbRk6cKXuniZfFtHct1wzDcnvVSgay91N7SoOCWTAWbDU8YcwQQbdn'),
            repeated_blobkey=[ndb.BlobKey('oEFRyChdYLJbRk6cKXuniZfFtHct1wzDcnvVSgay91N7SoOCWTAWbDU8YcwQQbdn'), ndb.BlobKey('vQHMoSU5zK2zBxMA_fcP7A==')],
            structured=InnerModel(one='One', two=2),
            repeated_structured=[InnerModel(one='One', two=2), InnerModel(one='Name', two=1)]
        )

        widget.put()

        return WidgetMessage, widget

    def test_to_message(self):
        WidgetMessage, widget = self.make_test_model()

        message = protopigeon.to_message(widget, WidgetMessage)

        assert message.string == widget.string
        assert message.repeated_string == widget.repeated_string
        assert message.text == widget.text
        assert message.repeated_text == widget.repeated_text
        assert message.blob == widget.blob
        assert message.repeated_blob == widget.repeated_blob
        assert message.boolean == widget.boolean
        assert message.repeated_boolean == widget.repeated_boolean
        assert message.integer == widget.integer
        assert message.repeated_integer == widget.repeated_integer
        assert message.float == widget.float
        assert message.repeated_float == widget.repeated_float
        assert message.key_prop.urlsafe == widget.key_prop.urlsafe()
        assert len(message.repeated_key) == 2
        assert message.repeated_key[0].urlsafe == widget.repeated_key[0].urlsafe()
        assert message.datetime.year == widget.datetime.year
        assert message.datetime.month == widget.datetime.month
        assert message.datetime.day == widget.datetime.day
        assert message.datetime.hour == widget.datetime.hour
        assert message.datetime.minute == widget.datetime.minute
        assert len(message.repeated_datetime) == 2
        assert message.repeated_datetime[0].year == widget.repeated_datetime[0].year
        assert message.geopt.lat == widget.geopt.lat
        assert message.geopt.lon == widget.geopt.lon
        assert len(message.repeated_geopt) == 2
        assert message.repeated_geopt[0].lat == widget.repeated_geopt[0].lat
        assert message.blobkey == str(widget.blobkey)
        assert message.repeated_blobkey[1] == str(widget.repeated_blobkey[1])
        assert message.structured.one == widget.structured.one
        assert message.structured.two == widget.structured.two
        assert message.repeated_structured[0].one == widget.repeated_structured[0].one
        assert message.datastore_key.urlsafe == widget.key.urlsafe()

        # Updating an existing instance
        message = protopigeon.to_message(widget, WidgetMessage(string='Meow'))

        assert message.string == widget.string
        assert message.integer == widget.integer

    def test_to_model(self):
        WidgetMessage, widget = self.make_test_model()

        # Simple test
        message = WidgetMessage(string='Dalek', integer=1)

        simple_widget = protopigeon.to_entity(message, MessageModelTest)

        assert message.string == simple_widget.string
        assert message.integer == simple_widget.integer

        # Updating an existing instance
        simple_widget = protopigeon.to_entity(message, MessageModelTest(string='Meow'))

        assert message.string == simple_widget.string
        assert message.integer == simple_widget.integer

        # Full serialization/deserialization comparion test.
        message = protopigeon.to_message(widget, WidgetMessage)
        print message
        deserialized = protopigeon.to_entity(message, MessageModelTest)

        for prop in MessageModelTest._properties.keys():
            assert getattr(deserialized, prop) == getattr(widget, prop)

        assert deserialized.key.urlsafe() == widget.key.urlsafe()

    def test_empty_values(self):
        WidgetMessage, widget = self.make_test_model()

        empty_widget = MessageModelTest()
        message = protopigeon.to_message(empty_widget, WidgetMessage)

        for prop in MessageModelTest._properties.keys():
            assert not getattr(message, prop)

        empty_message = WidgetMessage()
        widget = protopigeon.to_entity(empty_message, MessageModelTest)

        for field in WidgetMessage.all_fields():
            assert not getattr(widget, prop)

    def test_partials(self):
        WidgetMessage, widget = self.make_test_model()

        msg = WidgetMessage(string='meow')
        widget = protopigeon.to_entity(msg, widget, only=('string',))

        assert widget.repeated_string
        assert widget.string == 'meow'

        widget = protopigeon.to_entity(msg, widget)

        assert not widget.repeated_string
