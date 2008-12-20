from sqlalchemy import create_engine
from werkzeug import ClosingIterator, SharedDataMiddleware,\
        import_string
from werkzeug.exceptions import HTTPException, NotFound
from werkzeug.routing import RequestRedirect

from os import path
from ConfigParser import SafeConfigParser

from rdrei.utils import session, metadata, local, local_manager,\
        Request
from rdrei.controllers import get_controller
from rdrei.core.appcache import ApplicationCache
import logging

log = logging.getLogger(__name__)

class RdreiApplication(object):
    def __init__(self, configfile):
        self._load_config(configfile)
        self.HERE_PATH = path.abspath(path.dirname(configfile))

        db_uri = self.get_config("database", "sqlalchemy.url")
        self.database_engine = create_engine(db_uri, convert_unicode=True)

        self.bind_to_context()
        self.make_middleware()
        self.load_appcache()

    def make_middleware(self):
        """Loads the middleware by "replacing" the dispatcher with a patched
        instance. This has to be redesigned from scratch, as this is not
        customizable by users."""
        self.dispatch = SharedDataMiddleware(self.dispatch, {
            '/static':  self.get_config('locations', 'static')
        })
        for mw in self._get_conflist("middleware"):
            self.dispatch = mw(self.dispatch,
                               dict(self.config.items("general")))
        #self.dispatch = CacheMiddleware(self.dispatch,
        #                                dict(self.config.items("general")))
        #self.dispatch = SessionMiddleware(self.dispatch,
        #                                  dict(self.config.items("general")))

    def _get_conflist(self, ssection):
        """Returns a module list of comma-seperated values in the config.ini subsection
        ssection."""
        return [import_string(m.strip()) for m in self.config.get("general", ssection).split(',') if m]

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
        processors = self._get_conflist("processors")
        # Apply the request processors
        for processor in processors:
            processor.process_request(request)

        # This is ugly and reminds me too much of pylons.
        # Let's try to live without it and see how much carrying the request
        # with us annoys us.
        #request.bind_to_context()

        # Get url_map from app_name.urls
        self.url_map = self.import_from_app("urls", "url_map")

        local.url_adapter = adapter = self.url_map.bind_to_environ(environ)
        try:
            endpoint, values = adapter.match(request.path)
            handler = get_controller(request, endpoint)
        except NotFound:
            response = get_controller(request, 'static/not_found')()
            response.status_code = 404
        except (HTTPException, RequestRedirect), e:
            response = e
        else:
            for processor in processors:
                action = processor.process_view(request, handler, values)
                if action:
                    return action(environ, start_response)
        try:
            response = handler(**values)
        except Exception, e:
            # If the handler raised an exception, process it.
            for processor in reversed(processors):
                action = processor.process_exception(request, e)
                if action:
                    # If process_exception returned something, process it.
                    return action(environ, start_response)
            # In case no hook applied, raise it.
            raise

        for processor in reversed(processors):
            response = processor.process_response(request, response)

        return ClosingIterator(response(environ, start_response),
                               [session.remove, local_manager.cleanup])

    def __call__(self, environ, start_response):
        return self.dispatch(environ, start_response)

