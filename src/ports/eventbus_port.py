from abc import ABC, abstractmethod
from typing import Callable

from .base_port import InjectablePort


class EventBusPort(InjectablePort, ABC):
    @abstractmethod
    def emit(self, tenant_id: str, event_name: str, event_data: dict) -> None:
        raise NotImplementedError

    @abstractmethod
    def subscribe(self, event_type: str, function: Callable):
        raise NotImplementedError

    @abstractmethod
    def execute(self):
        raise NotImplementedError

    @abstractmethod
    def __enter__(self):
        raise NotImplementedError

    @abstractmethod
    def __exit__(self, exc_type, exc_value, traceback):
        raise NotImplementedError


class ObserverPort:
    event_name: str

    @classmethod
    def run(cls, app_ctx, event_name: str, event_data: dict):
        raise NotImplementedError

    @classmethod
    def self_subscribe(cls) -> tuple[str, Callable]:
        return (cls.event_name, cls.run)
