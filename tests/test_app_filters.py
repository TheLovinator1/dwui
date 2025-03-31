from __future__ import annotations

from typing import TYPE_CHECKING

from dwui.templatetags import app_filters

if TYPE_CHECKING:
    from docker.models.containers import Container
    from pytest_mock import MockerFixture


def test_split() -> None:
    """Test the split filter."""
    value = "a,b,c"
    delimiter = ","
    result: list[str] = app_filters.split(value, delimiter)
    assert result == ["a", "b", "c"]


def test_groupby_container(mocker: MockerFixture) -> None:
    """Test the groupby_container filter."""
    mock_container_1 = mocker.Mock()
    mock_container_1.attrs = {"Config": {"Labels": {"com.docker.compose.project": "project1"}}}

    mock_container_2 = mocker.Mock()
    mock_container_2.attrs = {"Config": {"Labels": {"com.docker.compose.project": "project2"}}}

    mock_container_3 = mocker.Mock()
    mock_container_3.attrs = {"Config": {"Labels": {"com.docker.compose.project": "project1"}}}

    containers = [mock_container_1, mock_container_2, mock_container_3]
    result: list[tuple[str, list[Container]]] = app_filters.groupby_container(containers)

    assert len(result) == 2
    assert result[0][0] == "project1"
    assert len(result[0][1]) == 2
    assert result[1][0] == "project2"
    assert len(result[1][1]) == 1


def test_dict_get() -> None:
    """Test the dict_get filter."""
    dictionary: dict[str, str] = {"key1": "value1", "key2": "value2"}
    key = "key1"
    result: str | None = app_filters.dict_get(dictionary, key)
    assert result == "value1"

    missing_key = "key3"
    result: str | None = app_filters.dict_get(dictionary, missing_key)
    assert result is None

    not_a_dict = "not_a_dict"
    result: str | None = app_filters.dict_get(not_a_dict, key)  # type: ignore  # noqa: PGH003
    assert result is None
