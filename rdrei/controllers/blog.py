from werkzeug import BaseResponse
from rdrei.utils import expose
from rdrei.controllers import BaseController
from rdrei.decorators import beaker_cache

class BlogController(BaseController):
    def index(self):
        return self.render_to_response("index.html")

    @expose("/test/i18n/<lang>")
    def i18n(self, lang):
        self.request.set_language(lang)
        return BaseResponse(self.request._("Hello, World!")+" Locale: %s" % self.request.locale)

    @expose("/test/bla")
    def bla(self):
        return self.render_to_response("index.html", {'msg': "@expose works."})

    def get_session(self):
        c = {'msg': "Session value is: "+self.request.session.get("test_data",
                                                             "empty")}
        return self.render_to_response("index.html", c)

    def set_session(self, value):
        self.request.session['test_data'] = value
        return BaseResponse("Okay, new Value: %s" %
                            self.request.session.get('test_data'))

    @beaker_cache(query_args=False)
    def cached_page(self):
        """With query_args=False, the arguments to this method are ignored. That
        means that the first call with ?wurst=x will set the cache value and any
        change will be ignore. Set query_args=True, to turn this behaviour
        off."""
        parameter = 'wurst' in self.request.values and self.request.values['wurst'] or None
        if parameter:
            return BaseResponse("This should be cached. Wurst is currently %s." %
                                parameter)
        return BaseResponse("This should be cached. (Watch log to verify.)")


controller = BlogController
