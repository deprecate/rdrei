from werkzeug import BaseResponse

from rdrei.controllers import BaseController

class ${contname_cap}(BaseController):

    def index(self):
        """Your controller code here."""
        return BaseResponse("${contname}/index")

controller = ${contname_cap}
