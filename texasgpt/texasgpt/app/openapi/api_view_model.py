import socket
import time
import uuid
from enum import Enum
from typing import Any, Dict, Generic, List, Literal, Optional, TypeVar

from texasgpt._private.pydantic import BaseModel, ConfigDict, Field, model_to_dict

T = TypeVar("T")


class Result(BaseModel, Generic[T]):
    success: bool
    err_code: Optional[str] = None
    err_msg: Optional[str] = None
    data: Optional[T] = None
    host_name: Optional[str] = socket.gethostname()

    @classmethod
    def succ(cls, data: T = None):
        return Result(success=True, err_code=None, err_msg=None, data=data)

    @classmethod
    def failed(cls, code: str = "E000X", msg=None):
        return Result(success=False, err_code=code, err_msg=msg, data=None)

    def to_dict(self) -> Dict[str, Any]:
        return model_to_dict(self)

