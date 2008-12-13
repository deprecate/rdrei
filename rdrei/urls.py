from werkzeug.routing import Map, Rule

url_map = Map([
    Rule('/static/<file>', endpoint='static', build_only=True),

    # Blog
    Rule('/', endpoint="test/index")
])

