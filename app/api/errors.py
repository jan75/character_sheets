import logging
from enum import Enum
from typing import List

from flask import make_response
from marshmallow import ValidationError

logger = logging.getLogger(__name__)


class ErrorType(Enum):
    INPUT_ERROR = 'input_error'
    NOT_FOUND = 'not_found'
    SERVER_ERROR = 'server_error'


def return_validation_errors(error: ValidationError):
    logger.info('Validation errors: %s', error)
    details = []
    if isinstance(error.messages, list):
        details = error.messages
    else:
        for key, value in error.messages.items():
            details.append({
                'field': key,
                'message': value
            })

    return error_response(400, ErrorType.INPUT_ERROR, 'Input validation error', details)


def error_response(status_code: int, error_type: ErrorType, message: str, details: List = None):
    data = {
        'status': status_code,
        'error_type': error_type.value,
        'message': message
    }

    if details:
        data['details'] = []
        for detail in details:
            data['details'].append(detail)

    return make_response(data, status_code)
