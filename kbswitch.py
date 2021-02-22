import subprocess
import argparse
from xdg import XDG_CONFIG_HOME
import json

# from typing import Union
import re

CONFIG_PATH = XDG_CONFIG_HOME.joinpath("kbswitch")
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


def remove_mapping(mapping_name: str) -> None:
    for i, m in enumerate(MAPPINGS):
        if m["name"] == mapping_name:
            MAPPINGS.pop(i)


def add_mapping(mapping: dict[str, str], order: int = -1) -> None:
    if mapping["name"] in MAPPINGS:
        MAPPINGS[mapping["name"]] = mapping
        return

    MAPPINGS[mapping["name"]] = mapping

    if order < 0 or order > len(MAPPING_ORDER):
        MAPPING_ORDER.append(mapping["name"])
    else:
        MAPPING_ORDER[order] = mapping["name"]


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
    m = MAPPINGS[name]
    print(
        f"{name}\n  model:\t{m['model']}\n  layout:\t{m['layout']}"
        + f"\n  variant:\t{m['variant']}\n  options:\t{m['option']}"
    )


def print_order() -> None:
    for i, m in enumerate(MAPPING_ORDER):
        if CURRENT_MAPPING[0] == i:
            print(f"+ {i:>2} {m}")
        else:
            print(f"  {i:>2} {m}")


def next_mapping() -> None:
    set_mapping((CURRENT_MAPPING[0] + 1) % len(MAPPING_ORDER))


def main_(args):
    if not SAVE_FILE_PATH.exists():
        CONFIG_PATH.mkdir(parents=True, exist_ok=True)
    else:
        load_from_file()

    if CURRENT_FILE_PATH.exists():
        load_current()

    if args["current"]:
        print_mapping(MAPPING_ORDER[CURRENT_MAPPING[0]])
        return

    if args["print"]:
        print_order()
        return

    if args["details"]:
        for m in MAPPING_ORDER:
            print_mapping(m)
        return

    if args["next"]:
        next_mapping()
        return

    if args["set_number"]:
        set_mapping(int(args["set_number"][0]))
        return

    if args["add"]:
        add_current_layout(args["add"][0], current=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="kbswitch")

    parser.add_argument("-n", "--next", help="Next mapping", action="store_true")
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
        metavar="NUMBER",
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
        "-p",
        "--print",
        help="Print layouts order",
        action="store_true",
    )
    parser.add_argument(
        "-d",
        "--details",
        help="Print layouts in order with details",
        action="store_true",
    )

    args = vars(parser.parse_args())
    main_(args)