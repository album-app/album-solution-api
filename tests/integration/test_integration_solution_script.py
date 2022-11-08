import argparse
import os
import sys
import unittest
from pathlib import Path
from unittest import mock

from album.runner.api import get_args, get_active_solution
from album.runner.core.model.solution import Solution
from album.runner.core.model.solution_script import SolutionScript
from tests.test_unit_common import TestUnitCommon


class TestIntegrationScriptCreator(TestUnitCommon):

    def test__solutionaction__init__(self):
        solution = mock.create_autospec(Solution)
        action = SolutionScript.make_action(solution, "", "dest")
        parser = argparse.ArgumentParser(description='album run %s' % solution.setup().name)
        parser.add_argument("test", action=action)

    def test_get_args(self):
        solution_content = """
from album.runner.api import setup

setup(**{
            'group': "tsg",
            'name': "tsn",
            'version': "tsv",
            'args': [{"name": "a1", "description": ""}]
        })
"""
        sys.argv = ['']
        exec(solution_content)
        active_solution = get_active_solution()
        active_solution.set_script(solution_content)

        SolutionScript.trigger_solution_goal(active_solution, Solution.Action.RUN)

        # test no arg
        sys.argv = ['']
        SolutionScript.trigger_solution_goal(active_solution, Solution.Action.RUN)
        args = get_args()
        self.assertIsNone(args.a1)

        # test with arg
        sys.argv = ['', '--a1', 'aValue']
        SolutionScript.trigger_solution_goal(active_solution, Solution.Action.RUN)
        args = get_args()
        self.assertEqual('aValue', args.a1)

    def test_get_args_boolean(self):
        solution_content = """
from album.runner.api import setup

setup(**{
            'group': "tsg",
            'name': "tsn",
            'version': "tsv",
            'args': [{"name": "a1", "type": "boolean", "default": False}]
        })
"""
        sys.argv = ['']
        exec(solution_content)
        active_solution = get_active_solution()
        active_solution.set_script(solution_content)

        # test no arg
        SolutionScript.trigger_solution_goal(active_solution, Solution.Action.RUN)
        args = get_args()
        self.assertFalse(args.a1)

        # test with arg
        sys.argv = ['', '--a1', 'True']
        SolutionScript.trigger_solution_goal(active_solution, Solution.Action.RUN)
        args = get_args()
        self.assertEqual(True, args.a1)

    def test_test_without_pretest(self):
        solution_content = """
from album.runner.api import setup

setup(**{
            'group': "tsg",
            'name': "tsn",
            'version': "tsv",
            'test': lambda: True,
            'args': [{"name": "a1", "description": ""}]
        })
"""
        sys.argv = ['']
        exec(solution_content)
        active_solution = get_active_solution()
        active_solution.set_script(solution_content)

        SolutionScript.trigger_solution_goal(active_solution, Solution.Action.TEST)

    def test_test_pretest_without_return(self):
        solution_content = """
from album.runner.api import setup

def pre_test():
    print("jej")

setup(**{
            'group': "tsg",
            'name': "tsn",
            'version': "tsv",
            'pre_test': pre_test,
            'test': lambda: True,
            'args': [{"name": "a1", "description": ""}]
        })
"""
        sys.argv = ['']
        exec(solution_content)
        active_solution = get_active_solution()
        active_solution.set_script(solution_content)

        SolutionScript.trigger_solution_goal(active_solution, Solution.Action.TEST)

    def test_local_import(self):
        solution_content = """
from album.runner.api import setup
def run():
    try:
        from import_test import test_val
    except ModuleNotFoundError:
        raise ModuleNotFoundError("Could not import local module")

setup(**{
            'group': "tsg",
            'name': "tsn",
            'version': "tsv",
            'run': run,
            'args': [{"name": "a1", "description": ""}]
        })
"""
        import_content = "test_val = \"GGEZ\""

        tmp_dir = Path(self.tmp_dir.name)
        tmp_import = Path(tmp_dir).joinpath("import_test.py")
        tmp_import.write_text(import_content)

        sys.argv = ['']
        exec(solution_content)
        active_solution = get_active_solution()
        active_solution.set_script(solution_content)

        SolutionScript.trigger_solution_goal(active_solution, Solution.Action.RUN, package_path=self.tmp_dir.name)

    def test_default_arg(self):
        solution_content = """
from album.runner.api import setup
def run():
    from album.runner.api import get_args
    print(get_args())

setup(**{
            'group': "tsg",
            'name': "tsn",
            'version': "tsv",
            'run': run,
            'args': [{"name": "a1", "description": "", "default": "test"}]
        })
"""
        sys.argv = ['']
        exec(solution_content)
        active_solution = get_active_solution()
        active_solution.installation().set_package_path(self.tmp_dir.name)
        active_solution.set_script(solution_content)

        SolutionScript.trigger_solution_goal(active_solution, Solution.Action.RUN)

    def test_solution_api(self):
        solution_content = """
from album.runner.api import setup
def run():
    from album.runner.api import get_app_path, get_data_path, get_cache_path, get_package_path
    print(get_cache_path())
    if not get_app_path():
        raise RuntimeError()
    if not get_data_path():
        raise RuntimeError()
    if not get_cache_path():
        raise RuntimeError()
    if not get_package_path():
        raise RuntimeError()

setup(**{
            'group': "tsg",
            'name': "tsn",
            'version': "tsv",
            'run': run
        })
"""
        sys.argv = ['']
        exec(solution_content)
        active_solution = get_active_solution()
        active_solution.set_script(solution_content)
        tmp_dir = Path(self.tmp_dir.name)
        active_solution.installation().set_installation_path(tmp_dir)
        active_solution.installation().set_package_path(tmp_dir)
        SolutionScript.trigger_solution_goal(active_solution, Solution.Action.RUN)

    def test_solution_api_env_variables(self):
        solution_content = """
from album.runner.api import setup
def run():
    from album.runner.api import get_app_path, get_data_path, get_cache_path, get_package_path, get_environment_path
    if not get_app_path() or not str(get_app_path()).endswith("app"):
        raise RuntimeError("wrong app path: %s" % get_app_path())
    if not get_data_path() or not str(get_data_path()).endswith("data"):
        raise RuntimeError("wrong data path: %s" % get_data_path())
    if not get_cache_path() or not str(get_cache_path()).endswith("ucache"):
        raise RuntimeError("wrong cache path: %s" % get_cache_path())
    if not get_package_path() or not str(get_package_path()).endswith("pck"):
        raise RuntimeError("wrong package path: %s" % get_package_path())

setup(**{
            'group': "tsg",
            'name': "tsn",
            'version': "tsv",
            'run': run
        })
"""
        sys.argv = ['']
        tmp_dir = Path(self.tmp_dir.name)
        os.environ['ALBUM_SOLUTION_ENVIRONMENT'] = str(tmp_dir.joinpath('env'))
        os.environ['ALBUM_SOLUTION_INSTALLATION'] = str(tmp_dir.joinpath('install'))
        os.environ['ALBUM_SOLUTION_PACKAGE'] = str(tmp_dir.joinpath('pck'))
        os.environ['ALBUM_SOLUTION_ACTION'] = "RUN"
        exec(solution_content)


if __name__ == '__main__':
    unittest.main()
