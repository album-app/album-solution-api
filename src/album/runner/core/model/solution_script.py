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
            if goal == Solution.Action.RUN:
                parser = SolutionScript.append_arguments(solution)
            elif goal == Solution.Action.TEST:
                # For the test goal the arguments come from the command line and from
                # pre_test(), which has not run at this point. Enforcing `required` here
                # made argparse exit with "the following arguments are required: ..." for
                # every solution that marks an argument required -- before pre_test() had
                # any chance to provide it. Solutions worked around this by declaring
                # required=False and writing "(required)" into the description, which hid
                # the requirement from every consumer of the metadata. So parse the command
                # line without enforcing `required`: pre_test() can read get_args() and
                # adapt what the caller passed, and an invalid command line still fails
                # before pre_test() runs. The parse that enforces `required` happens below,
                # after pre_test()'s values are on the command line.
                parser = SolutionScript.build_parser(solution)
                if parser is not None:
                    lenient_parser = SolutionScript.build_parser(solution, enforce_required=False)
                    solution.set_args(lenient_parser.parse_args())
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

            # The parse that counts for the test goal: pre_test()'s arguments now follow
            # the caller's, so they win, and a required argument pre_test() supplies is
            # satisfied rather than fatal.
            if parser is not None:
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
    def build_parser(solution: ISolution, enforce_required=True):
        """The argument parser for a solution's declared arguments, built but not yet parsed.

        Returns None when the solution declares its arguments as a string ('pass-through'),
        which is validated the same way append_arguments() validates it. Separated from the
        parse so that the test goal can enforce required arguments only after pre_test() has
        run. With enforce_required=False, no argument is marked required: the test goal parses
        the command line that way for pre_test(), which may still supply them.
        """
        if isinstance(solution.setup().args, str):
            SolutionScript._handle_args_string(solution.setup().args)
            return None
        parser = argparse.ArgumentParser(description='album run %s' % solution.setup().name)
        for arg in solution.setup().args:
            SolutionScript._add_parser_argument(solution, parser, arg, enforce_required)
        return parser

    @staticmethod
    def _handle_args_list(solution: ISolution):
        parser = SolutionScript.build_parser(solution)
        args = parser.parse_args()
        solution.set_args(args)
        return parser

    @staticmethod
    def _add_parser_argument(solution, parser, arg, enforce_required=True):
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
        if 'required' in keys and enforce_required:
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
