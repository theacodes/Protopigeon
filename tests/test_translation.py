from ferrisnose import AppEngineTest
from google.appengine.ext import ndb
import protopigeon
import datetime


class InnerModel(ndb.Model):
    one = ndb.StringProperty()
    two = ndb.IntegerProperty()


class MessageModelTest(ndb.Model):
    string = ndb.StringProperty()
    repeatedString = ndb.StringProperty(repeated=True)
    text = ndb.TextProperty()
    repeatedText = ndb.TextProperty(repeated=True)
    blob = ndb.BlobProperty()
    repeatedBlob = ndb.BlobProperty(repeated=True)
    keyProp = ndb.KeyProperty()
    repeatedKey = ndb.KeyProperty(repeated=True)
    boolean = ndb.BooleanProperty()
    repeatedBoolean = ndb.BooleanProperty(repeated=True)
    integer = ndb.IntegerProperty()
    repeatedInteger = ndb.IntegerProperty(repeated=True)
    float = ndb.FloatProperty()
    repeatedFloat = ndb.FloatProperty(repeated=True)
    datetime = ndb.DateTimeProperty()
    repeatedDatetime = ndb.DateTimeProperty(repeated=True)
    time = ndb.TimeProperty()
    date = ndb.DateProperty()
    geopt = ndb.GeoPtProperty()
    repeatedGeopt = ndb.GeoPtProperty(repeated=True)
    blobkey = ndb.BlobKeyProperty()
    repeatedBlobkey = ndb.BlobKeyProperty(repeated=True)
    structured = ndb.StructuredProperty(InnerModel)
    repeatedStructured = ndb.StructuredProperty(InnerModel, repeated=True)


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
            repeatedString=['a', 'b', 'c'],
            keyProp=ndb.Key('Moew', 'Test'),
            repeatedKey=[ndb.Key('One', 'Cat'), ndb.Key('Two', 'Cat')],
            text='a',
            repeatedText=['a', 'b', 'c'],
            blob='abc',
            repeatedBlob=['abc', 'abc', '123'],
            boolean=True,
            repeatedBoolean=[False, True, False],
            integer=5,
            repeatedInteger=[1, 2, 3, 4, 5],
            float=3.14,
            repeatedFloat=[3.14, 1.23, 10.4],
            datetime=datetime.datetime.utcnow(),
            date=datetime.date.today(),
            time=datetime.datetime.utcnow().time(),
            repeatedDatetime=[datetime.datetime.utcnow(), datetime.datetime.now()],
            geopt=ndb.GeoPt(5, 5),
            repeatedGeopt=[ndb.GeoPt(5, 7), ndb.GeoPt(7, 8)],
            blobkey=ndb.BlobKey('oEFRyChdYLJbRk6cKXuniZfFtHct1wzDcnvVSgay91N7SoOCWTAWbDU8YcwQQbdn'),
            repeatedBlobkey=[ndb.BlobKey('oEFRyChdYLJbRk6cKXuniZfFtHct1wzDcnvVSgay91N7SoOCWTAWbDU8YcwQQbdn'), ndb.BlobKey('vQHMoSU5zK2zBxMA_fcP7A==')],
            structured=InnerModel(one='One', two=2),
            repeatedStructured=[InnerModel(one='One', two=2), InnerModel(one='Name', two=1)]
        )

        widget.put()

        return WidgetMessage, widget

    def test_to_message(self):
        WidgetMessage, widget = self.make_test_model()

        message = protopigeon.to_message(widget, WidgetMessage)

        assert message.string == widget.string
        assert message.repeatedString == widget.repeatedString
        assert message.text == widget.text
        assert message.repeatedText == widget.repeatedText
        assert message.blob == widget.blob
        assert message.repeatedBlob == widget.repeatedBlob
        assert message.boolean == widget.boolean
        assert message.repeatedBoolean == widget.repeatedBoolean
        assert message.integer == widget.integer
        assert message.repeatedInteger == widget.repeatedInteger
        assert message.float == widget.float
        assert message.repeatedFloat == widget.repeatedFloat
        assert message.keyProp == widget.keyProp.urlsafe()
        assert len(message.repeatedKey) == 2
        assert message.repeatedKey[0] == widget.repeatedKey[0].urlsafe()
        assert message.datetime.year == widget.datetime.year
        assert message.datetime.month == widget.datetime.month
        assert message.datetime.day == widget.datetime.day
        assert message.datetime.hour == widget.datetime.hour
        assert message.datetime.minute == widget.datetime.minute
        assert len(message.repeatedDatetime) == 2
        assert message.repeatedDatetime[0].year == widget.repeatedDatetime[0].year
        assert message.geopt.lat == widget.geopt.lat
        assert message.geopt.lon == widget.geopt.lon
        assert len(message.repeatedGeopt) == 2
        assert message.repeatedGeopt[0].lat == widget.repeatedGeopt[0].lat
        assert message.blobkey == str(widget.blobkey)
        assert message.repeatedBlobkey[1] == str(widget.repeatedBlobkey[1])
        assert message.structured.one == widget.structured.one
        assert message.structured.two == widget.structured.two
        assert message.repeatedStructured[0].one == widget.repeatedStructured[0].one
        assert message.itemId == widget.key.urlsafe()

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

        assert widget.repeatedString
        assert widget.string == 'meow'

        widget = protopigeon.to_entity(msg, widget)

        assert not widget.repeatedString
