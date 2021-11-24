import logging
import os
import tempfile
import unittest
from datetime import date
from uuid import uuid4

from models.character import Character
from models.entry import Entry
from models.entrytype import EntryType
from models.series import Series

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ITDatabase(unittest.TestCase):
    tmp_db_file_path = None
    db = None
    env_patcher = None

    def _add_commit(self, obj):
        self.db.session.add(obj)
        self.db.session.commit()
        return obj

    @classmethod
    def setUpClass(cls):
        logger.info('Setting up ITDatabase class')

        cls.tmp_db_file_path = os.path.join(tempfile.gettempdir(), '{}-{}.db'.format(cls.__name__, uuid4()))
        db_connection_string = 'sqlite+pysqlite:///{}'.format(cls.tmp_db_file_path)

        # cls.env_patcher = mock.patch.dict(os.environ, {'DB_CONNECTION_STRING': db_connection_string})
        # cls.env_patcher.start()

        from database import db
        db.connect_db(db_connection_string)

        cls.db = db

    @classmethod
    def tearDownClass(cls):
        logger.info('Tearing down ITDatabase class')
        cls.db.session.close()
        # cls.env_patcher.stop()

        os.remove(cls.tmp_db_file_path)

    def tearDown(self):
        self.db.session.query(Entry).delete()
        self.db.session.commit()

        self.db.session.query(Series).delete()
        self.db.session.commit()

        self.db.session.query(EntryType).delete()
        self.db.session.commit()

        self.db.session.query(Character).delete()
        self.db.session.commit()

    def test_entry_ordering(self):
        series = self._add_commit(Series('test'))
        entrytype = self._add_commit(EntryType('book'))

        self.assertRaises(ValueError, Entry, 'invalid_entry1', date(2021, 1, 1), None, entrytype.id, series.id)
        self.assertRaises(ValueError, Entry, 'invalid_entry2', date(2021, 1, 1), -1, entrytype.id, series.id)

        entry1 = self._add_commit(Entry('entry1', date(2021, 1, 1), 1, entrytype.id, series.id))
        self.assertRaises(ValueError, setattr, entry1, 'order_in_series', None)
        self.assertEqual(1, entry1.order_in_series)
        self.assertRaises(ValueError, setattr, entry1, 'order_in_series', -1)
        self.assertEqual(1, entry1.order_in_series)

        self.assertRaises(ValueError, Entry, 'invalid_entry3', date(2021, 1, 1), 5, entrytype.id, series.id)

        entry2 = self._add_commit(Entry('entry2', date(2021, 1, 1), 2, entrytype.id, series.id))
        entry3 = self._add_commit(Entry('entry3', date(2021, 1, 1), 3, entrytype.id, series.id))

        self.assertEqual(1, entry1.order_in_series)
        self.assertEqual(2, entry2.order_in_series)
        self.assertEqual(3, entry3.order_in_series)

        entry4 = self._add_commit(Entry('entry4', date(2021, 1, 1), 1, entrytype.id, series.id))
        self.assertEqual(1, entry4.order_in_series)
        self.assertEqual(2, entry1.order_in_series)
        self.assertEqual(3, entry2.order_in_series)
        self.assertEqual(4, entry3.order_in_series)

        entry5 = self._add_commit(Entry('entry5', date(2021, 1, 1), 5, entrytype.id, series.id))

        # moving order down (higher)
        entry1.order_in_series = 4
        self.assertEqual(1, entry4.order_in_series)
        self.assertEqual(2, entry2.order_in_series)
        self.assertEqual(3, entry3.order_in_series)
        self.assertEqual(4, entry1.order_in_series)
        self.assertEqual(5, entry5.order_in_series)

        # moving order up (lower)
        entry1.order_in_series = 2
        self.assertEqual(1, entry4.order_in_series)
        self.assertEqual(2, entry1.order_in_series)
        self.assertEqual(3, entry2.order_in_series)
        self.assertEqual(4, entry3.order_in_series)
        self.assertEqual(5, entry5.order_in_series)

        entry5.order_in_series = 1
        self.assertEqual(1, entry5.order_in_series)
        self.assertEqual(2, entry4.order_in_series)
        self.assertEqual(3, entry1.order_in_series)
        self.assertEqual(4, entry2.order_in_series)
        self.assertEqual(5, entry3.order_in_series)

        # nothing should change
        entry2.order_in_series = 4
        self.assertEqual(1, entry5.order_in_series)
        self.assertEqual(2, entry4.order_in_series)
        self.assertEqual(3, entry1.order_in_series)
        self.assertEqual(4, entry2.order_in_series)
        self.assertEqual(5, entry3.order_in_series)

        # deletion
        self.db.session.delete(entry2)
        self.db.session.commit()

        self.assertEqual(1, entry5.order_in_series)
        self.assertEqual(2, entry4.order_in_series)
        self.assertEqual(3, entry1.order_in_series)
        self.assertEqual(4, entry3.order_in_series)

        self.db.session.delete(entry5)
        self.db.session.commit()

        self.assertEqual(1, entry4.order_in_series)
        self.assertEqual(2, entry1.order_in_series)
        self.assertEqual(3, entry3.order_in_series)

    def test_entry_search(self):
        series1 = self._add_commit(Series('series1'))
        entrytype1 = self._add_commit(EntryType('entrytype1'))
        series2 = self._add_commit(Series('series2'))

        entry1 = self._add_commit(Entry('entry1', date(2021, 1, 1), 1, entrytype1.id, series1.id))
        entry2 = self._add_commit(Entry('entry2', date(2021, 2, 1), 2, entrytype1.id, series1.id))
        entry3 = self._add_commit(Entry('entry3', date(2021, 3, 1), 3, entrytype1.id, series1.id))
        entry4 = self._add_commit(Entry('entry4', date(2021, 3, 1), 1, entrytype1.id, series2.id))

        entries, _ = Entry.query_by_fields({'id': entry1.id})
        self.assertEqual([entry1], entries)

        entries, _ = Entry.query_by_fields({'series_id': series1.id})
        self.assertEqual([entry1, entry2, entry3], entries)

        entries, _ = Entry.query_by_fields({'name': '1'})
        self.assertEqual([entry1], entries)

        entries, _ = Entry.query_by_fields({'entrytype_id': 342})
        self.assertEqual([], entries)

        entries, _ = Entry.query_by_fields({'date': date(2021, 3, 1)})
        self.assertEqual([entry3, entry4], entries)

        entries, _ = Entry.query_by_fields({'date': date(2021, 3, 1), 'series_id': series1.id})
        self.assertEqual([entry3], entries)

        entries, _ = Entry.query_by_fields({'invalid_field': 123})
        self.assertEqual(None, entries)






if __name__ == '__main__':
    unittest.main()
