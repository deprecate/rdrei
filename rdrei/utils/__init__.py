from sqlalchemy import MetaData
from sqlalchemy.orm import create_session, scoped_session
from werkzeug import Request as RequestBase, Response
from babel import Locale
from jinja2 import Environment, PackageLoader
from hashlib import sha1
from random import random
import time, logging

from rdrei.i18n import get_translations
from rdrei.core.local import local, local_manager

application = local('application')
url_map = local('url_adapter')

log = logging.getLogger(__name__)

metadata = MetaData()
session = scoped_session(lambda: create_session(application.database_engine,
                         autocommit=True), local_manager.get_ident)

def url_for(endpoint, _external=False, **values):
    return local.url_adapter.build(endpoint, values, force_external=_external)

jinja_env = None
def render_template(request, template, context=None):
    global jinja_env
    if not jinja_env:
        jinja_env = Environment(loader=PackageLoader(application.config.get("general", "application.name"),
                                                     'templates'),
                                extensions=['jinja2.ext.i18n'])

    context = context or {}
    context.update({
        'url_for': url_for,
        'request': request,
        'gettext': request.translations.ugettext,
        'ngettext': request.translations.ungettext
    })
    return Response(jinja_env.get_template(template).render(**context),
                    mimetype='text/html')

def generate_user_hash():
    """Generates an more or less unique SHA1 hash."""
    return sha1('%s|%s' % (random(), time.time())).hexdigest()

class Request(RequestBase):
    """Subclass of the `Request` object. automatically creates a new
    `user_hash` and sets `first_visit` to `True` if it's a new user.
    It also stores the engine and dbsession on it.
    """
    charset = 'utf-8'

    def __init__(self, environ):
        super(Request, self).__init__(environ)
        self.first_visit = False
        session = environ['beaker.session']
        user_hash = session.get('user_hash')

        if not user_hash:
            session['user_hash'] = generate_user_hash()
            self.first_visit = True
        self.user_hash = session['user_hash']
        self.session = session
        self.cache = environ['beaker.cache']

        # language is limited to english until translations are ready
        lang = session.get('locale')
        if lang is None:
            lang = (self.accept_languages.best or 'en').split('-')[0]
        self.locale = Locale.parse(lang)

    def set_language(self, lang):
        self.session['locale'] = lang

    @property
    def translations(self):
        return get_translations(self.locale)

    def _(self, *args, **kwargs):
        return self.translations.ugettext(*args, **kwargs)

    def bind_to_context(self):
        local.request = self

