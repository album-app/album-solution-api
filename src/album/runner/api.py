"""This module provides the API for the album runner."""
import json
import os
import sys
import tarfile
from pathlib import Path
from typing import Any, Dict, Optional
from urllib.request import urlretrieve

from album.runner.album_logging import configure_logging, get_active_logger, to_loglevel
from album.runner.core.api.model.solution import ISolution
from album.runner.core.default_values_runner import DefaultValuesRunner
from album.runner.core.model.solution import Solution
from album.runner.core.model.solution_script import SolutionScript


def download_if_not_exists(url, file_name):
    """Download resource if not already cached and returns local resource path.

    Args:
        url: The URL of the download.
        file_name: The local filename of the download.

    Returns: The path to the downloaded resource.

    """
    download_dir = get_cache_path()
    download_path = download_dir.joinpath(file_name)

    if download_path.exists():
        get_active_logger().info(f"Found cache of {url}: {download_path}...")
        return download_path
    if not download_dir.exists():
        download_dir.mkdir(parents=True)

    get_active_logger().info(f"Downloading {url} to {download_path}...")

    urlretrieve(url, download_path)

    return download_path


def extract_tar(in_tar, out_dir):
    """Extract a TAR file to a directory.

    Args:
        out_dir: Directory where the TAR file should be extracted to
        in_tar: TAR file to be extracted
    """
    out_path = Path(out_dir)

    if not out_path.exists():
        out_path.mkdir(parents=True)

    get_active_logger().info(f"Extracting {in_tar} to {out_dir}...")

    my_tar = tarfile.open(in_tar)
    my_tar.extractall(out_dir)
    my_tar.close()


def get_environment_name() -> str:
    """Return the name of the environment the solution runs in."""
    get_active_logger().warning(
        "Get_environment_name is deprecated. Use get_environment_path instead."
    )
    return str(get_environment_path())


def get_environment_path() -> Path:
    """Return the path of the environment the solution runs in."""
    active_solution = get_active_solution()
    res = active_solution.installation().environment_path()
    return Path(res) if res else res


def get_data_path() -> Path:
    """Return the data path provided for the solution."""
    active_solution = get_active_solution()
    res = active_solution.installation().data_path()
    return Path(res) if res else res


def get_package_path() -> Path:
    """Return the package path provided for the solution."""
    active_solution = get_active_solution()
    res = active_solution.installation().package_path()
    return Path(res) if res else res


def get_app_path() -> Path:
    """Return the app path provided for the solution."""
    active_solution = get_active_solution()
    res = active_solution.installation().app_path()
    return Path(res) if res else res


def get_cache_path() -> Path:
    """Return the cache path provided for the solution."""
    active_solution = get_active_solution()
    res = active_solution.installation().user_cache_path()
    return Path(res) if res else res


def get_resources_dict(os_specific: bool = False) -> Dict[str, Any]:
    """Return the resource files from a json as a dictionary and adds the download paths to the dictionary.

    Args:
        os_specific: If True, all resources are returned, otherwise only the installed resources
        meant for the current OS are returned.
    """
    resources_dict = {}
    active_solution = get_active_solution()
    cache_path = active_solution.installation().internal_cache_path()

    # get catalog name from active_solution use
    coords = active_solution.coordinates()
    resource_json_name = "_".join(
        [coords.group(), coords.name(), coords.version(), "resource_file.json"]
    )

    # read json file from cache path
    file = cache_path.joinpath(resource_json_name)
    if file.exists():
        # read dict from json file
        with open(file) as f:
            resources_dict = json.load(f)
    if os_specific:
        # filter the resources that have the OS key as the current OS
        resources_dict["resources"] = {
            key: value
            for key, value in resources_dict.get("resources", {}).items()
            if value.get("os") == sys.platform
        }
    return resources_dict


def in_target_environment() -> bool:
    """Give the boolean information whether current python is the python from the album target environment.

    Returns:
        True when current active python is the album target environment else False.

    """
    active_solution = get_active_solution()

    return (
        True
        if sys.executable.startswith(
            str(active_solution.installation().environment_path())
        )
        else False
    )


def get_args():
    """Get the parsed argument from the solution call.

    Returns:
        The namespace object of the parsed arguments.

    """
    active_solution = get_active_solution()

    return active_solution.args()


# Global variable for tracking the currently active solution. Do not use this
# directly instead use get_active_solution()
_active_solution = []

enc = sys.getfilesystemencoding()


def setup(**attrs):
    """Configure a solution for the use by the main album tool."""
    global _active_solution
    loglevel = os.getenv(DefaultValuesRunner.env_variable_logger_level.value, "INFO")
    configure_logging(
        "script",
        loglevel=to_loglevel(loglevel),
        stream_handler=sys.stdout,
        formatter_string=SolutionScript.get_script_logging_formatter_str(),
    )
    next_solution = Solution(attrs)
    push_active_solution(next_solution)
    goal = os.getenv(DefaultValuesRunner.env_variable_action.value, None)
    if goal:
        goal = Solution.Action[goal]
    package_path = os.getenv(
        DefaultValuesRunner.env_variable_package.value, os.path.abspath(__file__)
    )
    if package_path:
        package_path = Path(package_path)
    installation_base_path = os.getenv(
        DefaultValuesRunner.env_variable_installation.value, None
    )
    if installation_base_path:
        installation_base_path = Path(installation_base_path)
    environment_path = os.getenv(
        DefaultValuesRunner.env_variable_environment.value, None
    )
    if environment_path:
        environment_path = Path(environment_path)
    if goal:
        next_solution.installation().set_package_path(package_path)
        SolutionScript.trigger_solution_goal(
            next_solution, goal, package_path, installation_base_path, environment_path
        )


def push_active_solution(solution_object: ISolution):
    """Pop a solution to the _active_solution stack."""
    global _active_solution
    _active_solution.insert(0, solution_object)


def get_parent_solution() -> Optional[ISolution]:
    """Return the parent solution of the currently active solution."""
    global _active_solution
    if len(_active_solution) > 1:
        return _active_solution[1]
    return None


def get_active_solution() -> Optional[ISolution]:
    """Return the currently active solution, which is defined globally."""
    global _active_solution
    if len(_active_solution) > 0:
        return _active_solution[0]
    return None


def pop_active_solution():
    """Pop the currently active solution from the _active_solution stack."""
    global _active_solution

    if len(_active_solution) > 0:
        return _active_solution.pop(0)
    else:
        return None
