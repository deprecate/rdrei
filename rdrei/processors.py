# -*- coding: utf-8 -*-
"""
 rdrei.processors
 ~~~~~~~~~~~~~~~~
 Module for django-middleware-like request and response manipulation.


 :copyright: 2008 by Pascal Hartig <phartig@rdrei.net>, Armin Ronacher, Marek
 Kubica
 :license: GPL, see doc/LICENSE for more details.
 """

class Processor(object):
    """A request and response processor - it is what Django calls a
    middleware, but Werkzeug also includes straight-foward support for real
    WSGI middlewares, so another name was chosen.

    The code of this processor is derived from the example in the Werkzeug
    trac, called `Request and Response Processor
    <http://dev.pocoo.org/projects/werkzeug/wiki/RequestResponseProcessor>`_
    """

    @staticmethod
    def process_request(request):
        return request

    @staticmethod
    def process_response(request, response):
        return response

    @staticmethod
    def process_view(request, view_func, view_kwargs):
        """process_view() is called just before the Application calls the
        function specified by view_func.

        If this returns None, the Application processes the next Processor,
        and if it returns something else (like a Response instance), that
        will be returned without any further processing.
        """
        return None

    @staticmethod
    def process_exception(request, exception):
        return None

class SessionProcessor(Processor):
    """A session processor that saves the session after every view."""
    @staticmethod
    def process_response(request, response):
        request.session.save()
        return response

