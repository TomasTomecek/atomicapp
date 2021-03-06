#!/usr/bin/python

from atomicapp.run import Run
from atomicapp.install import Install
from atomicapp.create import Create
from atomicapp import params
import os, sys, json
from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
import logging
import anymarkup #FIXME

from atomicapp import set_logging
from atomicapp.constants import ANSWERS_FILE, MAIN_FILE, __ATOMICAPPVERSION__, __NULECULESPECVERSION__

def cli_install(args):
    install = Install(**vars(args))
    install.install()

def cli_create(args):
    ac = Create(args.NAME, args.schema, args.dryrun)
    ac.create()

def cli_build(args):
    if os.path.isfile(os.path.join(os.getcwd(), MAIN_FILE)):
        data = anymarkup.parse_file(os.path.join(os.getcwd(), MAIN_FILE))
        ac = Create(data["id"], args.dryrun)
        ac.build(args.TAG)

def cli_run(args):
    ae = Run(**vars(args))
    ae.run()

class CLI():
    def __init__(self):
        self.parser = ArgumentParser(prog='atomicapp', description='This will install and run an atomicapp, a containerized application conforming to the Nulecule Specification', formatter_class=RawDescriptionHelpFormatter)

    def set_arguments(self):

        self.parser.add_argument("-V", "--version", action='version', version='atomicapp %s, Nulecule Specification %s' % (__ATOMICAPPVERSION__, __NULECULESPECVERSION__), help="show the version and exit.") # TODO refactor program name and version to some globals
        self.parser.add_argument("-v", "--verbose", dest="verbose", default=False, action="store_true", help="Verbose output mode.")
        self.parser.add_argument("-q", "--quiet", dest="quiet", default=False, action="store_true", help="Quiet output mode.")

        self.parser.add_argument("--dry-run", dest="dryrun", default=False, action="store_true", help="Don't actually call provider. The commands that should be run will be sent to stdout but not run.")

        subparsers = self.parser.add_subparsers(dest="action")

        parser_create = subparsers.add_parser("create")
        parser_create.add_argument("--schema", default=None, help="Schema for the app spec")
        parser_create.add_argument("NAME", help="App name")
        parser_create.set_defaults(func=cli_create)

    
        parser_run = subparsers.add_parser("run")
        self.parser.add_argument("-a", "--answers", dest="answers", default=os.path.join(os.getcwd(), ANSWERS_FILE), help="Path to %s" % ANSWERS_FILE)
        parser_run.add_argument("--write-answers", dest="answers_output", help="A file which will contain anwsers provided in interactive mode")
        parser_run.add_argument("--ask", default=False, action="store_true", help="Ask for params even if the defaul value is provided")
        parser_run.add_argument("APP", help="Path to the directory where the image is installed.")
        parser_run.set_defaults(func=cli_run)
    
        parser_install = subparsers.add_parser("install")

        parser_install.add_argument("--no-deps", dest="nodeps", default=False, action="store_true", help="Skip pulling dependencies of the app")
        parser_install.add_argument("-u", "--update", dest="update", default=False, action="store_true", help="Re-pull images and overwrite existing files")
        parser_install.add_argument("--destination", dest="target_path", default=None, help="Destination directory for install")
        parser_install.add_argument("APP",  help="Application to run. This is a container image or a path that contains the metadata describing the whole application.")
        parser_install.set_defaults(func=cli_install)
    
        parser_build = subparsers.add_parser("build")
        parser_build.add_argument("TAG", nargs="?", default=None, help="Name of the image containing your app")
        parser_build.set_defaults(func=cli_build)

    def run(self):
        self.set_arguments()
        args = self.parser.parse_args()
        if args.verbose:
            set_logging(level=logging.DEBUG)
        elif args.quiet:
            set_logging(level=logging.WARNING)
        else:
            set_logging(level=logging.INFO)
        try:
            args.func(args)
        except AttributeError:
            if hasattr(args, 'func'):
                raise
            else:
                self.parser.print_help()
        except KeyboardInterrupt:
            pass
        except Exception as ex:
            if True or args.verbose:
                raise
            else:
                logger.error("Exception caught: %s", repr(ex))   



def main():
    cli = CLI()
    cli.run()

if __name__ == '__main__':
    main()
