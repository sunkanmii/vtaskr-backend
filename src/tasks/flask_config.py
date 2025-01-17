from jinja2 import FileSystemLoader

from flask import Flask
from src.tasks.hmi.flask import tasks_bp
from src.tasks.persistence.sqlalchemy import TagDB, TaskDB

from .settings import APP_NAME


def setup_flask(app: Flask, project_dir: str) -> dict:
    app.register_blueprint(tasks_bp)

    return {
        "domains": [APP_NAME],
        "loaders": [
            FileSystemLoader(
                f"{project_dir}/src/{APP_NAME.lower()}/hmi/flask/templates"
            )
        ],
        "observers": [],
        "repositories": [
            (APP_NAME, "Tag", TagDB()),
            (APP_NAME, "Task", TaskDB()),
        ],
        "permissions_resources": ["Task", "Tag"],
    }
