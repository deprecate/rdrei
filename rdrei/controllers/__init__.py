# -*- coding: utf-8 -*-
"""
    rdrei.controllers
    ~~~~~~~~~~~~~~~~
    Basic functions for controller management and BaseController class.

    :copyright: 2008 by Pascal Hartig <phartig@rdrei.net>
    :license: GPL, see doc/LICENSE for more details.
"""

from rdrei.local import local
from rdrei.utils import render_template

from functools import wraps

import logging

log = logging.getLogger(__name__)

def get_controller(request, name):
    application = local.application
    if '/' in name:
        cname, hname = name.split('/')
    else:
        return application.import_from_app('controllers.%s' % name)

    controller = application.cache.get_controller(cname)
    if not controller:
        module = application.import_from_app('controllers.%s' % cname)
        controller = module.controller
    return getattr(controller(request), hname)

class BaseController(object):
    helpers = dict()
    _need_request = list()

    def __init__(self, request):
        self.request = request
        self.translations = self.request.translations
        self._load_helpers()

    def render_to_response(self, template, context = None):
        context = context or {}
        context.update({'h': self.helpers, 'request': self.request})
        return render_template(self.request, template, context)

    #def register_helper(self, helper, name = None):
    #    name = name or helper.__name__
    #    self.helpers[name] = helper

    def register_request(self):
        """Maps the first parameter to be the request object."""
        def _outer(func):
            @wraps(func)
            def _inner(*args, **kwargs):
                return func(self.request, *args, **kwargs)
            return _inner
        return _outer

    @classmethod
    def register_helper(cls, func):
        """Decorator that registers a help method to need a request as first argument."""
        cls._need_request.append(func)
        return func

    def _load_helpers(self):
        """Loads the corresponding app_name.helpers.controller_name functions
        into our helpers dictionary, that is available via render_to_response
        and the context variable h."""
        # If we are not a sub class, do nothing.
        if not self.__class__.__bases__:
            return {}
        import inspect
        application = local.application
        mod_name = self.__module__.split('.')[-1]
        _helpers = application.import_from_app("helpers", mod_name)
        #helpers = [(k, v) for k, v in vars(_helpers).iteritems() if inspect.isfunction(v)]
        helpers = dict()
        for k, v in vars(_helpers).iteritems():
            if inspect.isfunction(v):
                log.debug("%r is function and need request is %r" % (v,
                                                                     self._need_request))
                if v in self.__class__._need_request:
                    log.debug("%r is in need request." % v)
                    helpers[k] = self.register_request()(v)
                else:
                    helpers[k] = v

        self.helpers.update(helpers)

