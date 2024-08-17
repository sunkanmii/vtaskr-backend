import logging
import os
from importlib import import_module
from typing import Callable

from jinja2 import ChoiceLoader

from flask import Flask
from src.libs.dependencies import DependencyInjector
from src.settings import APP_NAME, AVAILABLE_LANGUAGES, INSTALLED_APPS, SECRET_KEY

logger = logging.getLogger(__name__)


def create_flask_app(dependencies: DependencyInjector) -> Flask:
    logger.info(f"Starting {APP_NAME}...")

    app = Flask(__name__)
    app.secret_key = SECRET_KEY
    app.dependencies = dependencies

    project_dir = os.getcwd()

    app.static_folder = f"{project_dir}/src/static"

    # App self config
    loaders = []
    domains: list[str] = []
    repositories: list[tuple] = []
    permissions_resources: list[str] = []

    for module in INSTALLED_APPS:
        logger.info(f"loading app {module}")

        setup_app: Callable = getattr(
            import_module(f"src.{module}.flask_config"), "setup_flask"
        )
        result = setup_app(app=app, project_dir=project_dir)

        loaders.extend(result.get("loaders", []))
        domains.extend(result.get("domains", []))
        repositories.extend(result.get("repositories", []))
        permissions_resources.extend(result.get("permissions_resources", []))

        logger.info(f"app {module} ready.")

    logger.info("loading Jinja items")
    app.jinja_env.add_extension("jinja2.ext.i18n")
    app.jinja_env.loader = ChoiceLoader(loaders)

    logger.info("set up dependencies.")

    app.dependencies.instantiate_dependencies()
    app.dependencies.set_context(
        app=app,
        domains=domains,
        languages=list(AVAILABLE_LANGUAGES.keys()),
        repositories=repositories,
        permissions_resources=permissions_resources,
    )

    logger.info(f"{APP_NAME} ready !")

    return app
