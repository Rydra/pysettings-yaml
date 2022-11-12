from typing import Dict

from deepmerge import Merger

default_merger = Merger(
    # pass in a list of tuple, with the
    # strategies you are looking to apply
    # to each type.
    [(dict, ["merge"])],
    # next, choose the fallback strategies,
    # applied to all other types:
    ["override"],
    # finally, choose the strategies in
    # the case where the types conflict:
    ["override"],
)


def merge(*dicts: Dict) -> Dict:
    if len(dicts) < 2:
        raise Exception("Need at least two dicts to merge")

    base: Dict = {}
    for dict in dicts:
        default_merger.merge(base, dict)

    return base
