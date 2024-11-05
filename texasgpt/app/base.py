import logging
import os
import signal
import sys
import threading
from dataclasses import dataclass, field
from typing import Optional

from texasgpt._private.config import Config # type: ignore
from texasgpt.component import SystemApp
# from texasgpt.storage import DBType
from texasgpt.util.parameter_utils import BaseServerParameters

ROOT_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(ROOT_PATH)

logger = logging.getLogger(__name__)


def signal_handler(sig, frame):
    print("in order to avoid chroma db atexit problem")
    os._exit(0)


def server_init(param: "WebServerParameters", system_app: SystemApp):
    # logger.info(f"args: {args}")
    # init config
    cfg = Config()
    cfg.SYSTEM_APP = system_app
    # Initialize db storage first
    # _initialize_db_storage(param, system_app)

    # load_native_plugins(cfg)
    signal.signal(signal.SIGINT, signal_handler)


@dataclass
class WebServerParameters(BaseServerParameters):
    host: Optional[str] = field(
        default="0.0.0.0", metadata={"help": "Webserver deploy host"}
    )
    port: Optional[int] = field(
        default=None, metadata={"help": "Webserver deploy port"}
    )
    daemon: Optional[bool] = field(
        default=False, metadata={"help": "Run Webserver in background"}
    )
    controller_addr: Optional[str] = field(
        default=None,
        metadata={
            "help": "The Model controller address to connect. If None, read model "
            "controller address from environment key MODEL_SERVER."
        },
    )
    model_name: str = field(
        default=None,
        metadata={
            "help": "The default model name to use. If None, read model name from "
            "environment key LLM_MODEL.",
            "tags": "fixed",
        },
    )
    share: Optional[bool] = field(
        default=False,
        metadata={
            "help": "Whether to create a publicly shareable link for the interface. "
            "Creates an SSH tunnel to make your UI accessible from anywhere. "
        },
    )
    # remote_embedding: Optional[bool] = field(
    #     default=False,
    #     metadata={
    #         "help": "Whether to enable remote embedding models. If it is True, you need"
    #         " to start a embedding model through texasgpt start worker --worker_type "
    #         "text2vec --model_name xxx --model_path xxx"
    #     },
    # )
    # remote_rerank: Optional[bool] = field(
    #     default=False,
    #     metadata={
    #         "help": "Whether to enable remote rerank models. If it is True, you need"
    #         " to start a rerank model through texasgpt start worker --worker_type "
    #         "text2vec --rerank --model_name xxx --model_path xxx"
    #     },
    # )

    light: Optional[bool] = field(default=False, metadata={"help": "enable light mode"})
    log_file: Optional[str] = field(
        default="texasgpt_webserver.log",
        metadata={
            "help": "The filename to store log",
        },
    )
    tracer_file: Optional[str] = field(
        default="texasgpt_webserver_tracer.jsonl",
        metadata={
            "help": "The filename to store tracer span records",
        },
    )
    tracer_storage_cls: Optional[str] = field(
        default=None,
        metadata={
            "help": "The storage class to storage tracer span records",
        },
    )
    # disable_alembic_upgrade: Optional[bool] = field(
    #     default=False,
    #     metadata={
    #         "help": "Whether to disable alembic to initialize and upgrade database metadata",
    #     },
    # )
    # awel_dirs: Optional[str] = field(
    #     default=None,
    #     metadata={
    #         "help": "The directories to search awel files, split by ,",
    #     },
    # )
    default_thread_pool_size: Optional[int] = field(
        default=None,
        metadata={
            "help": "The default thread pool size, If None, "
            "use default config of python thread pool",
        },
    )