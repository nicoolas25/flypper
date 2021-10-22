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

from flypper.storage.abstract import AbstractStorage
from flypper.storage.in_memory import InMemoryStorage

def get_hostname(url):
    return url_parse(url).netloc


class FlypperWebUI:
    def __init__(self, storage: AbstractStorage):
        self._storage = storage
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
                Rule("/flags", endpoint="create_flag", methods=["POST"]),
            ]
        )

    def on_index(self, request):
        return self.render_template("index.html", flags=self._storage.list())

    def on_edit(self, request):
        print(request.form)
        form = request.form
        self._storage.upsert({
            "name": form["flag_name"],
            "enabled": form.get("enabled", "off") == "on",
            "enabled_for_actors": {
                "actor_key": form["enabled_for_actors_key"],
                "actor_ids": [
                    actor_id.strip()
                    for actor_id in form["enabled_for_actors_ids"].split()
                    if actor_id
                ],
            } if form.get("enabled_for_actors", "off") == "on" else None,
            "enabled_for_percentage_of_actors": {
                "actor_key": form["enabled_for_percentage_of_actors_key"],
                "percentage": float(form["enabled_for_percentage_of_actors_percentage"]),
            } if form.get("enabled_for_percentage_of_actors", "off") == "on" else None,
            "deleted": False,
        })
        return redirect("/")

    def on_edit_form(self, request):
        flag = self._fetch_flag(flag_name=request.args.get("flag_name", None))
        if not flag:
            return self.error_404()

        return self.render_template("edit_form.html", flag=flag)

    def on_create_flag(self, request):
        form = request.form
        self._storage.upsert({
            "name": form["flag_name"],
            "enabled": False,
            "enabled_for_actors": None,
            "enabled_for_percentage_of_actors": None,
            "deleted": False,
        })
        return redirect("/")

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

    def _fetch_flag(self, flag_name: str):
        if not flag_name:
            return None

        flag = next(
            (flag for flag in self._storage.list() if flag.name == flag_name),
            None,
        )
        return flag
