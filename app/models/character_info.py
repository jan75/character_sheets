import logging
from typing import Dict, List

from marshmallow import Schema, fields
from sqlalchemy import ForeignKey, Column, Integer, String
from sqlalchemy.orm import Query, relationship, declarative_base
from sqlalchemy.sql.functions import count

from database import LIMIT, db
from models.base import RESTModel
from models.character import Character
from models.entry import Entry

logger = logging.getLogger(__name__)

base = declarative_base()


class CharacterInfoSchema(Schema):
    id = fields.Int()
    text = fields.Str(required=True)
    entry_id = fields.Int(required=True, data_key='seriesId')
    character_id = fields.Int(required=True, data_key='characterId')


class CharacterInfo(RESTModel, base):
    __tablename__ = 'characterinfo'
    id = Column(Integer, primary_key=True)
    text = Column(String(240), nullable=False)
    entry_id = Column(Integer, ForeignKey(Entry.id), nullable=False)
    character_id = Column(Integer, ForeignKey(Character.id), nullable=False)

    entry = relationship(Entry, foreign_keys='CharacterInfo.entry_id')
    character = relationship(Character, foreign_keys='CharacterInfo.character_id')

    schema = CharacterInfoSchema()

    def __init__(self, text: str, entry_id: int, character_id: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.text = text
        self.entry_id = entry_id
        self.character_id = character_id

    def __str__(self):
        return f'CharacterInfo ({self.id}): {self.name}'

    @staticmethod
    def init_entity(session, engine):
        base.metadata.create_all(bind=engine)

    @staticmethod
    def query_by_id(id: int = None, offset: int = 0, limit: int = LIMIT) -> (List['Character'], int) or None:
        logger.debug('CharacterInfo.query(%s, %d)', id, offset)

        if limit > LIMIT:
            logger.info('Value for limit is too high, using system LIMIT (%d)', LIMIT)
            limit = LIMIT

        try:
            if id:
                row_count_query = Query(count(CharacterInfo.id)).filter_by(id=id)
                query = Query(CharacterInfo).limit(limit).filter_by(id=id)
            else:
                row_count_query = Query(count(CharacterInfo.id))
                query = Query(CharacterInfo).limit(limit).offset(offset)

            result_rows = db.session.execute(query).all()
            result_row_count = db.session.execute(row_count_query).first()
            return [row['CharacterInfo'] for row in result_rows], result_row_count[0]
        except Exception as e:
            logger.error('Could not query characterinfo %s', e)
            return None

    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'text': self.text,
            'entry': self.entry.to_dict(),
            'character': self.character.to_dict()
        }

    @staticmethod
    def from_dict(data: Dict) -> 'CharacterInfo':
        try:
            character = CharacterInfo(data['text'], data['entry_id'], data['character_id'])
            return character
        except KeyError as e:
            logger.error('Key error when trying to create object instance', e)
            return None

    def update(self, data: Dict) -> 'Character':
        try:
            self.text = data['text']
            self.entry_id = data['entry_id']
            self.character_id = data['character_id']
            return self
        except KeyError as e:
            logger.error('Key error when trying to update characterinfo %s', e)
            return None
