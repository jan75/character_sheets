import functools
from typing import Type

from flask import make_response, request, Response
from marshmallow import ValidationError, Schema
from sqlalchemy.exc import IntegrityError

from models.base import RESTModel, logger
from api.errors import error_response, ErrorType, return_validation_errors
from database import LIMIT, db


def check_pagination(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        request_args = request.args
        logger.debug('request_args: %s', request_args)
        try:
            offset = int(request_args['offset'])
            if offset < 0:
                return error_response(400, ErrorType.INPUT_ERROR, 'Offset can\'t be a negative value')
        except KeyError as e:
            logger.debug('No offset set, using 0')
            offset = 0
        except ValueError as e:
            logger.info('Invalid offset value: %s', e)
            return error_response(400, ErrorType.INPUT_ERROR, 'Invalid value for offset (not a number?)')

        try:
            limit = int(request_args['limit'])
            if limit < 0:
                return error_response(400, ErrorType.INPUT_ERROR, 'limit can\'t be a negative value')
            if limit > LIMIT:
                logger.info('Given value for limit is above system limit, using LIMIT (%d)', LIMIT)
                limit = LIMIT
        except KeyError as e:
            logger.debug('No limit set, using LIMIT (%d)', LIMIT)
            limit = LIMIT
        except ValueError as e:
            logger.info('Invalid limit value: %s', e)
            return error_response(400, ErrorType.INPUT_ERROR, 'Invalid value for limit (not a number?)')

        return f(offset=offset, limit=limit, *args, **kwargs)

    return wrapper


class SearchRESTResource:

    def __init__(self, entity_type: Type[RESTModel], input_schema: Schema):
        self.entity_type = entity_type
        self.input_schema = input_schema

    def post(self):
        if not request.is_json:
            return error_response(400, ErrorType.INPUT_ERROR, 'MimeType is not application/json')

        try:
            input_data = self.input_schema.load(request.json)
        except ValidationError as e:
            return return_validation_errors(e)

        entities, row_count = self.entity_type.query_by_fields(fields=input_data, offset=0, limit=LIMIT)
        if entities is None:
            return error_response(500, ErrorType.SERVER_ERROR, 'Could not search entities due to an unexpected error')

        return multi_data_response(entities, row_count, 0, LIMIT)


class BasicEntityRESTResource:

    def __init__(self, entity_type: Type[RESTModel]):
        self.entity_type = entity_type

    @check_pagination
    def get(self, id: int = None, offset: int = 0, limit: int = LIMIT):
        if id:
            entities, row_count = self.entity_type.query_by_id(id=id)
        else:
            entities, row_count = self.entity_type.query_by_id(offset=offset, limit=limit)

        logger.debug('id: %s, row_count: %s', id, row_count)
        if entities is None:
            return error_response(500, ErrorType.SERVER_ERROR, 'Could not query entities due to an unexpected error')

        if id:
            if len(entities) == 0:
                return error_response(404, ErrorType.NOT_FOUND, 'No entity found with given ID')
            elif len(entities) == 1:
                return make_response(entities[0].to_dict(), 200)
            elif len(entities) > 1:
                return error_response(500, ErrorType.SERVER_ERROR,
                                      'Multiple results found when there should only be one')
        else:
            return multi_data_response(entities, row_count, offset, limit)

    def post(self):
        if not request.is_json:
            return error_response(400, ErrorType.INPUT_ERROR, 'MimeType is not application/json')

        try:
            input_data = self.entity_type.schema.load(request.json)
        except ValidationError as e:
            return return_validation_errors(e)

        try:
            entity = self.entity_type.from_dict(input_data)
            db.session.add(entity)
            db.session.commit()
            return make_response('', 201)
        except IntegrityError as e:
            logger.error(e)
            db.session.rollback()
            return error_response(400, ErrorType.INPUT_ERROR,
                                  'Integrity error, some constraint might not have been respected. Schema: %s',
                                  self.entity_type.schema)
        except Exception as e:
            logger.error(e)
            db.session.rollback()
            return error_response(500, ErrorType.SERVER_ERROR, 'Could not create entity due to an unexpected error')

    def put(self, id: int = None):
        if not request.is_json:
            return error_response(400, ErrorType.INPUT_ERROR, 'MimeType is not application/json')

        if not id:
            return error_response(400, ErrorType.INPUT_ERROR, 'ID of entity in URL required')

        try:
            input_data = self.entity_type.schema.load(request.json)
        except ValidationError as e:
            return return_validation_errors(e)

        entity, row_count = self.entity_type.query_by_id(id=id)
        if entity is None:
            return error_response(500, ErrorType.SERVER_ERROR, 'Could not query entities due to an unexpected error')

        if len(entity) == 0:
            return error_response(404, ErrorType.NOT_FOUND, 'No entity found with given ID')
        elif len(entity) > 1:
            return error_response(500, ErrorType.SERVER_ERROR, 'Multiple results found when there should only be one')

        try:
            entity = entity[0]
            entity.update(input_data)
            db.session.commit()
            return make_response(entity.to_dict(), 200)
        except IntegrityError as e:
            logger.error(e)
            db.session.rollback()
            return error_response(400, ErrorType.INPUT_ERROR,
                                  'Integrity error, some constraint might not have been respected. Schema: %s')
        except Exception as e:
            logger.error(e)
            db.session.rollback()
            return error_response(500, ErrorType.SERVER_ERROR, 'Could not update entity due to an unexpected error')

    def delete(self, id: int = None):
        if not id:
            return error_response(400, ErrorType.INPUT_ERROR, 'ID of entity in URL required')

        entity, row_count = self.entity_type.query_by_id(id=id)
        if entity is None:
            return error_response(500, ErrorType.SERVER_ERROR, 'Could not query entities due to an unexpected error')

        if len(entity) == 0:
            return error_response(404, ErrorType.NOT_FOUND, 'No entity found with given ID')
        elif len(entity) > 1:
            return error_response(500, ErrorType.SERVER_ERROR, 'Multiple results found when there should only be one')

        try:
            entity = entity[0]
            db.session.delete(entity)
            db.session.commit()
            return make_response('', 204)
        except Exception as e:
            logger.error(e)
            db.session.rollback()
            return error_response(500, ErrorType.SERVER_ERROR, 'Could not delete entity due to an unexpected error')


def message_response(status_code: int, message: str) -> Response:
    data = {
        'status': status_code,
        'message': message
    }
    return make_response(data, status_code)


def multi_data_response(entity_list: [RESTModel], total_rows: int, offset: int, limit: int):
    if entity_list is None:
        entity_list = []

    data = {
        'size': total_rows,
        'limit': limit,
        'offset': offset,
        'data': []
    }

    for entity in entity_list:
        data['data'].append(entity.to_dict())

    return make_response(data, 200)
