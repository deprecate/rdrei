# Add your controller's helpers here.
from rdrei.controllers.blog import BlogController

@BlogController.register_helper
def test(request):
    return request.translations.ugettext("Hello, World!")

def test2():
    return "Was geht?"

