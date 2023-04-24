from dataclasses import dataclass, fields, is_dataclass
from datetime import date, datetime, time, timedelta
from enum import Enum
from typing import Any, List, Optional, _GenericAlias
from urllib.parse import parse_qs


class Operations(Enum):
    ASC = "order ASC"
    DESC = "order DESC"
    OFFSET = "offset"
    LIMIT = "limit"
    PAGE = "page"
    EQ = "equal"
    NEQ = "not equal"
    LT = "lower than"
    LTE = "lower than equal"
    GT = "greater than"
    GTE = "greater than equal"
    IN = "in"
    NIN = "not in"
    CONTAINS = "contains"
    NCONTAINS = "not contains"
    STARTSWITH = "starts with"
    NSTARTSWITH = "not starts with"
    ENDSWITH = "ends with"
    NENDSWITH = "not ends with"


@dataclass
class Filter:
    field: str
    operation: Operations
    value: str


class QueryStringFilter:
    _filters: list = []
    _dto_data: Optional[dict] = None
    _dto_fields: Optional[List[str]] = None

    def __init__(self, query_string: str, dto: Optional[Any] = None):
        """
        Generate filters from query string args.
        Fournish a DTO instance (using dataclass required) to cast values
        """

        self._set_dto(dto)

        self._filters = []
        raw_data = parse_qs(query_string)
        for k, v in raw_data.items():
            list_values = self._separate_values(v)
            [self._create_filter(k, val) for val in list_values if val]

    def _set_dto(self, dto: Optional[Any] = None):
        """Define accepted fields"""
        self._dto_data = None
        self._dto_fields = None

        if dto and is_dataclass(dto):
            self._dto_data = {field.name: field.type for field in fields(dto)}
            self._dto_data["orderby"] = str
            self._dto_data["offset"] = int
            self._dto_data["limit"] = int
            self._dto_data["page"] = int
            self._dto_fields = list(self._dto_data.keys())

    def _cast_filter_value(self, filter: Filter, field_type: Any):
        """Attempt to infer type from DTO class"""

        if field_type in [int, float, str, bool, bytes]:
            filter.value = field_type(filter.value)

        elif field_type in [datetime, date, time]:
            filter.value = field_type.fromisoformat(filter.value)

        elif field_type == timedelta:
            filter.value = timedelta(seconds=filter.value)

        elif field_type == type(None) and filter.value.lower() in [  # noqa: E721
            "none",
            "null",
        ]:
            filter.value = None

        # Attempt to infer Optional and Union recursively
        elif isinstance(field_type, _GenericAlias):
            for t in field_type.__args__:
                self._cast_filter_value(filter, t)

    def _separate_values(self, values: List[str]) -> List[str]:
        """Split grouped values in many"""
        new_values = []
        for value in values:
            new_values.extend(value.split(","))
        return new_values

    def _create_filter(self, key: str, value: str):
        """Create a filter for a valid pair key, value"""
        field, op = self._parse_key(key, value)
        if (
            field
            and op
            and (
                self._dto_fields is None
                or (self._dto_fields and field in self._dto_fields)
            )
        ):
            filtr = Filter(field=field, operation=op, value=value)
            if self._dto_fields:
                field_type = self._dto_data[filtr.field]
                try:  # nosec
                    self._cast_filter_value(filtr, field_type)
                except Exception:
                    pass
            self._filters.append(filtr)

    def _parse_key(self, key: str, value: str):
        """Parse key to infer operation type"""
        if "_" in key:
            for op in Operations:
                op_name = f"_{op.name.lower()}"
                if key.endswith(op_name):
                    size = len(op_name)
                    return key[:-size], op

        elif key == "orderby":
            if value.startswith("-"):
                return value[1:], Operations.DESC
            else:
                return value, Operations.ASC

        elif key == "offset":
            return key, Operations.OFFSET
        elif key == "limit":
            return key, Operations.LIMIT
        elif key == "page":
            return key, Operations.PAGE

        return None, None

    def get_filters(self) -> List[Filter]:
        return self._filters