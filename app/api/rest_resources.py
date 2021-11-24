from flask_restful import Resource

from api.api_base import BasicEntityRESTResource, check_pagination, multi_data_response, SearchRESTResource
from api.errors import error_response, ErrorType
from database import LIMIT
from models.character import Character, CharacterSearchSchema
from models.character_info import CharacterInfo
from models.entry import Entry, EntrySearchSchema
from models.entrytype import EntryType, EntryTypeSearchSchema
from models.series import Series, SeriesSearchSchema


class EntryRESTResource(Resource, BasicEntityRESTResource):

    def __init__(self, *args, **kwargs):
        super().__init__(Entry, *args, **kwargs)


class EntrySearchRESTResource(Resource, SearchRESTResource):

    def __init__(self, *args, **kwargs):
        super().__init__(Entry, EntrySearchSchema(), *args, **kwargs)


class EntryTypeRESTResource(Resource, BasicEntityRESTResource):

    def __init__(self, *args, **kwargs):
        super().__init__(EntryType, *args, **kwargs)


class EntryTypeSearchRESTResource(Resource, SearchRESTResource):

    def __init__(self, *args, **kwargs):
        super().__init__(EntryType, EntryTypeSearchSchema(), *args, **kwargs)


class SeriesRESTResource(Resource, BasicEntityRESTResource):

    def __init__(self, *args, **kwargs):
        super().__init__(Series, *args, **kwargs)


class SeriesSearchRESTResource(Resource, SearchRESTResource):

    def __init__(self, *args, **kwargs):
        super().__init__(Series, SeriesSearchSchema(), *args, **kwargs)


class CharacterRESTResource(Resource, BasicEntityRESTResource):

    def __init__(self, *args, **kwargs):
        super().__init__(Character, *args, **kwargs)


class CharacterSearchRESTResource(Resource, SearchRESTResource):

    def __init__(self, *args, **kwargs):
        super().__init__(Character, CharacterSearchSchema(), *args, **kwargs)


class CharacterInfoRESTResource(Resource, BasicEntityRESTResource):

    def __init__(self, *args, **kwargs):
        super().__init__(CharacterInfo, *args, **kwargs)


class EntryTypeEntriesRESTResource(Resource):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @check_pagination
    def get(self, id: int, offset: int = 0, limit: int = LIMIT):
        entry_types, row_count = EntryType.query_by_id(id=id, offset=offset, limit=limit)
        if not entry_types:
            return error_response(500, ErrorType.SERVER_ERROR, 'Could not query entrytypes due to an unexpected error')

        if len(entry_types) == 0:
            return error_response(404, ErrorType.NOT_FOUND, 'No entity found with given ID')
        elif len(entry_types) > 1:
            return error_response(500, ErrorType.SERVER_ERROR,
                                  'Multiple results found when there should only be one')

        entry_type = entry_types[0]

        entries, row_count = Entry.query_by_fields({'type_id': entry_type.id}, offset=offset, limit=limit)
        if entries is None:
            return error_response(500, ErrorType.SERVER_ERROR, 'Could not query entries due to an unexpected error')

        return multi_data_response(entries, row_count, offset, limit)


class SeriesEntriesRESTResource(Resource):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @check_pagination
    def get(self, id: int, offset: int = 0, limit: int = LIMIT):
        series, row_count = Series.query_by_id(id=id, offset=offset, limit=limit)
        if not series:
            return error_response(500, ErrorType.SERVER_ERROR, 'Could not query series due to an unexpected error')

        if len(series) == 0:
            return error_response(404, ErrorType.NOT_FOUND, 'No entity found with given ID')
        elif len(series) > 1:
            return error_response(500, ErrorType.SERVER_ERROR,
                                  'Multiple results found when there should only be one')

        series = series[0]

        entries, row_count = Entry.query_by_fields({'series_id': series.id}, offset=offset, limit=limit)
        if entries is None:
            return error_response(500, ErrorType.SERVER_ERROR, 'Could not query entries due to an unexpected error')

        return multi_data_response(entries, row_count, offset, limit)


class SeriesCharactersRESTResource(Resource):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @check_pagination
    def get(self, id: int, offset: int = 0, limit: int = LIMIT):
        series, row_count = Series.query_by_id(id=id, offset=offset, limit=limit)
        if not series:
            return error_response(500, ErrorType.SERVER_ERROR, 'Could not query series due to an unexpected error')

        if len(series) == 0:
            return error_response(404, ErrorType.NOT_FOUND, 'No entity found with given ID')
        elif len(series) > 1:
            return error_response(500, ErrorType.SERVER_ERROR,
                                  'Multiple results found when there should only be one')

        series = series[0]

        characters, row_count = Character.query_by_fields({'series_id': series.id}, limit=limit, offset=offset)
        if characters is None:
            return error_response(500, ErrorType.SERVER_ERROR, 'Could not query characters due to an unexpected error')

        return multi_data_response(characters, row_count, offset, limit)
