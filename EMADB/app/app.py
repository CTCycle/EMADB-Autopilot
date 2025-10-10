from __future__ import annotations

import os

from fastapi import FastAPI
import gradio as gr

from EMADB.app.api.endpoints import configuration, search
from EMADB.app.client.controllers import UIController
from EMADB.app.client.ui import build_interface
from EMADB.app.dependencies import config_service
from EMADB.app.logger import logger
from EMADB.app.variables import EnvironmentVariables


###############################################################################
def create_app() -> FastAPI:
    os.environ.setdefault("GRADIO_ANALYTICS_ENABLED", "0")
    EnvironmentVariables()
    app = FastAPI(title="EMAutoPilot", version="1.0")

    app.include_router(configuration.router, prefix="/api")
    app.include_router(search.router, prefix="/api")

    controller = UIController(app)
    initial_config = config_service.get_configuration()
    interface = build_interface(controller, initial_config)
    app = gr.mount_gradio_app(app, interface, path="/")

    logger.info("EMAutoPilot web application initialized")
    return app


app = create_app()
