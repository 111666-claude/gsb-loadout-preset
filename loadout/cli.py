"""命令行入口：跑装备预设样例。"""

import argparse

from .core import Armory


def build_parser():
    parser = argparse.ArgumentParser(prog="loadout-preset", description="装备预设")
    parser.add_argument("--sample", default="atomic",
                        help="atomic / idempotent / diff / slot / scan")
    return parser


def build_catalog():
    return [
        {"id": "sword", "slot": "weapon", "min_level": 1, "stats": {"power": 100}},
        {"id": "dagger", "slot": "weapon", "min_level": 1, "stats": {"power": 60}},
        {"id": "shield", "slot": "offhand", "min_level": 5, "stats": {"armor": 40}},
        {"id": "helm", "slot": "head", "min_level": 1, "stats": {"armor": 10}},
    ]


def main(argv=None):
    args = build_parser().parse_args(argv)
    if args.sample == "atomic":
        armory = Armory(build_catalog(), player_level=1)
        armory.equipped["weapon"] = "sword"
        armory.presets["p"] = {"weapon": "dagger", "offhand": "shield"}
        ok = armory.apply("p")
        print("ok=%s weapon=%s"
              % (str(ok).lower(), armory.equipped.get("weapon")))
    elif args.sample == "idempotent":
        armory = Armory(build_catalog(), player_level=10)
        armory.presets["p"] = {"weapon": "sword"}
        armory.apply("p")
        armory.apply("p")
        print("power=%d" % armory.stats().get("power", 0))
    elif args.sample == "diff":
        armory = Armory(build_catalog(), player_level=10)
        armory.presets["empty"] = {}
        armory.equipped["weapon"] = "sword"
        armory.apply("empty")
        added, removed, changed = armory.diff("empty")
        print("removed=%d equipped=%d" % (len(removed), len(armory.equipped)))
    elif args.sample == "slot":
        armory = Armory(build_catalog(), player_level=10)
        armory.presets["p"] = {"weapon": "helm"}
        print("ok=%s" % str(armory.apply("p")).lower())
    elif args.sample == "scan":
        catalog = build_catalog() + [
            {"id": "filler-%d" % i, "slot": "weapon", "min_level": 1, "stats": {}}
            for i in range(2996)
        ]
        armory = Armory(catalog, player_level=10)
        armory.presets["p"] = {"weapon": "filler-2995"}
        for _ in range(3000):
            armory.apply("p")
        print("scanned=%d" % armory.scanned)
    else:
        raise SystemExit("需要 --sample atomic|idempotent|diff|slot|scan")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
