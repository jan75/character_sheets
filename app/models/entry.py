import logging
from typing import Dict, List

from marshmallow import Schema, fields, validates_schema, ValidationError
from sqlalchemy import select, ForeignKey, Column, Integer, String, Date, and_, update, event
from sqlalchemy.orm import relationship, declarative_base, validates
from sqlalchemy.sql.functions import count, func

from database import db, LIMIT
from models.base import RESTModel
from models.entrytype import EntryType
from models.series import Series

logger = logging.getLogger(__name__)

base = declarative_base()


class EntrySchema(Schema):
    id = fields.Int()
    name = fields.Str(required=True)
    date = fields.Date(required=True)
    order_in_series = fields.Int(required=True)
    entrytype_id = fields.Int(required=True)
    series_id = fields.Int(required=True)


class EntrySearchSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    date = fields.Date()
    order_in_series = fields.Int()
    entrytype_id = fields.Int()
    series_id = fields.Int()

    @validates_schema
    def check_presence(self, data, **kwargs):
        if not any(key in data for key in ('id', 'name', 'date', 'order_in_series', 'entrytype_id', 'series_id')):
            raise ValidationError('Either id, name, date, order_in_series, entrytype_id or series_id must be set')


class Entry(RESTModel, base):
    __tablename__ = 'entries'
    id = Column(Integer, primary_key=True)
    name = Column(String(240), nullable=False)
    date = Column(Date, nullable=False)
    _order_in_series = Column('order_in_series', Integer, nullable=False)
    entrytype_id = Column(Integer, ForeignKey(EntryType.id), nullable=False)
    series_id = Column(Integer, ForeignKey(Series.id), nullable=False)

    entrytype = relationship(EntryType, foreign_keys='Entry.entrytype_id')
    series = relationship(Series, foreign_keys='Entry.series_id')

    schema = EntrySchema()

    def __init__(self, name: str, date: date, order_in_series: int, entrytype_id: int, series_id: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name
        self.date = date
        self.entrytype_id = entrytype_id
        self.series_id = series_id

        self.order_in_series = order_in_series

    @staticmethod
    def init_entity(session, engine):
        base.metadata.create_all(bind=engine)

        event.listen(session, 'before_flush', Entry.handle_before_flush)

    @staticmethod
    def handle_before_flush(session, flush_context, instances):
        logger.debug('_handle_before_flush session: %s, flush_context: %s, instances: %s', session, flush_context,
                     instances)
        for obj in session.deleted:
            if isinstance(obj, Entry):
                logger.info('Deleting entry, update other entries order_in_series values')
                query = update(Entry) \
                    .where(
                    and_(
                        Entry.id != obj.id,
                        Entry.series_id == obj.series_id,
                        Entry._order_in_series > obj._order_in_series
                    )
                ) \
                    .values(
                    {
                        Entry._order_in_series: Entry._order_in_series - 1
                    }
                )
                logger.debug('query: %s', query)
                db.session.execute(query)

    def __str__(self):
        return f'Entry ({self.id}): {self.name} {self.date} {self.order_in_series}'

    def __eq__(self, other: 'Entry'):
        return self.name == other.name \
               and self.date == other.date \
               and self.order_in_series == other.order_in_series \
               and self.entrytype_id == other.entrytype_id \
               and self.series_id == other.series_id

    def __gt__(self, other: 'Entry'):
        return self.order_in_series > other.order_in_series

    @property
    def order_in_series(self):
        return self._order_in_series

    @order_in_series.deleter
    def order_in_series(self):
        raise RuntimeError('order_in_series is a non-optional value and can\'t be deleted!')

    @order_in_series.setter
    def order_in_series(self, value):
        """
        Validates and sets order_in_series value. Additionally adjusts order_in_series value in other Entries belonging to the
        same series. The field is not an absolute order of an entry but a relative ordering of the given entries in
        the application (for example while "Harry Potter and the Goblet of Fire" is the fourth novel in the Harry Potter
        series, it's order_in_series in this application must be 1 if it's the only Harry Potter novel in this
        application). Therefore, the order is gapless.

        The following conditions apply:
        - If value is None a ValueError is thrown
        - If the value is <= 0 a ValueError is thrown
        - If the value is > `max(order_in_series) + 1` among Entries belonging to the same series a ValueError is thrown.
        This also applies if the Entry is the first Entry belonging to a series and it's order_in_series is not 1.
        - If the value is `0 < value <= max(order_in_series) + 1` the order_in_series values of the other Entries
        belonging to the same series are adjusted accordingly (i.E. + 1 or - 1)

        :param key: Key of updated field
        :param value: Value of 'order_in_series'
        :return: value or ValueError in case of invalid given value
        """
        if not value:
            raise ValueError('order_in_series can\'t be None')

        if value <= 0:
            raise ValueError('order_in_series can\'t be <= 0')

        query = select(func.max(Entry._order_in_series)) \
            .where(
            and_(
                Entry.id != self.id,
                Entry.series_id == self.series_id
            )
        )
        logger.debug('max query: %s', query)
        res = db.session.execute(query).first()
        max_order_in_series = res[0]
        logger.debug('max_order_in_series: %s', max_order_in_series)
        if not max_order_in_series:
            max_order_in_series = 0
        logger.debug('max_order_in_series: %s', max_order_in_series)

        if value > max_order_in_series + 1:
            raise ValueError('order_in_series must be between 1 and {}'.format(max_order_in_series + 1))

        # insert new entry
        if not self._order_in_series:
            query = update(Entry) \
                .where(
                and_(
                    Entry.id != self.id,
                    Entry.series_id == self.series_id,
                    Entry._order_in_series >= value
                )
            ) \
                .values(
                {
                    Entry._order_in_series: Entry._order_in_series + 1
                }
            )
            logger.debug('query: %s', query)
            db.session.execute(query)

            self._order_in_series = value
            return

        # update values between old and new value
        if value > self._order_in_series:
            query = update(Entry) \
                .where(
                and_(
                    Entry.id != self.id,
                    Entry.series_id == self.series_id,
                    Entry._order_in_series > self._order_in_series,
                    Entry._order_in_series <= value
                )
            ) \
                .values(
                {
                    Entry._order_in_series: Entry._order_in_series - 1
                }
            )
            logger.debug('query: %s', query)
            db.session.execute(query)
            self._order_in_series = value
            return
        elif value < self._order_in_series:
            query = update(Entry) \
                .where(
                and_(
                    Entry.id != self.id,
                    Entry.series_id == self.series_id,
                    Entry._order_in_series < self._order_in_series,
                    Entry._order_in_series >= value
                )
            ) \
                .values(
                {
                    Entry._order_in_series: Entry._order_in_series + 1
                }
            )
            logger.debug('query: %s', query)
            db.session.execute(query)
            self._order_in_series = value
            return

    @validates('_order_in_series', include_removes=True)
    def validate_order_in_series(self, key, value, is_remove):
        logger.debug('validate_order_in_series key: %s, value: %s, is_remove: %s', key, value, is_remove)
        return value

    @staticmethod
    def query_by_id(id: int = None, offset: int = 0, limit: int = LIMIT) -> (List['Entry'], int) or (None, None):
        logger.debug('Entry.query(%s, %d)', id, offset)

        if limit > LIMIT:
            logger.debug('Value for limit is too high, using system LIMIT (%d)', LIMIT)
            limit = LIMIT

        try:
            if id:
                row_count_query = select(count(Entry.id)).filter_by(id=id)
                query = select(Entry).limit(limit).filter_by(id=id)
            else:
                row_count_query = select(count(Entry.id))
                query = select(Entry).limit(limit).offset(offset)

            result_rows = db.session.execute(query).all()
            result_row_count = db.session.execute(row_count_query).first()
            return [row['Entry'] for row in result_rows], result_row_count[0]
        except Exception as e:
            logger.error('Could not query entries %s', e)
            return None, None

    @staticmethod
    def query_by_fields(fields: Dict, offset: int = 0, limit: int = LIMIT) -> (List['Entry'], int) or (None, None):
        logger.debug('Entry.query_by_fields(%s, %d, %d)', fields, offset, limit)

        if 'id' in fields:
            return Entry.query_by_id(fields['id'], offset, limit)

        filter_list = []
        for key, value in fields.items():
            if key == Entry.name.key:
                filter_list.append(Entry.name.contains(value))
            elif key == Entry.date.key:
                filter_list.append(Entry.date == value)
            elif key == Entry.entrytype_id.key:
                filter_list.append(Entry.entrytype_id == value)
            elif key == Entry.series_id.key:
                filter_list.append(Entry.series_id == value)
            else:
                logger.warning('Invalid filter parameter')
                return None, None

        row_count_query = select(count(Entry.id)).filter(*filter_list)
        query = select(Entry).limit(limit).offset(offset).filter(*filter_list)

        try:
            result_rows = db.session.execute(query).all()
            result_row_count = db.session.execute(row_count_query).first()
            return [row['Entry'] for row in result_rows], result_row_count[0]
        except Exception as e:
            logger.error('Could not query entries %s', e)
            return None, None

    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'name': self.name,
            'date': self.date.strftime('%Y-%m-%d'),
            'order_in_series': self.order_in_series,
            'entrytype': self.entrytype.to_dict(),
            'series': self.series.to_dict()
        }

    @staticmethod
    def from_dict(data: Dict) -> 'Entry':
        try:
            entry = Entry(data['name'], data['date'], data['order_in_series'], data['entrytype_id'], data['series_id'])
            return entry
        except KeyError as e:
            logger.error('Key error when trying to create object instance', e)
            return None

    def update(self, data: Dict) -> 'Entry':
        try:
            self.name = data['name']
            self.date = data['date']
            self.order_in_series = data['order_in_series']
            self.entrytype_id = data['entrytype_id']
            self.series_id = data['series_id']
            return self
        except KeyError as e:
            logger.error('Key error when trying to update entry', e)
            return None
