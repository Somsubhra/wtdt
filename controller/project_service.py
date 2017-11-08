from flask import g
import bcrypt
from datetime import datetime
from uuid import uuid4


class ProjectService:
    def __init__(self):
        pass

    @staticmethod
    def add_project(name, password):
        if ProjectService.project_exists(name):
            raise Exception("Project '" + name + "' already exists")

        project_id = g.mongo.projects.insert_one({
            "name": name,
            "password": bcrypt.hashpw(password, bcrypt.gensalt()),
            "access_token": str(uuid4()),
            "status": "active",
            "created_on": datetime.now(),
            "modified_on": datetime.now()
        }).inserted_id

        return {
            "id": project_id,
            "name": name
        }

    @staticmethod
    def authenticate_project(name, password):
        project = g.mongo.projects.find_one({"name": name,
                                             "status": "active"})

        if not project:
            raise Exception("Project '" + name + "' not found")

        if not bcrypt.hashpw(password.encode("utf-8"), project["password"].encode("utf-8")) == project["password"]:
            raise Exception("Invalid password")

        return {
            "id": str(project["_id"]),
            "name": project["name"],
            "access_token": project["access_token"]
        }

    @staticmethod
    def identify_project_from_bearer_token(bearer_token):
        project = g.mongo.projects.find_one({"access_token": bearer_token,
                                             "status": "active"})

        if not project:
            raise Exception("Invalid bearer token")

        return {
            "id": str(project["_id"]),
            "role": "project",
            "name": project["name"]
        }

    @staticmethod
    def project_exists(name):
        return g.mongo.projects.find({"name": name}).count() is 1
