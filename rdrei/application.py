from sqlalchemy import create_engine
from werkzeug import ClosingIterator, SharedDataMiddleware
from werkzeug.exceptions import HTTPException, NotFound
from beaker.middleware import CacheMiddleware, SessionMiddleware

from os import path
from ConfigParser import SafeConfigParser

from rdrei.utils import session, metadata, local, local_manager,\
        Request
from rdrei.controllers import get_controller
from rdrei.appcache import ApplicationCache
import rdrei.models, logging

log = logging.getLogger(__name__)

class RdreiApplication(object):
    def __init__(self, configfile):
        self._load_config(configfile)
        self.HERE_PATH = path.abspath(path.dirname(configfile))

        db_uri = self.get_config("database", "sqlalchemy.url")
        self.database_engine = create_engine(db_uri, convert_unicode=True)

        self.make_middleware()
        self.load_appcache()

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
                                                      "application.name"), self)

    def bind_to_context(self):
        local.application = self

    def _load_config(self, configfile):
        config = SafeConfigParser()
        #config.read(path.join(HERE_PATH, '..', 'config.ini'))
        config.read(configfile)
        self.config = config

    def get_config(self, section, key):
        return self.config.get(section, key, False, {
            'here': self.HERE_PATH
        })

    def init_database(self):
        metadata.create_all(self.database_engine)

    def import_from_app(self, name, sub = None):
        _sub = sub and [sub] or ['']
        app_name = self.config.get("general", "application.name")
        
        module = __import__(app_name+"."+name, None, None, _sub)
        if sub:
            return getattr(module, sub)
        return module
        
    def dispatch(self, environ, start_response):
        self.bind_to_context()
        request = Request(environ)
        # This is ugly and reminds me too much of pylons.
        # Let's try to live without it and see how much carrying the request
        # with us annoys us.
        #request.bind_to_context()

        # Get url_map from app_name.urls
        url_map = self.import_from_app("urls", "url_map")

        local.url_adapter = adapter = url_map.bind_to_environ(environ)
        try:
            endpoint, values = adapter.match(request.path)
            handler = get_controller(request, endpoint)
            response = handler(**values)
        except NotFound:
            response = get_controller(request, 'static/not_found')()
            response.status_code = 404
        except HTTPException, e:
            response = e.get_response(environ)

        request.session.save()
        return ClosingIterator(response(environ, start_response),
                               [session.remove, local_manager.cleanup])

    def __call__(self, environ, start_response):
        return self.dispatch(environ, start_response)

