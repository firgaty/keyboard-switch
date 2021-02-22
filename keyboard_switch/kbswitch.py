#!/usr/bin/env python
# PYZSHCOMPLETE_OK
# PYTHON_ARGCOMPLETE_OK
import argparse
import json
import re
import subprocess

import argcomplete
import pyzshcomplete
from xdg import XDG_CONFIG_HOME

CONFIG_PATH = XDG_CONFIG_HOME.joinpath("keyboard-switch")
SAVE_FILE_PATH = CONFIG_PATH.joinpath("mappings")
CURRENT_FILE_PATH = CONFIG_PATH.joinpath("current")

MAPPINGS = {}
MAPPING_ORDER = []
CURRENT_MAPPING = [0]


def extract_layout(string: str) -> dict[str]:
    results = re.findall(
        r"^model:\s*(\S+)$|^layout:\s*(\S+)$|^variant:\s*(\S+)$|^options:\s*(\S+)$",
        string,
        re.MULTILINE,
    )

    out = {"model": "", "layout": "", "variant": "", "option": ""}

    for r in results:
        model, layout, variant, options = r

        if model != "":
            out["model"] = model
        elif layout != "":
            out["layout"] = layout
        elif variant != "":
            out["variant"] = variant
        elif options != "":
            out["option"] = options

    return out


def load_from_file():
    with open(SAVE_FILE_PATH, "r") as file:
        for e in map(json.loads, file.readlines()):
            add_mapping(e)


def save_to_file():
    with open(SAVE_FILE_PATH, "w") as file:
        for mapping in MAPPING_ORDER:
            file.write(json.dumps(MAPPINGS[mapping]) + "\n")


def save_current():
    with open(CURRENT_FILE_PATH, "w") as file:
        file.write(str(CURRENT_MAPPING[0]))


def load_current():
    with open(CURRENT_FILE_PATH, "r") as file:
        CURRENT_MAPPING[0] = int(file.readline().strip())


def add_mapping(mapping: dict[str, str], order: int = -1) -> None:
    MAPPINGS[mapping["name"]] = mapping

    if mapping['name'] in MAPPING_ORDER:
        return

    if order < 0 or order >= len(MAPPING_ORDER):
        MAPPING_ORDER.append(mapping["name"])
    else:
        MAPPING_ORDER.insert(order, mapping["name"])


def reorder(from_: int, to: int) -> None:
    length = len(MAPPING_ORDER)

    if from_ < length:
        m = MAPPINGS[MAPPING_ORDER.pop(from_)]
        add_mapping(m, to)
    save_to_file()
    CURRENT_MAPPING[0] = 0
    save_current()


def add_current_layout(name: str, order: int = -1, current: bool = False) -> None:
    result = subprocess.run(["setxkbmap", "-v", "9"], stdout=subprocess.PIPE)
    out = extract_layout(result.stdout.decode("utf-8"))
    out["name"] = name
    add_mapping(out, order)
    set_mapping(order)
    save_to_file()


def set_mapping(order: int) -> None:
    if order < 0:
        order = len(MAPPING_ORDER) - 1

    if order < len(MAPPING_ORDER):
        set_layout(MAPPING_ORDER[order])
        CURRENT_MAPPING[0] = order
        save_current()


def set_mapping_name(name: str) -> None:
    if name not in MAPPINGS:
        return

    for i, m in enumerate(MAPPING_ORDER):
        if m == name:
            set_mapping(i)
            return


def remove_mapping(order: int) -> None:
    if order >= len(MAPPING_ORDER):
        return

    MAPPING_ORDER.pop(order)

    if order >= len(MAPPING_ORDER):
        order = 0

    save_to_file()
    save_current()


def remove_mapping_name(mapping_name: str) -> None:
    if mapping_name not in MAPPINGS:
        return

    for i, m in enumerate(MAPPING_ORDER):
        if m == mapping_name:
            remove_mapping(i)
            return


def set_layout(name: str) -> None:
    if name not in MAPPINGS:
        return

    m = MAPPINGS[name]

    prog = ["setxkbmap"]

    for e in ["model", "layout", "variant", "option"]:
        prog.append(f"-{e}")
        prog.append(f"{m[e]}")

    subprocess.run(prog)


def print_mapping(name: str) -> None:
    if MAPPING_ORDER == []:
        print_empty()
        return
    
    m = MAPPINGS[name]
    print(
        f"{name}\n  model:\t{m['model']}\n  layout:\t{m['layout']}"
        + f"\n  variant:\t{m['variant']}\n  options:\t{m['option']}"
    )


def print_order() -> None:
    if MAPPING_ORDER == []:
        print_empty()
        return
    
    for i, m in enumerate(MAPPING_ORDER):
        if CURRENT_MAPPING[0] == i:
            print(f"+ {i:>2} {m}")
        else:
            print(f"  {i:>2} {m}")


def print_empty() -> None:
    print("No keyboard mapping were found.\nAdd a new mapping using `kbswitch -a <name>`.\nSee help with `kbswitch -h`.")

def notify_current():
    import gi

    gi.require_version("Notify", "0.7")

    from gi.repository import Notify
    
    mapping = MAPPINGS[MAPPING_ORDER[CURRENT_MAPPING[0]]]

    Notify.init("keyboard-switch")
    Msg = Notify.Notification.new(
        "keyboard-switch", f"{mapping['name']}\n[{mapping['layout']}]", "dialog-information"
    )
    Msg.show()


def next_mapping() -> None:
    set_mapping((CURRENT_MAPPING[0] + 1) % len(MAPPING_ORDER))


def previous_mapping() -> None:
    set_mapping((CURRENT_MAPPING[0] - 1 + len(MAPPING_ORDER)) % len(MAPPING_ORDER))

def sub_main(args):
    if not SAVE_FILE_PATH.exists():
        CONFIG_PATH.mkdir(parents=True, exist_ok=True)
    else:
        load_from_file()

    if CURRENT_FILE_PATH.exists():
        load_current()

    if args["current"]:
        print_mapping(MAPPING_ORDER[CURRENT_MAPPING[0]])
        return

    if args["list"]:
        print_order()
        return

    if args["details"]:
        for m in MAPPING_ORDER:
            print_mapping(m)
        return

    if args["add"]:
        add_current_layout(args["add"][0], current=True)
        return

    if len(MAPPING_ORDER) <= 0:
        return

    if args["remove_number"]:
        remove_mapping(int(args["remove_number"][0]))
        return
    if args["remove"]:
        remove_mapping_name(args["remove"][0])
        return
    if args['order']:
        reorder(args['order'][0], args['order'][1])
        return
    
    if args["next"]:
        next_mapping()
    elif args['previous']:
        previous_mapping()
    elif args["set_number"]:
        set_mapping(int(args["set_number"][0]))
    elif args["set"]:
        set_mapping_name(args["set"][0])

    if args["notify"]:
        notify_current()


def main():
    parser = argparse.ArgumentParser(prog="kbswitch")

    parser.add_argument("-n", "--next", help="Next mapping", action="store_true")
    parser.add_argument("-p", "--previous", help="Previous mapping", action="store_true")
    parser.add_argument(
        "-s",
        "--set",
        help="Set current mapping to NAME",
        nargs=1,
        metavar="NAME",
        type=str,
    )
    parser.add_argument(
        "-S",
        "--set-number",
        help="Set current mapping to NUMBER",
        nargs=1,
        metavar="N",
        type=int,
    )
    parser.add_argument(
        "-a",
        "--add",
        help="Add current mapping with name NAME",
        nargs=1,
        metavar="NAME",
        type=str,
    )
    parser.add_argument(
        "-r",
        "--remove",
        help="Remove mapping with name NAME",
        nargs=1,
        metavar="NAME",
        type=str,
    )
    parser.add_argument(
        "-R",
        "--remove-number",
        help="Remove mapping with order N",
        nargs=1,
        metavar="N",
        type=int,
    )
    parser.add_argument(
        "-o",
        "--order",
        help="Reorder mapping at place FROM to place TO",
        nargs=2,
        metavar=("FROM", "TO"),
        type=int,
    )
    parser.add_argument(
        "-c",
        "--current",
        help="Print current layout",
        action="store_true",
    )
    parser.add_argument(
        "-l",
        "--list",
        help="Lists layouts in order",
        action="store_true",
    )
    parser.add_argument(
        "-d",
        "--details",
        help="Print layouts in order with details",
        action="store_true",
    )
    parser.add_argument(
        "--notify",
        help="Prints change to notification window using libnotify",
        action="store_true",
    )

    argcomplete.autocomplete(parser)
    pyzshcomplete.autocomplete(parser)
    args = vars(parser.parse_args())
    sub_main(args)


if __name__ == "__main__":
    main()