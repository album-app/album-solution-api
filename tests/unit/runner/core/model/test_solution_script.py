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

