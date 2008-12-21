from werkzeug import BaseResponse

from rdrei.controllers import ControllerBase

class ${contname_cap}(ControllerBase):

    def index(self):
        """Your controller code here."""
        return BaseResponse("${contname}/index")

