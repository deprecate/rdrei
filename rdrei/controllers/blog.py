from rdrei.utils import render_template, expose
from rdrei.controllers import BaseController

class BlogController(BaseController):
    @expose("/")
    def index(self, request):
        return render_template("index.html")

controller = BlogController
