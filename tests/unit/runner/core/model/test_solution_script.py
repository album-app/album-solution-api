import argparse
from pathlib import Path

from album.runner.core.model.solution_script import SolutionScript
from tests.test_unit_common import TestUnitCommon


class TestSolutionScript(TestUnitCommon):

    def test__add_parser_argument(self):
        solution = None
        args = {
            'name': 'myname'
        }
        parser = argparse.ArgumentParser()
        SolutionScript._add_parser_argument(solution, parser, args)
        args = parser.parse_args(["--myname", "bla"])
        self.assertIn('myname', args)
        self.assertIsInstance(args.myname, str)

        args = {
            'name': 'myname',
            'type': 'integer'
        }
        parser = argparse.ArgumentParser()
        SolutionScript._add_parser_argument(solution, parser, args)
        args = parser.parse_args(["--myname", "0"])
        self.assertIn('myname', args)
        self.assertIsInstance(args.myname, int)

        args = {
            'name': 'myname',
            'type': 'boolean'
        }
        parser = argparse.ArgumentParser()
        SolutionScript._add_parser_argument(solution, parser, args)
        args = parser.parse_args(["--myname", "false"])
        self.assertIn('myname', args)
        self.assertIsInstance(args.myname, bool)
        self.assertEqual(args.myname, False)

        args = {
            'name': 'myname',
            'type': 'string'
        }
        parser = argparse.ArgumentParser()
        SolutionScript._add_parser_argument(solution, parser, args)
        args = parser.parse_args(["--myname", "bla"])
        self.assertIn('myname', args)
        self.assertIsInstance(args.myname, str)

        args = {
            'name': 'myname',
            'type': 'file'
        }
        parser = argparse.ArgumentParser()
        SolutionScript._add_parser_argument(solution, parser, args)
        args = parser.parse_args(["--myname", "0"])
        self.assertIn('myname', args)
        self.assertIsInstance(args.myname, Path)

        args = {
            'name': 'myname',
            'type': 'directory'
        }
        parser = argparse.ArgumentParser()
        SolutionScript._add_parser_argument(solution, parser, args)
        args = parser.parse_args(["--myname", "0"])
        self.assertIn('myname', args)
        self.assertIsInstance(args.myname, Path)

    def test__add_parser_argument_python_type_names(self):
        solution = None
        args = {
            'name': 'myname',
            'type': 'int'
        }
        parser = argparse.ArgumentParser()
        SolutionScript._add_parser_argument(solution, parser, args)
        args = parser.parse_args(["--myname", "5"])
        self.assertEqual(args.myname, 5)

        args = {
            'name': 'myname',
            'type': 'bool'
        }
        parser = argparse.ArgumentParser()
        SolutionScript._add_parser_argument(solution, parser, args)
        args = parser.parse_args(["--myname", "false"])
        self.assertIs(args.myname, False)

        args = {
            'name': 'myname',
            'type': 'str'
        }
        parser = argparse.ArgumentParser()
        SolutionScript._add_parser_argument(solution, parser, args)
        args = parser.parse_args(["--myname", "5"])
        self.assertEqual(args.myname, "5")

    def test__add_parser_argument_unknown_type(self):
        args = {
            'name': 'myname',
            'type': 'integr'
        }
        parser = argparse.ArgumentParser()
        with self.assertRaises(ValueError) as context:
            SolutionScript._add_parser_argument(None, parser, args)
        self.assertIn("The argument myname has the unknown type 'integr'.", str(context.exception))

