# Generated from the getclean API contract; do not edit.

# isort: skip_file

import typing
from importlib import import_module

if typing.TYPE_CHECKING:
    from .access import Access
    from .access_kind import AccessKind
    from .applied_search_request import AppliedSearchRequest
    from .archive import Archive
    from .block import Block
    from .block_change import BlockChange
    from .block_change_kind import BlockChangeKind
    from .block_page import BlockPage
    from .bound import Bound
    from .bounds import Bounds
    from .candidate import Candidate
    from .candidate_dropped_reason import CandidateDroppedReason
    from .caps import Caps
    from .cell_address import CellAddress
    from .cell_change import CellChange
    from .cell_confidence import CellConfidence
    from .change_side import ChangeSide
    from .comparison import Comparison
    from .comparison_counts import ComparisonCounts
    from .comparison_side import ComparisonSide
    from .contents import Contents
    from .contents_batch import ContentsBatch
    from .contents_batch_counts import ContentsBatchCounts
    from .contents_batch_item import ContentsBatchItem
    from .contents_batch_result import ContentsBatchResult
    from .contents_compact import ContentsCompact
    from .contents_counts import ContentsCounts
    from .contents_highlights import ContentsHighlights
    from .contents_page import ContentsPage
    from .contents_summary import ContentsSummary
    from .contents_upload import ContentsUpload
    from .cost import Cost
    from .coverage_gap import CoverageGap
    from .coverage_gap_target_kind import CoverageGapTargetKind
    from .datasource import Datasource
    from .datasource_access import DatasourceAccess
    from .datasource_page import DatasourcePage
    from .datasource_receipt import DatasourceReceipt
    from .datasource_receipt_reason import DatasourceReceiptReason
    from .datasource_receipt_result_count_kind import DatasourceReceiptResultCountKind
    from .date_precision import DatePrecision
    from .declared import Declared
    from .declared_term import DeclaredTerm
    from .declared_term_as_parsed import DeclaredTermAsParsed
    from .document_pages import DocumentPages
    from .dropped_counts import DroppedCounts
    from .embed import Embed
    from .excerpt import Excerpt
    from .excerpt_origin import ExcerptOrigin
    from .execution import Execution
    from .filter_applied import FilterApplied
    from .filter_state import FilterState
    from .filters_applied import FiltersApplied
    from .hidden_text import HiddenText
    from .highlight import Highlight
    from .image import Image
    from .interpretation import Interpretation
    from .job import Job
    from .job_counts import JobCounts
    from .job_page import JobPage
    from .key_budget import KeyBudget
    from .language_version import LanguageVersion
    from .left_out import LeftOut
    from .limits import Limits
    from .link import Link
    from .link_page import LinkPage
    from .match import Match
    from .media import Media
    from .model_step import ModelStep
    from .money import Money
    from .notice import Notice
    from .operator_applied import OperatorApplied
    from .operator_state import OperatorState
    from .operators_applied import OperatorsApplied
    from .origin import Origin
    from .outcome import Outcome
    from .outcome_kind import OutcomeKind
    from .pictured_page import PicturedPage
    from .policy import Policy
    from .problem import Problem
    from .problem_change import ProblemChange
    from .problem_who_must_act import ProblemWhoMustAct
    from .query_operator import QueryOperator
    from .ranking import Ranking
    from .ranking_merge import RankingMerge
    from .ranking_order import RankingOrder
    from .ranking_priority import RankingPriority
    from .rates import Rates
    from .raw_html import RawHtml
    from .recognized_page import RecognizedPage
    from .redirect import Redirect
    from .retention import Retention
    from .review import Review
    from .review_kind import ReviewKind
    from .safe_search import SafeSearch
    from .schema_fill import SchemaFill
    from .schema_status import SchemaStatus
    from .scope import Scope
    from .screenshot import Screenshot
    from .search import Search
    from .search_batch import SearchBatch
    from .search_batch_counts import SearchBatchCounts
    from .search_batch_item import SearchBatchItem
    from .search_batch_result import SearchBatchResult
    from .search_contents_options import SearchContentsOptions
    from .search_counts import SearchCounts
    from .search_end_reason import SearchEndReason
    from .search_record import SearchRecord
    from .section import Section
    from .section_contents import SectionContents
    from .source import Source
    from .source_compact import SourceCompact
    from .source_independence import SourceIndependence
    from .source_profile import SourceProfile
    from .source_profile_independence import SourceProfileIndependence
    from .source_profile_role import SourceProfileRole
    from .stratum import Stratum
    from .subject_identifier import SubjectIdentifier
    from .table import Table
    from .table_span import TableSpan
    from .time_stamp import TimeStamp
    from .undated import Undated
    from .usage import Usage
    from .version import Version
    from .view import View
    from .violation import Violation
    from .violation_place import ViolationPlace
    from .visitor import Visitor
    from .wording import Wording
    from .wording_language_basis import WordingLanguageBasis
    from .wording_origin import WordingOrigin
_dynamic_imports: typing.Dict[str, str] = {
    "Access": ".access",
    "AccessKind": ".access_kind",
    "AppliedSearchRequest": ".applied_search_request",
    "Archive": ".archive",
    "Block": ".block",
    "BlockChange": ".block_change",
    "BlockChangeKind": ".block_change_kind",
    "BlockPage": ".block_page",
    "Bound": ".bound",
    "Bounds": ".bounds",
    "Candidate": ".candidate",
    "CandidateDroppedReason": ".candidate_dropped_reason",
    "Caps": ".caps",
    "CellAddress": ".cell_address",
    "CellChange": ".cell_change",
    "CellConfidence": ".cell_confidence",
    "ChangeSide": ".change_side",
    "Comparison": ".comparison",
    "ComparisonCounts": ".comparison_counts",
    "ComparisonSide": ".comparison_side",
    "Contents": ".contents",
    "ContentsBatch": ".contents_batch",
    "ContentsBatchCounts": ".contents_batch_counts",
    "ContentsBatchItem": ".contents_batch_item",
    "ContentsBatchResult": ".contents_batch_result",
    "ContentsCompact": ".contents_compact",
    "ContentsCounts": ".contents_counts",
    "ContentsHighlights": ".contents_highlights",
    "ContentsPage": ".contents_page",
    "ContentsSummary": ".contents_summary",
    "ContentsUpload": ".contents_upload",
    "Cost": ".cost",
    "CoverageGap": ".coverage_gap",
    "CoverageGapTargetKind": ".coverage_gap_target_kind",
    "Datasource": ".datasource",
    "DatasourceAccess": ".datasource_access",
    "DatasourcePage": ".datasource_page",
    "DatasourceReceipt": ".datasource_receipt",
    "DatasourceReceiptReason": ".datasource_receipt_reason",
    "DatasourceReceiptResultCountKind": ".datasource_receipt_result_count_kind",
    "DatePrecision": ".date_precision",
    "Declared": ".declared",
    "DeclaredTerm": ".declared_term",
    "DeclaredTermAsParsed": ".declared_term_as_parsed",
    "DocumentPages": ".document_pages",
    "DroppedCounts": ".dropped_counts",
    "Embed": ".embed",
    "Excerpt": ".excerpt",
    "ExcerptOrigin": ".excerpt_origin",
    "Execution": ".execution",
    "FilterApplied": ".filter_applied",
    "FilterState": ".filter_state",
    "FiltersApplied": ".filters_applied",
    "HiddenText": ".hidden_text",
    "Highlight": ".highlight",
    "Image": ".image",
    "Interpretation": ".interpretation",
    "Job": ".job",
    "JobCounts": ".job_counts",
    "JobPage": ".job_page",
    "KeyBudget": ".key_budget",
    "LanguageVersion": ".language_version",
    "LeftOut": ".left_out",
    "Limits": ".limits",
    "Link": ".link",
    "LinkPage": ".link_page",
    "Match": ".match",
    "Media": ".media",
    "ModelStep": ".model_step",
    "Money": ".money",
    "Notice": ".notice",
    "OperatorApplied": ".operator_applied",
    "OperatorState": ".operator_state",
    "OperatorsApplied": ".operators_applied",
    "Origin": ".origin",
    "Outcome": ".outcome",
    "OutcomeKind": ".outcome_kind",
    "PicturedPage": ".pictured_page",
    "Policy": ".policy",
    "Problem": ".problem",
    "ProblemChange": ".problem_change",
    "ProblemWhoMustAct": ".problem_who_must_act",
    "QueryOperator": ".query_operator",
    "Ranking": ".ranking",
    "RankingMerge": ".ranking_merge",
    "RankingOrder": ".ranking_order",
    "RankingPriority": ".ranking_priority",
    "Rates": ".rates",
    "RawHtml": ".raw_html",
    "RecognizedPage": ".recognized_page",
    "Redirect": ".redirect",
    "Retention": ".retention",
    "Review": ".review",
    "ReviewKind": ".review_kind",
    "SafeSearch": ".safe_search",
    "SchemaFill": ".schema_fill",
    "SchemaStatus": ".schema_status",
    "Scope": ".scope",
    "Screenshot": ".screenshot",
    "Search": ".search",
    "SearchBatch": ".search_batch",
    "SearchBatchCounts": ".search_batch_counts",
    "SearchBatchItem": ".search_batch_item",
    "SearchBatchResult": ".search_batch_result",
    "SearchContentsOptions": ".search_contents_options",
    "SearchCounts": ".search_counts",
    "SearchEndReason": ".search_end_reason",
    "SearchRecord": ".search_record",
    "Section": ".section",
    "SectionContents": ".section_contents",
    "Source": ".source",
    "SourceCompact": ".source_compact",
    "SourceIndependence": ".source_independence",
    "SourceProfile": ".source_profile",
    "SourceProfileIndependence": ".source_profile_independence",
    "SourceProfileRole": ".source_profile_role",
    "Stratum": ".stratum",
    "SubjectIdentifier": ".subject_identifier",
    "Table": ".table",
    "TableSpan": ".table_span",
    "TimeStamp": ".time_stamp",
    "Undated": ".undated",
    "Usage": ".usage",
    "Version": ".version",
    "View": ".view",
    "Violation": ".violation",
    "ViolationPlace": ".violation_place",
    "Visitor": ".visitor",
    "Wording": ".wording",
    "WordingLanguageBasis": ".wording_language_basis",
    "WordingOrigin": ".wording_origin",
}


def __getattr__(attr_name: str) -> typing.Any:
    module_name = _dynamic_imports.get(attr_name)
    if module_name is None:
        raise AttributeError(f"No {attr_name} found in _dynamic_imports for module name -> {__name__}")
    try:
        module = import_module(module_name, __package__)
        if module_name == f".{attr_name}":
            return module
        else:
            return getattr(module, attr_name)
    except ImportError as e:
        raise ImportError(f"Failed to import {attr_name} from {module_name}: {e}") from e
    except AttributeError as e:
        raise AttributeError(f"Failed to get {attr_name} from {module_name}: {e}") from e


def __dir__():
    lazy_attrs = list(_dynamic_imports.keys())
    return sorted(lazy_attrs)


__all__ = [
    "Access",
    "AccessKind",
    "AppliedSearchRequest",
    "Archive",
    "Block",
    "BlockChange",
    "BlockChangeKind",
    "BlockPage",
    "Bound",
    "Bounds",
    "Candidate",
    "CandidateDroppedReason",
    "Caps",
    "CellAddress",
    "CellChange",
    "CellConfidence",
    "ChangeSide",
    "Comparison",
    "ComparisonCounts",
    "ComparisonSide",
    "Contents",
    "ContentsBatch",
    "ContentsBatchCounts",
    "ContentsBatchItem",
    "ContentsBatchResult",
    "ContentsCompact",
    "ContentsCounts",
    "ContentsHighlights",
    "ContentsPage",
    "ContentsSummary",
    "ContentsUpload",
    "Cost",
    "CoverageGap",
    "CoverageGapTargetKind",
    "Datasource",
    "DatasourceAccess",
    "DatasourcePage",
    "DatasourceReceipt",
    "DatasourceReceiptReason",
    "DatasourceReceiptResultCountKind",
    "DatePrecision",
    "Declared",
    "DeclaredTerm",
    "DeclaredTermAsParsed",
    "DocumentPages",
    "DroppedCounts",
    "Embed",
    "Excerpt",
    "ExcerptOrigin",
    "Execution",
    "FilterApplied",
    "FilterState",
    "FiltersApplied",
    "HiddenText",
    "Highlight",
    "Image",
    "Interpretation",
    "Job",
    "JobCounts",
    "JobPage",
    "KeyBudget",
    "LanguageVersion",
    "LeftOut",
    "Limits",
    "Link",
    "LinkPage",
    "Match",
    "Media",
    "ModelStep",
    "Money",
    "Notice",
    "OperatorApplied",
    "OperatorState",
    "OperatorsApplied",
    "Origin",
    "Outcome",
    "OutcomeKind",
    "PicturedPage",
    "Policy",
    "Problem",
    "ProblemChange",
    "ProblemWhoMustAct",
    "QueryOperator",
    "Ranking",
    "RankingMerge",
    "RankingOrder",
    "RankingPriority",
    "Rates",
    "RawHtml",
    "RecognizedPage",
    "Redirect",
    "Retention",
    "Review",
    "ReviewKind",
    "SafeSearch",
    "SchemaFill",
    "SchemaStatus",
    "Scope",
    "Screenshot",
    "Search",
    "SearchBatch",
    "SearchBatchCounts",
    "SearchBatchItem",
    "SearchBatchResult",
    "SearchContentsOptions",
    "SearchCounts",
    "SearchEndReason",
    "SearchRecord",
    "Section",
    "SectionContents",
    "Source",
    "SourceCompact",
    "SourceIndependence",
    "SourceProfile",
    "SourceProfileIndependence",
    "SourceProfileRole",
    "Stratum",
    "SubjectIdentifier",
    "Table",
    "TableSpan",
    "TimeStamp",
    "Undated",
    "Usage",
    "Version",
    "View",
    "Violation",
    "ViolationPlace",
    "Visitor",
    "Wording",
    "WordingLanguageBasis",
    "WordingOrigin",
]
