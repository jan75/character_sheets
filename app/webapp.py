import logging
import os

from flask import Flask
from flask_restful import Api

from api.rest_resources import EntryTypeSearchRESTResource, CharacterSearchRESTResource

logger = logging.getLogger(__name__)


def create_app():
    logger.info('Creating flask app')

    db_connection_string = os.getenv('DB_CONNECTION_STRING')
    if not db_connection_string:
        err = 'No database connection string specified (DB_CONNECTION_STRING)'
        logger.error(err)
        raise RuntimeError(err)

    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.urandom(16)

    from database import db
    db.connect_db(db_connection_string)

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db.session.remove()

    api = Api(app, '/rest')

    from database import generate_test_data
    app.add_url_rule('/rest/generate_test_data', view_func=generate_test_data)

    from api.rest_resources import SeriesRESTResource, SeriesSearchRESTResource, SeriesEntriesRESTResource, \
        SeriesCharactersRESTResource
    api.add_resource(SeriesRESTResource, '/series', '/series/', '/series/<int:id>')
    api.add_resource(SeriesSearchRESTResource, '/series/search')
    api.add_resource(SeriesEntriesRESTResource, '/series/<int:id>/entries')
    api.add_resource(SeriesCharactersRESTResource, '/series/<int:id>/characters')

    from api.rest_resources import EntryTypeRESTResource, EntryTypeEntriesRESTResource
    api.add_resource(EntryTypeRESTResource, '/entrytypes', '/entrytypes/', '/entrytypes/<int:id>')
    api.add_resource(EntryTypeSearchRESTResource, '/entrytypes/search')
    api.add_resource(EntryTypeEntriesRESTResource, '/entrytypes/<int:id>/entries')

    from api.rest_resources import EntryRESTResource, EntrySearchRESTResource
    api.add_resource(EntryRESTResource, '/entries', '/entries/', '/entries/<int:id>')
    api.add_resource(EntrySearchRESTResource, '/entries/search')

    from api.rest_resources import CharacterRESTResource
    api.add_resource(CharacterRESTResource, '/characters', '/characters/')
    api.add_resource(CharacterSearchRESTResource, '/characters/search')

    from api.rest_resources import CharacterInfoRESTResource
    api.add_resource(CharacterInfoRESTResource, '/characterinfo', '/characterinfo/')

    return app
