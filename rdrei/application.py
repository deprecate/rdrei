from sqlalchemy import create_engine
from werkzeug import ClosingIterator, SharedDataMiddleware, find_modules
from werkzeug.exceptions import HTTPException, NotFound
from beaker.middleware import CacheMiddleware, SessionMiddleware

from os import path
from ConfigParser import SafeConfigParser
from datetime import datetime

from rdrei.utils import session, metadata, local, local_manager, url_map,\
        Request
from rdrei.controllers import get_controller, BaseController
from rdrei.appcache import ApplicationCache
import rdrei.models, logging

log = logging.getLogger(__name__)

HERE_PATH = path.dirname(__file__)

class RdreiApplication(object):
    def __init__(self):
        self._load_config()
        db_uri = self.get_config("database", "sqlalchemy.url")
        self.database_engine = create_engine(db_uri, convert_unicode=True)

        self.make_middleware()
        self.load_appcache()
        BaseController.expose_all()

    def make_middleware(self):
        self.dispatch = SharedDataMiddleware(self.dispatch, {
            '/static':  self.get_config('locations', 'static')
        })
        self.dispatch = CacheMiddleware(self.dispatch,
                                        dict(self.config.items("general")))
        self.dispatch = SessionMiddleware(self.dispatch,
                                          dict(self.config.items("general")))

    def load_appcache(self):
        self.cache = ApplicationCache(self.config.get("general",
                                                      "application.name"))

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

    def import_from_app(self, name, sub = None):
        sub = sub or ['']
        app_name = self.config.get("general", "app_name")
        
        module = __import__(app_name+"."+name, None, None, sub)
        return module
        

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

        return ClosingIterator(response(environ, start_response),
                               [session.remove, local_manager.cleanup])

    def __call__(self, environ, start_response):
        return self.dispatch(environ, start_response)


