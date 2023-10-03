""" Provides main method """
from argparse import ArgumentParser
from .action.list_all import list_all
from .action.find import find


def main() -> int:
    """Main project method"""
    parser = _create_argument_parser()
    arguments = parser.parse_args()
    if ("action" not in arguments) or (arguments.action is None):
        parser.print_help()
        return 1
    action: str = arguments.action
    if action == "list-all":
        list_all()
        return 0
    if action == "find":
        find(arguments.term[0])
        return 0
    return 0


def _create_argument_parser() -> ArgumentParser:
    parser = ArgumentParser(description="TODO")
    action_subparser = parser.add_subparsers(title="action", dest="action")

    description = "Add template to current .gitignore."
    action_parser = action_subparser.add_parser("add", help=description, description=description)
    _add_argument_template(action_parser)
    _add_argument_url(action_parser)

    description = "Create .gitignore with only specified templates."
    action_parser = action_subparser.add_parser("create", help=description, description=description)
    _add_argument_template(action_parser)
    _add_argument_url(action_parser)

    description = "Remove template from current .gitignore."
    action_parser = action_subparser.add_parser("remove", help=description, description=description)
    _add_argument_template(action_parser)
    _add_argument_url(action_parser)

    description = "List all templates in current .gitignore."
    action_parser = action_subparser.add_parser("list", help=description, description=description)

    description = "Update current .gitignore content with provider."
    action_parser = action_subparser.add_parser("update", help=description, description=description)
    _add_argument_url(action_parser)

    description = "List all templates supported by provider."
    action_parser = action_subparser.add_parser("list-all", help=description, description=description)
    _add_argument_url(action_parser)

    description = "List templates who contains searched term."
    action_parser = action_subparser.add_parser("find", help=description, description=description)
    _add_argument_url(action_parser)
    action_parser.add_argument("term", action="store", nargs=1, help="Part of template name to be searched")

    return parser


def _add_argument_template(parser: ArgumentParser):
    parser.add_argument("template", action="store", nargs="+", help="Name of template to be used")


def _add_argument_url(parser: ArgumentParser):
    parser.add_argument("--url", action="store", help="Alternative url for gitignore provider")
