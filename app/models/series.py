import logging
from typing import Dict, List

from marshmallow import Schema, fields, validates_schema, ValidationError
from sqlalchemy import select, Column, Integer, String
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql.functions import count

from database import LIMIT, db
from models.base import RESTModel

logger = logging.getLogger(__name__)

base = declarative_base()


class SeriesSchema(Schema):
    id = fields.Int()
    name = fields.Str(required=True)


class SeriesSearchSchema(Schema):
    id = fields.Int()
    name = fields.Str()

    @validates_schema
    def check_presence(self, data, **kwargs):
        if not any(key in data for key in ('id', 'name')):
            raise ValidationError('Either id or name must be set')


class Series(RESTModel, base):
    __tablename__ = 'series'
    id = Column(Integer, primary_key=True)
    name = Column(String(240), nullable=False, unique=True)

    schema = SeriesSchema()

    def __init__(self, name: str = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name

    def __str__(self):
        return f'Series ({self.id}): {self.name}'

    @staticmethod
    def init_entity(session, engine):
        base.metadata.create_all(bind=engine)

    @staticmethod
    def query_by_id(id: int = None, offset: int = 0, limit: int = LIMIT) -> (List['Series'], int) or (None, None):
        logger.debug('Series.query(%s, %d)', id, offset)

        if limit > LIMIT:
            logger.info('Value for limit is too high, using system default LIMIT (%d)', LIMIT)
            limit = LIMIT

        try:
            if id:
                row_count_query = select(count(Series.id)).filter_by(id=id)
                query = select(Series).limit(limit).filter_by(id=id)
            else:
                row_count_query = select(count(Series.id))
                query = select(Series).limit(limit).offset(offset)

            result = db.session.execute(query).all()
            result_row_count = db.session.execute(row_count_query).first()
            return [row['Series'] for row in result], result_row_count[0]
        except Exception as e:
            logger.error('Could not query series %s', e)
            return None, None

    @staticmethod
    def query_by_fields(fields: Dict, offset: int = 0, limit: int = LIMIT) -> (List['Series'], int) or (None, None):
        logger.debug('Series.query_by_fields(%s, %d, %d)', fields, offset, limit)

        if 'id' in fields:
            return Series.query_by_id(fields['id'], offset, limit)

        filter_list = []
        for key, value in fields.items():
            if key == Series.name.key:
                filter_list.append(Series.name.contains(value))
            else:
                logger.warning('Invalid filter parameter')
                return None, None

        row_count_query = select(count(Series.id)).filter(*filter_list)
        query = select(Series).limit(limit).offset(offset).filter(*filter_list)

        try:
            result_rows = db.session.execute(query).all()
            result_row_count = db.session.execute(row_count_query).first()
            return [row['Series'] for row in result_rows], result_row_count[0]
        except Exception as e:
            logger.error('Could not query series %s', e)
            return None, None

    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'name': self.name
        }

    @staticmethod
    def from_dict(data: Dict) -> 'Series':
        try:
            series = Series(data['name'])
            return series
        except KeyError as e:
            logger.error('Key error when trying to create object instance', e)
            return None

    def update(self, data: Dict) -> 'Series':
        try:
            self.name = data['name']
            return self
        except KeyError as e:
            logger.error('Key error when trying to update series', e)
            return None
