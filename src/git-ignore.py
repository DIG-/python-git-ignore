#!/usr/bin/python
# -*- coding: utf-8 -*-

from enum import Enum, auto
import getopt
import os
import sys
import urllib.request

verbose = False

IGNORE_FILE = ".gitignore"
IGNORE_BAK = IGNORE_FILE + ".bak"
IGNORE_DOWN = IGNORE_FILE + ".down"
URL = "https://gitignore.io/api/"

CONTENT_START_BLOCK = "# Created by http"
CONTENT_END_BLOCK = "# End of http"


class Mode(Enum):
    ADD = auto()
    CREATE = auto()
    LIST = auto()
    REMOVE = auto()
    UPDATE = auto()


def usage():
    print("Usage:\t" + sys.argv[0] + " [options] action [terms...]")
    print("Actions:")
    print("  -a,--add\t\tAdd terms to current .gitignore")
    print("  -c,--create\t\tCreate new .gitignore with terms")
    print("  -l,--list\t\tList terms from current .gitignore")
    print("  -r,--remove\t\tRemove terms from current .gitignore")
    print("  -u,--update\t\tJust update current .gitignore")
    print("Terms:")
    print("  List terms. Accept multiple value or comma separated values")
    print("  Required for action add, create and remove")
    print("Options:")
    print("  -h,--help\t\tShow help")
    print("  --url=URL\t\tChange url of download")
    print("  -v,--verbose\t\tPrint more messages")
    print("  --version\t\tShow version")


def print_v(*args):
    global verbose
    if verbose:
        print(*args)


def split_term(term):
    output = []
    for s in term.split(","):
        output.append(s.strip())
    return output


def split_terms(terms):
    if isinstance(terms, str):
        return set(split_term(terms))
    output = []
    for term in terms:
        output.extend(split_term(term))
    return set(output)


def download_file(url, filename):
    try:
        with urllib.request.urlopen(
            urllib.request.Request(url, headers={"User-Agent": "Python"})
        ) as r:
            with open(filename, "wb") as f:
                f.write(r.read())
        return True
    except BaseException as e:
        print_v("Download failed")
        print_v(str(e))
        return False


def trimmed_copy(_input, output, stop=None):
    line: str = _input.readline()
    started = False
    count = 0
    while line:
        if not line.strip():
            count += 1
        else:
            if stop != None and stop(line):
                return started

            while count > 0 and started:
                count -= 1
                output.write("\n")

            count = 0
            started = True
            output.write(line)

        line: str = _input.readline()
    return started


def main():
    global verbose
    try:
        opts, terms = getopt.getopt(
            sys.argv[1:],
            "achlruv",
            [
                "add",
                "create",
                "help",
                "list",
                "remove",
                "update",
                "url=",
                "verbose",
                "version",
            ],
        )
    except getopt.GetoptError as err:
        print(err)
        usage()
        sys.exit(2)

    mode: Mode = None
    url = URL
    for o, a in opts:
        if o == "--version":
            print("git-ignore poc")
            sys.exit()
        elif o == "--url=":
            url = a
        elif o in ("-v", "--verbose"):
            verbose = True
        elif o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-a", "--add"):
            if mode != None:
                print("Can not run multiple actions")
                sys.exit(1)
            mode = Mode.ADD
        elif o in ("-c", "--create"):
            if mode != None:
                print("Can not run multiple actions")
                sys.exit(1)
            mode = Mode.CREATE
        elif o in ("-l", "--list"):
            if mode != None:
                print("Can not run multiple actions")
                sys.exit(1)
            mode = Mode.LIST
        elif o in ("-r", "--remove"):
            if mode != None:
                print("Can not run multiple actions")
                sys.exit(1)
            mode = Mode.REMOVE
        elif o in ("-u", "--update"):
            if mode != None:
                print("Can not run multiple actions")
                sys.exit(1)
            mode = Mode.UPDATE
        else:
            assert False, "Unhandled option"

    if mode == None:
        print("Require action. Use --help to see how to use.")
        sys.exit(1)

    terms = split_terms(terms)
    if not terms:
        if mode == Mode.ADD or mode == Mode.CREATE or mode == Mode.REMOVE:
            print("Require terms. Use --help to see how to use.")
            sys.exit(1)
    elif mode == Mode.UPDATE:
        print("Useless fill terms in update")
        terms = set()
    elif mode == Mode.LIST:
        print("Useless fill terms in list")
        terms = set()

    if mode != Mode.CREATE:
        print_v("Extract current terms")
        try:
            file = open(IGNORE_FILE, "r")
            found = []
            for line in file.readlines():
                if line.startswith(CONTENT_START_BLOCK):
                    found = split_terms(line.split("/")[-1])
                    break
            file.close()
            if not found:
                if mode == Mode.ADD:
                    print_v("Can not find terms in current file. Skip!")
                else:
                    print("Can not find terms in current file")
                    return 1

            if mode == Mode.LIST:
                for term in found:
                    print(term)
                return 0

            elif mode == Mode.UPDATE:
                terms = found

            elif mode == Mode.ADD:
                terms.update(found)

            elif mode == Mode.REMOVE:
                for term in terms:
                    if term in found:
                        found.remove(term)
                    else:
                        print(
                            "Term '" + term + "' not found in current .gitignore. Skip!"
                        )
                terms = found

        except FileNotFoundError:
            print("Can not find .gitignore file")
            sys.exit(1)
        except BaseException as e:
            print("Error reading .gitignore")
            print(e)
            sys.exit(1)

    print_v("Sort terms")
    terms = sorted(terms)
    print("Download .gitignore")
    if not download_file(url + ",".join(terms), IGNORE_DOWN):
        print("Download failed")
        return 1

    if mode == Mode.CREATE:
        print_v("Apply download .gitignore as current")
        if os.path.exists(IGNORE_FILE):
            os.remove(IGNORE_FILE)
        os.rename(IGNORE_DOWN, IGNORE_FILE)
        return 0

    print_v("Backup current .gitignore")
    os.rename(IGNORE_FILE, IGNORE_BAK)

    old_file = open(IGNORE_BAK, "r")
    new_file = open(IGNORE_FILE, "w")

    print_v("Copy before section from old .gitignore")
    if trimmed_copy(
        old_file, new_file, lambda line: line.startswith(CONTENT_START_BLOCK)
    ):
        new_file.write("\n")

    print_v("Copy downloaded .gitignore")
    down_file = open(IGNORE_DOWN, "r")
    trimmed_copy(down_file, new_file)
    down_file.close()

    print_v("Seek to after section from old .gitignore")
    line = old_file.readline()
    while line:
        if line.startswith(CONTENT_END_BLOCK):
            break
        line = old_file.readline()

    print_v("Copy after section from old .gitignore")
    new_file.write("\n")
    trimmed_copy(old_file, new_file)

    old_file.close()
    new_file.close()

    print_v("Clear temporary files")
    os.remove(IGNORE_BAK)
    os.remove(IGNORE_DOWN)

    print(".gitignore updated")


if __name__ == "__main__":
    main()
