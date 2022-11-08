from pathlib import Path
from typing import List

from album.runner.core.api.model.coordinates import ICoordinates
from album.runner.core.api.model.solution import ISolution
from album.runner.core.default_values_runner import DefaultValuesRunner
from album.runner.core.model.coordinates import Coordinates


class Solution(ISolution):
    """Encapsulates a album solution configuration."""

    class Setup(ISolution.ISetup):

        def __init__(self, attrs=None):
            """sets object attributes

            Args:
                attrs:
                    Dictionary containing the attributes.
            """
            if attrs:
                super().__init__(attrs)
            else:
                super().__init__()

        def __str__(self, indent=2):
            s = '\n'
            for attr in self.__dict__:
                for i in range(0, indent):
                    s += '\t'
                s += (attr + ':\t' + str(getattr(self, attr))) + '\n'
            return s

    class Installation (ISolution.IInstallation):
        def __init__(self):
            super().__init__()
            # API keywords
            self._installation_path = None
            self._environment_path = None
            self._package_path = None

        def environment_path(self) -> Path:
            return self._environment_path

        def user_cache_path(self) -> Path:
            return self._installation_path.joinpath(DefaultValuesRunner.solution_user_cache_prefix.value)

        def internal_cache_path(self) -> Path:
            return self._installation_path.joinpath(DefaultValuesRunner.solution_internal_cache_prefix.value)

        def package_path(self) -> Path:
            return self._package_path

        def installation_path(self) -> Path:
            return self._installation_path

        def data_path(self) -> Path:
            return self._installation_path.joinpath(DefaultValuesRunner.solution_data_prefix.value)

        def app_path(self) -> Path:
            return self._installation_path.joinpath(DefaultValuesRunner.solution_app_prefix.value)

        def set_environment_path(self, path: Path):
            self._environment_path = path

        def set_package_path(self, package_path: Path):
            self._package_path = package_path

        def set_installation_path(self, solution_base_path: Path):
            self._installation_path = solution_base_path

    def __init__(self, attrs=None):
        self._installation = Solution.Installation()
        self._setup = Solution.Setup(attrs)
        self._coordinates = Coordinates(attrs['group'], attrs['name'], attrs['version'])
        self._args = None
        self._script = None

    def setup(self) -> ISolution.ISetup:
        return self._setup

    def installation(self) -> ISolution.IInstallation:
        return self._installation

    def coordinates(self) -> ICoordinates:
        return self._coordinates

    def script(self) -> Path:
        return self._script

    def get_arg(self, k):
        """Get a specific named argument for this album if it exists."""
        matches = [arg for arg in self._setup.args if arg['name'] == k]
        return matches[0]

    def get_identifier(self) -> str:
        identifier = '_'.join([self._setup.group, self._setup.name, self._setup.version])
        return identifier

    def set_script(self, script: str):
        self._script = script

    def __eq__(self, other):
        return isinstance(other, Solution) and \
               other.coordinates() == self._coordinates

    def set_args(self, args: List):
        self._args = args

    def args(self) -> List:
        return self._args
