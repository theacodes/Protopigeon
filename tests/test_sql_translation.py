from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, Unicode
from ferrisnose import AppEngineTest
from protopigeon import sql_translators


Engine = create_engine('sqlite:///:memory:')
Base = declarative_base()


class Example(Base):
    __tablename__ = 'example'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode)


class TestSqlTranslations(AppEngineTest):
    def test_sanity(self):
        Msg = sql_translators.model_message(Example)

        fields = dir(Msg)

        for column in Example.__table__.columns:
            assert column.name in fields
