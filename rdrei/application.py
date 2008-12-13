from sqlalchemy import create_engine
from werkzeug import ClosingIterator, SharedDataMiddleware
from werkzeug.exceptions import HTTPException, NotFound

from os import path
from ConfigParser import SafeConfigParser
from datetime import datetime, timedelta

from rdrei.utils import session, metadata, local, local_manager, url_map,\
        Request
from rdrei.controllers import get_controller
import rdrei.models

HERE_PATH = path.dirname(__file__)

class RdreiApplication(object):
    def __init__(self):
        self._load_config()
        db_uri = self.get_config("database", "sqlalchemy.url")
        self.database_engine = create_engine(db_uri, convert_unicode=True)

        self.dispatch = SharedDataMiddleware(self.dispatch, {
            '/static':  self.get_config('locations', 'static')
        })

    def bind_to_context(self):
        local.application = self

    def _load_config(self):
        config = SafeConfigParser()
        config.read(path.join(HERE_PATH, '..', 'config.ini'))
        self.config = config

    def get_config(self, section, key):
        return self.config.get(section, key, False, {
            'here': HERE_PATH
        })

    def init_database(self):
        metadata.create_all(self.database_engine)

    def dispatch(self, environ, start_response):
        self.bind_to_context()
        request = Request(environ)
        request.bind_to_context()

        local.url_adapter = adapter = url_map.bind_to_environ(environ)
        try:
            endpoint, values = adapter.match(request.path)
            handler = get_controller(endpoint)
            response = handler(request, **values)
        except NotFound:
            response = get_controller('static/not_found')(request)
            response.status_code = 404
        except HTTPException, e:
            response = e.get_response(environ)
        else:
            expires = datetime.utcnow() + timedelta(days=31)
            if request.first_visit or request.session.should_save:
                request.session.save_cookie(response, self.get_config("general", "cookie.name"),
                                            expires=expires)

        return ClosingIterator(response(environ, start_response),
                               [session.remove, local_manager.cleanup])

    def __call__(self, environ, start_response):
        return self.dispatch(environ, start_response)

