import argparse
import os
import sys
import unittest
from pathlib import Path
from unittest import mock

from album.runner.api import get_args, get_active_solution
from album.runner.core.model.solution import Solution
from album.runner.core.default_values_runner import DefaultValuesRunner
from album.runner.core.model.solution_script import SolutionScript
from tests.test_unit_common import TestUnitCommon


class TestIntegrationScriptCreator(TestUnitCommon):

    def test__solutionaction__init__(self):
        solution = mock.create_autospec(Solution)
        action = SolutionScript.make_action(solution, "dest")
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
    import sys
    for p in sys.path:
        if not isinstance(p, str):
            raise RuntimeError(f"Element {str(p)} in sys.path is not a string. It is of type: {type(p)}")

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
        SolutionScript.trigger_solution_goal(active_solution, Solution.Action.RUN, package_path=tmp_dir, installation_base_path=tmp_dir)

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


class TestSolutionScriptRequiredArguments(TestUnitCommon):
    """A required argument may be supplied by pre_test().

    Before this, trigger_solution_goal() parsed the command line for the TEST goal before
    calling pre_test(), so any argument declared required made argparse exit with "the
    following arguments are required" -- the values pre_test() was about to return never
    got the chance to satisfy it. Solutions with a genuine self-test therefore had to declare
    required=False and say "(required)" in the description instead, which hides the
    requirement from every tool that reads the metadata.

    The fix must not take away what pre_test() could always do: read the arguments the caller
    passed, and the defaults, through get_args() and adapt them. So the command line is still
    parsed before pre_test(), only without enforcing `required`, and an invalid one still
    fails before pre_test() runs.
    """

    def setUp(self):
        super().setUp()
        # setup() triggers a goal immediately when the runner's action variable is set;
        # a neighbouring test that exported it would make exec() below parse the command
        # line before this test has arranged it. Clear it so each test stands alone.
        os.environ.pop(DefaultValuesRunner.env_variable_action.value, None)

    def test_test_pretest_supplies_required_argument(self):
        solution_content = """
from album.runner.api import setup, get_args

def pre_test():
    return {"--a1": "fromPreTest"}

def run():
    assert get_args().a1 == "fromPreTest", get_args().a1

setup(**{
            'group': "tsg",
            'name': "tsn",
            'version': "tsv",
            'pre_test': pre_test,
            'run': run,
            'test': lambda: True,
            'args': [{"name": "a1", "description": "", "required": True}]
        })
"""
        sys.argv = ['']
        exec(solution_content)
        active_solution = get_active_solution()
        active_solution.set_script(solution_content)

        # Used to raise SystemExit(2) from argparse before pre_test() was ever called.
        SolutionScript.trigger_solution_goal(active_solution, Solution.Action.TEST)
        self.assertEqual('fromPreTest', get_args().a1)

    def test_test_without_pretest_still_enforces_required_argument(self):
        """Deferring the parse must not turn a genuinely missing argument into a pass."""
        solution_content = """
from album.runner.api import setup

setup(**{
            'group': "tsg",
            'name': "tsn",
            'version': "tsv",
            'test': lambda: True,
            'args': [{"name": "a1", "description": "", "required": True}]
        })
"""
        sys.argv = ['']
        exec(solution_content)
        active_solution = get_active_solution()
        active_solution.set_script(solution_content)

        with self.assertRaises(SystemExit):
            SolutionScript.trigger_solution_goal(active_solution, Solution.Action.TEST)

    def test_run_still_enforces_required_argument(self):
        """The RUN goal is untouched: no pre_test() exists to supply anything."""
        solution_content = """
from album.runner.api import setup

setup(**{
            'group': "tsg",
            'name': "tsn",
            'version': "tsv",
            'args': [{"name": "a1", "description": "", "required": True}]
        })
"""
        sys.argv = ['']
        exec(solution_content)
        active_solution = get_active_solution()
        active_solution.set_script(solution_content)

        with self.assertRaises(SystemExit):
            SolutionScript.trigger_solution_goal(active_solution, Solution.Action.RUN)

    def test_pass_through_arguments_still_work_for_the_test_goal(self):
        solution_content = """
from album.runner.api import setup

setup(**{
            'group': "tsg",
            'name': "tsn",
            'version': "tsv",
            'test': lambda: True,
            'args': 'pass-through'
        })
"""
        sys.argv = ['']
        exec(solution_content)
        active_solution = get_active_solution()
        active_solution.set_script(solution_content)

        SolutionScript.trigger_solution_goal(active_solution, Solution.Action.TEST)

    def test_test_pretest_can_read_and_adapt_command_line_arguments(self):
        """pre_test() sees what the caller passed, and the values it returns win."""
        solution_content = """
from album.runner.api import setup, get_args

def pre_test():
    return {"--a1": get_args().a1 + "Adapted", "--a2": str(get_args().a2 * 2)}

setup(**{
            'group': "tsg",
            'name': "tsn",
            'version': "tsv",
            'pre_test': pre_test,
            'run': lambda: None,
            'test': lambda: True,
            'args': [{"name": "a1", "description": "", "required": True},
                     {"name": "a2", "description": "", "type": "integer", "default": 1}]
        })
"""
        sys.argv = ['', '--a1=fromCommandLine', '--a2=5']
        exec(solution_content)
        active_solution = get_active_solution()
        active_solution.set_script(solution_content)

        SolutionScript.trigger_solution_goal(active_solution, Solution.Action.TEST)
        self.assertEqual('fromCommandLineAdapted', get_args().a1)
        self.assertEqual(10, get_args().a2)

    def test_test_pretest_sees_defaults_and_a_required_argument_not_yet_given(self):
        """Nothing passed: pre_test() gets the defaults, and None for what it must supply."""
        solution_content = """
from album.runner.api import setup, get_args

def pre_test():
    assert get_args().a1 is None, get_args().a1
    assert get_args().a2 == 1, get_args().a2
    return {"--a1": "fixture"}

setup(**{
            'group': "tsg",
            'name': "tsn",
            'version': "tsv",
            'pre_test': pre_test,
            'run': lambda: None,
            'test': lambda: True,
            'args': [{"name": "a1", "description": "", "required": True},
                     {"name": "a2", "description": "", "type": "integer", "default": 1}]
        })
"""
        sys.argv = ['']
        exec(solution_content)
        active_solution = get_active_solution()
        active_solution.set_script(solution_content)

        SolutionScript.trigger_solution_goal(active_solution, Solution.Action.TEST)
        self.assertEqual('fixture', get_args().a1)
        self.assertEqual(1, get_args().a2)

    def test_test_refuses_an_invalid_command_line_before_pretest_runs(self):
        """A typo on the command line fails fast, not after pre_test() did its work."""
        solution_content = """
from album.runner.api import setup

def pre_test():
    raise AssertionError("pre_test() ran although the command line was invalid")

setup(**{
            'group': "tsg",
            'name': "tsn",
            'version': "tsv",
            'pre_test': pre_test,
            'test': lambda: True,
            'args': [{"name": "a1", "description": ""}]
        })
"""
        sys.argv = ['', '--typo=1']
        exec(solution_content)
        active_solution = get_active_solution()
        active_solution.set_script(solution_content)

        with self.assertRaises(SystemExit):
            SolutionScript.trigger_solution_goal(active_solution, Solution.Action.TEST)


if __name__ == '__main__':
    unittest.main()
