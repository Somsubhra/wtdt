from functools import wraps
from flask import Flask, g, request, jsonify
from pymongo import MongoClient

from config_service import ConfigService
from project_service import ProjectService

app = Flask(__name__)


# Mongo configuration
@app.before_request
def init_mongo():
    g.mongo = MongoClient(ConfigService.get_mongo_host(), 27017).wtdt


# Helper functions
def requires_auth(roles):
    def requires_auth_child(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if "Authorization" not in request.headers:
                raise Exception("Authorization header is missing")

            authorization_header = request.headers["Authorization"]

            authorization_components = str(authorization_header).split()

            if len(authorization_components) != 2:
                raise Exception("Invalid authorization header")

            if authorization_components[0] == "Bearer":
                g.user = ProjectService.identify_project_from_bearer_token(authorization_components[1])
            else:
                raise Exception("Invalid authorization method")

            if not g.user["role"] in roles:
                raise Exception("Access denied for role " + g.user["role"])

            return f(*args, **kwargs)

        return decorated
    return requires_auth_child


@app.before_request
def unwind_json():
    g.json_body = request.get_json(force=True, silent=True)


def required_param(key):
    if not g.json_body:
        raise Exception("Missing request body")

    if key not in g.json_body:
        raise Exception("Missing required parameter '" + key + "'")

    return g.json_body[key]


def optional_param(key):
    if not g.json_body:
        return None

    if key not in g.json_body:
        return None

    return g.json_body[key]


@app.route("/")
def index():
    return jsonify({"success": True, "message": "WTDT Controller API"})


@app.route("/project", methods=["POST"])
def add_project():
    return jsonify(ProjectService.add_project(required_param("name"),
                                              required_param("password")))


@app.route("/project/authenticate", methods=["POST"])
def authenticate_project():
    return jsonify(ProjectService.authenticate_project(required_param("name"),
                                                       required_param("password")))


# Error handling routes
@app.errorhandler(404)
def handle_404(error):
    return jsonify({"success": False, "message": str(error)})


@app.errorhandler(Exception)
def handle_unknown_exception(error):
    return jsonify({"success": False, "message": str(error)})

app.run(host=ConfigService.get_controller_host(),
        port=ConfigService.get_controller_port(),
        debug=ConfigService.get_controller_env().lower() == "dev")
