from protorpc import messages


class TimeMessage(messages.Message):
    hour = messages.IntegerField(1)
    minute = messages.IntegerField(2)
    second = messages.IntegerField(3)
    microsecond = messages.IntegerField(4)
    time_zone_offset = messages.IntegerField(5)


class DateMessage(messages.Message):
    year = messages.IntegerField(1)
    month = messages.IntegerField(2)
    day = messages.IntegerField(3)


class UserMessage(messages.Message):
    email = messages.StringField(1)
    user_id = messages.StringField(2)
    nickname = messages.StringField(3)


class GeoPtMessage(messages.Message):
    lat = messages.FloatField(1)
    lon = messages.FloatField(2)
