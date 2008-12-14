from werkzeug.routing import Map, Rule, Submount

url_map = Map([
    Rule('/static/<file>', endpoint='static', build_only=True),

    # Blog
    Rule('/', endpoint="blog/index"),
    Submount('/test', [
        Rule('/get', endpoint="blog/get_session"),
        Rule('/set/<value>', endpoint="blog/set_session"),
        Rule('/cache', endpoint="blog/cached_page"),
    ])
])

