from werkzeug import BaseResponse
from rdrei.controllers import BaseController

class TestController(BaseController):
    def index(self):
        return self.render_to_response("index.html")

    def not_found(self):
        # Change me.
        response = BaseResponse("HTTP 404")
        response.status = 404
        return response

controller = TestController
