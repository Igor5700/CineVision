from __future__ import annotations

import json
import logging

from movielib.bootstrap.logging import _JsonFormatter, set_correlation_id


def _record(msg: str, args: tuple[object, ...] = ()) -> logging.LogRecord:
    return logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg=msg,
        args=args,
        exc_info=None,
    )


def test_formats_a_record_as_json() -> None:
    formatter = _JsonFormatter()

    output = json.loads(formatter.format(_record("hello %s", ("world",))))

    assert output["level"] == "INFO"
    assert output["logger"] == "test"
    assert output["message"] == "hello world"
    assert "correlation_id" not in output


def test_includes_the_correlation_id_once_set() -> None:
    set_correlation_id("abc-123")
    try:
        output = json.loads(_JsonFormatter().format(_record("hi")))
        assert output["correlation_id"] == "abc-123"
    finally:
        set_correlation_id(None)


def test_correlation_id_is_absent_again_once_cleared() -> None:
    set_correlation_id("abc-123")
    set_correlation_id(None)

    output = json.loads(_JsonFormatter().format(_record("hi")))

    assert "correlation_id" not in output
