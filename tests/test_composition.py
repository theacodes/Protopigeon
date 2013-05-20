from protorpc.messages import Message, IntegerField, StringField
import protopigeon


class MessageOne(Message):
    one = IntegerField(1)
    two = IntegerField(2)


class MessageTwo(Message):
    three = StringField(1)
    four = StringField(2)


def test():
    ComposedMessage = protopigeon.compose(MessageOne, MessageTwo)

    assert hasattr(ComposedMessage, 'one')
    assert hasattr(ComposedMessage, 'two')
    assert hasattr(ComposedMessage, 'three')
    assert hasattr(ComposedMessage, 'four')

    # Make sure these fields weren't modified
    assert MessageOne.one.number == 1
    assert MessageOne.two.number == 2
    assert MessageTwo.three.number == 1
    assert MessageTwo.four.number == 2

    instance = ComposedMessage(
        one=1,
        two=2,
        three='three',
        four='four')

    assert instance
