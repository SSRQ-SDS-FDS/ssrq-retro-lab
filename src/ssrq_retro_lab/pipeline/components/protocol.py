from typing import Any, Protocol, runtime_checkable
from result import Result


class ComponentError(Exception):
    def __init__(self, message: str):
        self.message = message


@runtime_checkable
class Component(Protocol):
    _allowed_retries: int
    _name: str
    _repeat_previous: bool

    def invoke(self, input: Any) -> Result[Any, ComponentError]:
        ...
