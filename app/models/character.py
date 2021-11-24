import logging
from typing import Dict, List

from marshmallow import Schema, fields, validates_schema, ValidationError
from sqlalchemy import ForeignKey, Column, Integer, String, select
from sqlalchemy.orm import Query, relationship, declarative_base
from sqlalchemy.sql.functions import count

from database import LIMIT, db
from models.base import RESTModel
from models.entry import Entry
from models.series import Series

logger = logging.getLogger(__name__)

base = declarative_base()


class CharacterSchema(Schema):
    id = fields.Int()
    name = fields.Str(required=True)
    series_id = fields.Int(required=True)
    occurs_first_in_entry_id = fields.Int(required=True)


class CharacterSearchSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    series_id = fields.Date()
    occurs_first_in_entry_id = fields.Int()

    @validates_schema
    def check_presence(self, data, **kwargs):
        if not any(key in data for key in ('id', 'name', 'series_id', 'occurs_first_in_entry_id')):
            raise ValidationError('Either id, name, series_id or occurs_first_in_entry_id must be set')


class Character(RESTModel, base):
    __tablename__ = 'characters'
    id = Column(Integer, primary_key=True)
    name = Column(String(240), nullable=False)
    series_id = Column(Integer, ForeignKey(Series.id), nullable=False)
    occurs_first_in_entry_id = Column(Integer, ForeignKey(Entry.id), nullable=False)

    series = relationship(Series, foreign_keys='Character.series_id')
    occurs_first_in_entry = relationship(Entry, foreign_keys='Character.occurs_first_in_entry_id')

    schema = CharacterSchema()

    def __init__(self, name: str, series_id: int, occurs_first_in_entry_id: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name
        self.series_id = series_id
        self.occurs_first_in_entry_id = occurs_first_in_entry_id

    def __str__(self):
        return f'Character ({self.id}): {self.name}'

    @staticmethod
    def init_entity(session, engine):
        base.metadata.create_all(bind=engine)

    @staticmethod
    def query_by_id(id: int = None, offset: int = 0, limit: int = LIMIT) -> (List['Character'], int) or (None, None):
        logger.debug('Character.query(%s, %d)', id, offset)

        if limit > LIMIT:
            logger.info('Value for limit is too high, using system default LIMIT (%d)', LIMIT)
            limit = LIMIT

        try:
            if id:
                row_count_query = Query(count(Character.id)).filter_by(id=id)
                query = Query(Character).limit(limit).filter_by(id=id)
            else:
                row_count_query = Query(count(Character.id))
                query = Query(Character).limit(limit).offset(offset)

            result_rows = db.session.execute(query).all()
            result_row_count = db.session.execute(row_count_query).first()
            return [row['Character'] for row in result_rows], result_row_count[0]
        except Exception as e:
            logger.error('Could not query characters %s', e)
            return None, None

    @staticmethod
    def query_by_fields(fields: Dict, offset: int = 0, limit: int = LIMIT) -> (List['Character'], int) or (
    None, None):
        logger.debug('Character.query_by_fields(%s, %d, %d)', fields, offset, limit)

        if 'id' in fields:
            return Character.query_by_id(fields['id'], offset, limit)

        filter_list = []
        for key, value in fields.items():
            if key == Character.name.key:
                filter_list.append(Character.name.contains(value))
            elif key == Character.series_id.key:
                filter_list.append(Character.series_id == value)
            elif key == Character.occurs_first_in_entry_id.key:
                filter_list.append(Character.occurs_first_in_entry_id == value)
            else:
                logger.warning('Invalid filter parameter')
                return None, None

        row_count_query = select(count(Character.id)).filter(*filter_list)
        query = select(Character).limit(limit).offset(offset).filter(*filter_list)

        try:
            result_rows = db.session.execute(query).all()
            result_row_count = db.session.execute(row_count_query).first()
            return [row['Character'] for row in result_rows], result_row_count[0]
        except Exception as e:
            logger.error('Could not query characters %s', e)
            return None, None

    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'name': self.name,
            'series': self.series.to_dict(),
            'occursFirstInEntryId': self.occurs_first_in_entry_id
        }

    @staticmethod
    def from_dict(data: Dict) -> 'Character':
        try:
            character = Character(data['name'], data['series_id'], data['occurs_first_in_entry_id'])
            return character
        except KeyError as e:
            logger.error('Key error when trying to create object instance', e)
            return None

    def update(self, data: Dict) -> 'Character':
        try:
            self.name = data['name']
            self.series_id = data['series_id']
            self.occurs_first_in_entry_id = data['occurs_first_in_entry_id']
            return self
        except KeyError as e:
            logger.error('Key error when trying to update character', e)
            return None
