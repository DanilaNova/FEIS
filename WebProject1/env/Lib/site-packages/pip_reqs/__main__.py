from __future__ import print_function

import argparse
import os
import sys

from .client import CompilationError, ResolutionError, WheelsproxyClient
from .compat import get_requirement_tracker, setup_global_pip_state
from .parser import RequirementsParser


LOCAL_DEPS_MESSAGE = [
    "",
    "# The following packages are available only locally.",
    "# Their dependencies *have* been considered while",
    "# resolving the full dependency tree:",
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-w", "--wheelsproxy", default=os.environ.get("WHEELSPROXY_URL")
    )
    subparsers = parser.add_subparsers()

    compile_parser = subparsers.add_parser("compile")
    compile_parser.set_defaults(func=compile)
    compile_parser.add_argument("infile", nargs="?", default="requirements.in")
    compile_parser.add_argument(
        "outfile", nargs="?", default="requirements.txt"
    )

    resolve_parser = subparsers.add_parser("resolve")
    resolve_parser.set_defaults(func=resolve)
    resolve_parser.add_argument(
        "infile", nargs="?", default="requirements.txt"
    )
    resolve_parser.add_argument(
        "outfile", nargs="?", default="requirements.urls"
    )

    args = parser.parse_args()

    if not args.wheelsproxy:
        print(
            (
                "Either the --wheelsproxy argument or a WHEELSPROXY_URL "
                "environment variable are required."
            ),
            file=sys.stderr,
        )

    client = WheelsproxyClient(args.wheelsproxy)
    with setup_global_pip_state():
        args.func(client, args)


def compile(client, args):
    with get_requirement_tracker() as req_tracker:
        parser = RequirementsParser(req_tracker=req_tracker)
        ext_reqs, local_reqs = parser.parse(args.infile)
        try:
            compiled_reqs = client.compile("\n".join(ext_reqs))
        except CompilationError as e:
            print(e.args[0], file=sys.stderr)
            sys.exit(1)
        with open(args.outfile, "w") as fh:
            fh.write(compiled_reqs)
            if local_reqs:
                fh.write("\n".join(LOCAL_DEPS_MESSAGE + local_reqs))
            fh.write("\n")


def resolve(client, args):
    with open(args.infile, "r") as fh:
        reqs = fh.read()

    try:
        urls = client.resolve(reqs)
    except ResolutionError as e:
        print(e.args[0], file=sys.stderr)
        sys.exit(1)

    with open(args.outfile, "w") as fh:
        fh.write(urls)


if __name__ == "__main__":
    main()
