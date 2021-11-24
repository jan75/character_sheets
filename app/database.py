import logging
import sqlite3
from datetime import date

from flask import Response, make_response
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, scoped_session

logger = logging.getLogger(__name__)

LIMIT = 1000


class ScopedDBConnection:
    _engine = None
    _scoped_session = None

    @property
    def session(self):
        if self._scoped_session:
            return self._scoped_session
        else:
            logger.info('Creating session')
            if not self._engine:
                raise RuntimeError(
                    'Can\'t create session, please connect to a database first')

            self._scoped_session = scoped_session(sessionmaker(bind=self._engine, autocommit=False, autoflush=False))
            return self._scoped_session

    def _fk_pragma_on_connect(connection, cursor, con_record):
        logger.debug('engine connect event: %s, %s, %s', connection, cursor, con_record)
        if isinstance(cursor, sqlite3.Connection):
            cursor.execute('PRAGMA foreign_keys=ON')

    def _init_db(self):
        from models.series import Series
        from models.entrytype import EntryType
        from models.entry import Entry
        from models.character import Character
        from models.character_info import CharacterInfo

        Series.init_entity(self.session, self._engine)
        EntryType.init_entity(self.session, self._engine)
        Entry.init_entity(self.session, self._engine)
        Character.init_entity(self.session, self._engine)
        CharacterInfo.init_entity(self.session, self._engine)

    def connect_db(self, db_connection_string: str):
        logger.info('Connecting to database %s', db_connection_string)
        if self._engine:
            raise RuntimeError('Already connected to database')

        self._engine = create_engine(db_connection_string)
        self._init_db()

        event.listen(self._engine, 'connect', self._fk_pragma_on_connect)
        #event.listen(Pool, 'connect', self._fk_pragma_on_connect)


db = ScopedDBConnection()


def _add_and_commit(obj):
    db.session.add(obj)
    db.session.commit()

    return obj


def generate_test_data() -> Response:
    from models.entrytype import EntryType
    from models.character import Character
    from models.entry import Entry
    from models.series import Series
    from models.character_info import CharacterInfo

    book_type = _add_and_commit(EntryType('Book'))
    episode_type = _add_and_commit(EntryType('Episode'))
    movie_type = _add_and_commit(EntryType('Movie'))

    riyria_series = _add_and_commit(Series('Riyria Revelations'))
    dune_series = _add_and_commit(Series('Dune'))

    theft_of_swords_entry = _add_and_commit(
        Entry('Theft of Swords', date(2011, 1, 1), 1, book_type.id, riyria_series.id))
    rise_of_empire_entry = _add_and_commit(Entry('Rise of Empire', date(2011, 1, 1), 2, book_type.id, riyria_series.id))
    heir_of_novron_entry = _add_and_commit(Entry('Heir of Novron', date(2012, 1, 1), 3, book_type.id, riyria_series.id))
    dune_entry = _add_and_commit(Entry('Dune', date(1965, 1, 1), book_type.id, 1, dune_series.id))
    dune_messiah_entry = _add_and_commit(Entry('Dune Messiah', date(1969, 1, 1), 2, book_type.id, dune_series.id))
    children_of_dune_entry = _add_and_commit(
        Entry('Children of Dune', date(1676, 1, 1), 3, book_type.id, dune_series.id))

    hadrian_char = _add_and_commit(Character('Hadrian', riyria_series.id, theft_of_swords_entry.id))
    royce_char = _add_and_commit(Character('Royce', riyria_series.id, theft_of_swords_entry.id))

    hadrian_info1 = _add_and_commit(CharacterInfo('Swordmaster, friend of Royce (part of Riyria)', theft_of_swords_entry.id, hadrian_char.id))
    hadrian_info2 = _add_and_commit(CharacterInfo('Guardian of Novron\'s Heir', heir_of_novron_entry.id, hadrian_char.id))
    royce_info1 = _add_and_commit(CharacterInfo('Thief, friend of Hadrian (part of Riyria)', theft_of_swords_entry.id, royce_char.id))

    return make_response('', 201)
