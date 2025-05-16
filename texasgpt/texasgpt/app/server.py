import argparse
import os
import sys
from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# fastapi import time cost about 0.05s
from fastapi.staticfiles import StaticFiles


import sys

from texasgpt._private.config import Config
from texasgpt._version import version
from texasgpt.app.base import (
    WebServerParameters,
    # _create_model_start_listener,
    # _migration_db_storage,
    server_init,
)

# initialize_components import time cost about 0.1s
from texasgpt.component import SystemApp
from texasgpt.serve.core.schemas import add_exception_handler
from texasgpt.util.fastapi import create_app, replace_router
from texasgpt.util.i18n_utils import _, set_default_language
from texasgpt.util.parameter_utils import _get_dict_from_obj
from texasgpt.util.system_utils import get_system_info
from texasgpt.util.tracer import SpanType, SpanTypeRunName, initialize_tracer, root_tracer
from texasgpt.util.utils import (
    _get_logging_level,
    logging_str_to_uvicorn_level,
    setup_http_service_logging,
    setup_logging,
)



ROOT_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(ROOT_PATH)

LOGDIR = os.getenv("TEXASGPT_LOG_DIR", os.path.join(ROOT_PATH, "logs"))

# static_file_path = os.path.join(ROOT_PATH, "texasgpt", "app/static")

CFG = Config()
set_default_language(CFG.LANGUAGE)

app = create_app(
    title=_("Texas-GPT Open API"),
    description=_("Texas-GPT Open API"),
    version=version,
    openapi_tags=[],
)
# Use custom router to support priority
replace_router(app)



system_app = SystemApp(app)


def mount_routers(app: FastAPI):
    """Lazy import to avoid high time cost"""
    # from texasgpt.app.knowledge.api import router as knowledge_router
    from texasgpt.app.play_poker.api import router as poker_api
    app.include_router(poker_api, prefix="/api/v1/play_poker", tags=["PlayPoker"])



add_exception_handler(app)


def _get_webserver_params(args: List[str] = None):
    from texasgpt.util.parameter_utils import EnvArgumentParser

    parser = EnvArgumentParser()

    env_prefix = "webserver_"
    webserver_params: WebServerParameters = parser.parse_args_into_dataclass(
        WebServerParameters,
        env_prefixes=[env_prefix],
        command_args=args,
    )
    return webserver_params


def initialize_app(param: WebServerParameters = None, args: List[str] = None):
    """Initialize app
    If you use gunicorn as a process manager, initialize_app can be invoke in on_starting hook.
    Args:
        param:WebWerverParameters
        args:List[str]
    """
    if not param:
        param = _get_webserver_params(args)

    # import after param is initialized, accelerate --help speed
    # from texasgpt.model.cluster import initialize_worker_manager_in_client

    if not param.log_level:
        param.log_level = _get_logging_level()
    setup_logging(
        "texasgpt", logging_level=param.log_level, logger_filename=param.log_file
    )

    # model_name = param.model_name or CFG.LLM_MODEL
    # param.model_name = model_name
    param.port = param.port or CFG.TEXAS_WEBSERVER_PORT
    if not param.port:
        param.port = 5670

    print(param)

    # embedding_model_name = CFG.EMBEDDING_MODEL
    # embedding_model_path = EMBEDDING_MODEL_CONFIG[CFG.EMBEDDING_MODEL]
    # rerank_model_name = CFG.RERANK_MODEL
    # rerank_model_path = None
    # if rerank_model_name:
    #     rerank_model_path = CFG.RERANK_MODEL_PATH or EMBEDDING_MODEL_CONFIG.get(
    #         rerank_model_name
    #     )

    server_init(param, system_app)
    mount_routers(app)
    # model_start_listener = _create_model_start_listener(system_app)
    # initialize_components(
    #     param,
    #     system_app,
    #     embedding_model_name,
    #     embedding_model_path,
    #     rerank_model_name,
    #     rerank_model_path,
    # )
    system_app.on_init()

    # # Migration db storage, so you db models must be imported before this
    # _migration_db_storage(param)

    # model_path = CFG.LLM_MODEL_PATH or LLM_MODEL_CONFIG.get(model_name)
    # # TODO: initialize_worker_manager_in_client as a component register in system_app
    # if not param.light:
    #     print("Model Unified Deployment Mode!")
    #     if not param.remote_embedding:
    #         # Embedding model is running in the same process, set embedding_model_name
    #         # and embedding_model_path to None
    #         embedding_model_name, embedding_model_path = None, None
    #     if not param.remote_rerank:
    #         # Rerank model is running in the same process, set rerank_model_name and
    #         # rerank_model_path to None
    #         rerank_model_name, rerank_model_path = None, None
    #     initialize_worker_manager_in_client(
    #         app=app,
    #         model_name=model_name,
    #         model_path=model_path,
    #         local_port=param.port,
    #         embedding_model_name=embedding_model_name,
    #         embedding_model_path=embedding_model_path,
    #         rerank_model_name=rerank_model_name,
    #         rerank_model_path=rerank_model_path,
    #         start_listener=model_start_listener,
    #         system_app=system_app,
    #     )

    #     CFG.NEW_SERVER_MODE = True
    # else:
    #     # MODEL_SERVER is controller address now
    #     controller_addr = param.controller_addr or CFG.MODEL_SERVER
    #     initialize_worker_manager_in_client(
    #         app=app,
    #         model_name=model_name,
    #         model_path=model_path,
    #         run_locally=False,
    #         controller_addr=controller_addr,
    #         local_port=param.port,
    #         start_listener=model_start_listener,
    #         system_app=system_app,
    #     )
    #     CFG.SERVER_LIGHT_MODE = True

   # mount_static_files(app)

    # Before start, after on_init
    system_app.before_start()
    return param


def run_uvicorn(param: WebServerParameters):
    import uvicorn

    setup_http_service_logging()

    # https://github.com/encode/starlette/issues/617
    cors_app = CORSMiddleware(
        app=app,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )
    uvicorn.run(
        cors_app,
        host=param.host,
        port=param.port,
        log_level=logging_str_to_uvicorn_level(param.log_level),
    )


def run_webserver(param: WebServerParameters = None):
    if not param:
        param = _get_webserver_params()
    initialize_tracer(
        os.path.join(LOGDIR, param.tracer_file),
        system_app=system_app,
        tracer_storage_cls=param.tracer_storage_cls,
    )

    with root_tracer.start_span(
        "run_webserver",
        span_type=SpanType.RUN,
        metadata={
            "run_service": SpanTypeRunName.WEBSERVER,
            "params": _get_dict_from_obj(param),
            "sys_infos": _get_dict_from_obj(get_system_info()),
        },
    ):
        param = initialize_app(param)
        run_uvicorn(param)


if __name__ == "__main__":
    run_webserver()
