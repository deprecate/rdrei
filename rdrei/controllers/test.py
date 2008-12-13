from rdrei.utils import render_template

class TestController(object):
    def index(self, request):
        request.set_language('de')
        return render_template('index.html')

controller = TestController
