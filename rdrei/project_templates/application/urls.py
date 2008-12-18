from werkzeug.routing import Map, Rule, Submount

url_map = Map([
    Rule("/", endpoint="static/index")
])

