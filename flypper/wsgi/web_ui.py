import os

from jinja2 import Environment
from jinja2 import FileSystemLoader
from werkzeug.exceptions import HTTPException
from werkzeug.exceptions import NotFound
from werkzeug.routing import Map
from werkzeug.routing import Rule
from werkzeug.urls import url_parse
from werkzeug.utils import redirect
from werkzeug.wrappers import Request
from werkzeug.wrappers import Response

def get_hostname(url):
    return url_parse(url).netloc


class FlypperWebUI:
    def __init__(self):
        self.jinja_env = Environment(
            loader=FileSystemLoader(
                os.path.join(os.path.dirname(__file__), "templates")
            ),
            autoescape=True,
        )
        self.jinja_env.filters["hostname"] = get_hostname
        self.url_map = Map(
            [
                Rule("/", endpoint="index", methods=["GET"]),
                Rule("/edit_form", endpoint="edit_form", methods=["GET"]),
                Rule("/edit", endpoint="edit", methods=["POST"]),
            ]
        )

    def on_index(self, request):
        return self.render_template("index.html")

    def on_edit(self, request):
        return redirect("/")

    def on_edit_form(self, request):
        return self.render_template("edit_form.html")

    def error_404(self):
        response = self.render_template("404.html")
        response.status_code = 404
        return response

    def render_template(self, template_name, **context):
        t = self.jinja_env.get_template(template_name)
        return Response(t.render(context), mimetype="text/html")

    def dispatch_request(self, request):
        adapter = self.url_map.bind_to_environ(request.environ)
        try:
            endpoint, values = adapter.match()
            return getattr(self, f"on_{endpoint}")(request, **values)
        except NotFound:
            return self.error_404()
        except HTTPException as e:
            return e

    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        response = self.dispatch_request(request)
        return response(environ, start_response)

    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)


if __name__ == "__main__":
    from werkzeug.serving import run_simple

    app = FlypperWebUI()
    run_simple("127.0.0.1", 5000, app, use_debugger=True, use_reloader=True)
