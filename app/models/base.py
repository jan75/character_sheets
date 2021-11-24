import logging
from typing import Dict

from marshmallow import Schema

from database import LIMIT

logger = logging.getLogger(__name__)


class RESTModel:
    schema: Schema

    def to_dict(self):
        raise NotImplementedError()

    @staticmethod
    def from_dict(data: Dict) -> 'RESTModel':
        raise NotImplementedError()

    def update(self, data: Dict) -> 'RESTModel':
        raise NotImplementedError()

    @staticmethod
    def query_by_id(id: int = None, offset: int = 0, limit: int = LIMIT):
        raise NotImplementedError()

    @staticmethod
    def query_by_fields(fields: Dict, offset: int = 0, limit: int = LIMIT):
        raise NotImplementedError()


