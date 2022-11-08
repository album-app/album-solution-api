from abc import ABCMeta, abstractmethod
from enum import Enum
from pathlib import Path
from typing import List

from album.runner.core.api.model.coordinates import ICoordinates


class ISolution:

    __metaclass__ = ABCMeta

    class Action(Enum):
        NO_ACTION = 0
        INSTALL = 1
        RUN = 2
        TEST = 3
        UNINSTALL = 4

    class ISetup(dict):
        __metaclass__ = ABCMeta
        __getattr__ = dict.get
        __setattr__ = dict.__setitem__
        __delattr__ = dict.__delitem__

    class IInstallation:
        __metaclass__ = ABCMeta

        @abstractmethod
        def environment_path(self) -> Path:
            raise NotImplementedError

        @abstractmethod
        def user_cache_path(self) -> Path:
            raise NotImplementedError

        @abstractmethod
        def internal_cache_path(self) -> Path:
            raise NotImplementedError

        @abstractmethod
        def package_path(self) -> Path:
            raise NotImplementedError

        @abstractmethod
        def data_path(self) -> Path:
            raise NotImplementedError

        @abstractmethod
        def app_path(self) -> Path:
            raise NotImplementedError

        @abstractmethod
        def installation_path(self) -> Path:
            raise NotImplementedError

        @abstractmethod
        def set_environment_path(self, path: Path):
            raise NotImplementedError

        @abstractmethod
        def set_package_path(self, package_path: Path):
            raise NotImplementedError

        @abstractmethod
        def set_installation_path(self, solution_base_path: Path):
            raise NotImplementedError

    @abstractmethod
    def setup(self) -> ISetup:
        raise NotImplementedError

    @abstractmethod
    def installation(self) -> IInstallation:
        raise NotImplementedError

    @abstractmethod
    def coordinates(self) -> ICoordinates:
        raise NotImplementedError

    @abstractmethod
    def script(self) -> Path:
        raise NotImplementedError

    @abstractmethod
    def args(self) -> List:
        raise NotImplementedError

    @abstractmethod
    def get_arg(self, name: str):
        raise NotImplementedError

    @abstractmethod
    def get_identifier(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def set_script(self, script: str):
        raise NotImplementedError

    @abstractmethod
    def set_args(self, args: List):
        raise NotImplementedError
