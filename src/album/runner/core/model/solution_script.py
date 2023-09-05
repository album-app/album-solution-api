import argparse
import sys
from argparse import ArgumentError
from pathlib import Path

from album.runner import album_logging
from album.runner.album_logging import get_active_logger, configure_logging
from album.runner.core.api.model.solution import ISolution
from album.runner.core.model.solution import Solution


class SolutionScript:

    @staticmethod
    def make_action(solution, mydest):
        class CustomAction(argparse.Action):
            def __call__(self, parser, namespace, values, option_string=None):
                setattr(namespace, mydest, solution.get_arg(mydest)['action'](values))

        return CustomAction

    @staticmethod
    def get_script_logging_formatter_str():
        return '%(levelname)-7s %(name)s - %(message)s'

    @staticmethod
    def get_script_logging_formatter_regex():
        regex_log_level = 'DEBUG|INFO|WARNING|ERROR'
        return r'(%s)\s+([\s\S]+) - ([\s\S]+)?' % regex_log_level

    @staticmethod
    def trigger_solution_goal(solution, goal, package_path=None, installation_base_path=None, environment_path=None):
        SolutionScript.api_access(solution, package_path, installation_base_path, environment_path)
        parser = None
        if solution.setup().args:
            append_arguments = (goal == Solution.Action.RUN) or (goal == Solution.Action.TEST)
            if append_arguments:
                parser = SolutionScript.append_arguments(solution)
        if goal == Solution.Action.INSTALL:
            solution.setup().install()
        if goal == Solution.Action.UNINSTALL:
            solution.setup().uninstall()
        if goal == Solution.Action.RUN:
            SolutionScript.execute_run_action(solution)
        if goal == Solution.Action.TEST:
            if 'pre_test' in solution.setup():
                d = solution.setup().pre_test()
            else:
                d = {}
            if d is None:
                d = {}
            sys.argv = sys.argv + ["=".join([c, d[c]]) for c in d]

            # parse args again after pre_test() routine if necessary.
            if parser and "args" in solution.setup().keys():
                args = parser.parse_args()
                solution.set_args(args)

            SolutionScript.execute_run_action(solution)
            solution.setup().test()

    @staticmethod
    def execute_run_action(solution):
        get_active_logger().info("Starting %s" % solution.setup().name)
        if solution.setup().run and callable(solution.setup().run):
            solution.setup().run()
        else:
            get_active_logger().warn(
                "No \"run\" routine configured for solution \"%s\"." % solution.setup().name)
        if solution.setup().close and callable(solution.setup().close):
            solution.setup().close()
        get_active_logger().info("Finished %s" % solution.setup().name)

    @staticmethod
    def init_logging():
        configure_logging("script", loglevel=album_logging.to_loglevel(album_logging.get_loglevel_name()),
                          stream_handler=sys.stdout,
                          formatter_string=SolutionScript.get_script_logging_formatter_str())

    @staticmethod
    def api_access(solution: ISolution, package_path, installation_base_path, environment_path):
        if package_path:
            solution.installation().set_package_path(package_path)
            sys.path.insert(0, str(solution.installation().package_path()))
        if installation_base_path:
            solution.installation().set_installation_path(installation_base_path)
            # add app_path to syspath
            sys.path.insert(0, str(solution.installation().app_path()))
        if environment_path:
            solution.installation().set_environment_path(environment_path)

    @staticmethod
    def append_arguments(solution: ISolution):
        parser = None
        if isinstance(solution.setup().args, str):
            SolutionScript._handle_args_string(solution.setup().args)
        else:
            parser = SolutionScript._handle_args_list(solution)
        return parser

    @staticmethod
    def _handle_args_string(args):
        # pass through to module
        if args == 'pass-through':
            get_active_logger().info(
                'Argument parsing not specified in album solution. Passing arguments through...'
            )
        else:
            message = 'Argument keyword \'%s\' not supported!' % args
            get_active_logger().error(message)
            raise ArgumentError(argument=args, message=message)

    @staticmethod
    def _handle_args_list(solution: ISolution):
        parser = argparse.ArgumentParser(description='album run %s' % solution.setup().name)
        for arg in solution.setup().args:
            SolutionScript._add_parser_argument(solution, parser, arg)
        args = parser.parse_args()
        solution.set_args(args)
        return parser

    @staticmethod
    def _add_parser_argument(solution, parser, arg):
        keys = arg.keys()

        if 'default' in keys and 'action' in keys:
            get_active_logger().warning("Default values cannot be automatically set when an action is provided! "
                                        "Ignoring default values...")

        args = {}
        if 'action' in keys:
            args['action'] = SolutionScript.make_action(solution, arg['name'])
        if 'default' in keys:
            args['default'] = arg['default']
        if 'description' in keys:
            args['help'] = arg['description']
        if 'type' in keys:
            args['type'] = SolutionScript._parse_type(arg['type'])
        if 'required' in keys:
            args['required'] = arg['required']
        parser.add_argument('--%s' % arg['name'], **args)

    @staticmethod
    def _get_action_class_name(name):
        class_name = '%sAction' % name.capitalize()
        return class_name

    @staticmethod
    def strtobool(val):
        val = val.lower()
        if val in ('y', 'yes', 't', 'true', 'on', '1'):
            return True
        elif val in ('n', 'no', 'f', 'false', 'off', '0'):
            return False
        else:
            raise ValueError("invalid truth value %r" % (val,))

    @staticmethod
    def _parse_type(type_str):
        if type_str == 'string':
            return str
        if type_str == 'file':
            return Path
        if type_str == 'directory':
            return Path
        if type_str == 'integer':
            return int
        if type_str == 'float':
            return float
        if type_str == 'boolean':
            return SolutionScript.strtobool
