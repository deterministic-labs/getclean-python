# Generated from the getclean API contract; do not edit.

import typing

CandidateDroppedReason = typing.Union[
    typing.Literal[
        "not_relevant",
        "undated",
        "max_per_domain",
        "blocked_domain",
        "outside_allowed",
        "source_kind",
        "source_independence",
        "folded_copy",
        "phrase_check",
        "exclusion_check",
        "beyond_max_candidates",
    ],
    typing.Any,
]
