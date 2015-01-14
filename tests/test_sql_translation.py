from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, Unicode, Boolean
from ferrisnose import AppEngineTest
from protopigeon import translators


Engine = create_engine('sqlite:///:memory:')
Base = declarative_base()


class Example(Base):
    __tablename__ = 'example'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(255))
    bool = Column(Boolean)


class TestSqlTranslations(AppEngineTest):
    def test_model_message(self):
        Msg = translators.model_message(Example)

        fields = dir(Msg)

        for column in Example.__table__.columns:
            assert column.name in fields

    def test_to_and_from(self):
        Msg = translators.model_message(Example)
        item = Example()
        item.id = 12
        item.name = 'Peter Capaldi'
        item.bool = True

        msg = translators.to_message(item, Msg)

        assert msg.id == item.id
        assert msg.name == item.name
        assert msg.bool == item.bool

        new_item = translators.to_model(msg, Example)

        assert new_item.id == item.id
        assert new_item.name == item.name
        assert new_item.bool == item.bool

        msg.id = 13
        overwrite_item = translators.to_model(msg, new_item)

        assert overwrite_item.id == 13
        assert overwrite_item.name == new_item.name
        assert overwrite_item.bool == new_item.bool
