# pyright: reportUnnecessaryTypeIgnoreComment = false
import dataclasses
from typing import Annotated

from litestar import Litestar, get
from litestar.enums import ParamType
from litestar.openapi.spec import Parameter as OpenAPIParameter
from litestar.params import (
    CookieParameter,
    FromCookie,
    FromHeader,
    FromPath,
    FromQuery,
    HeaderParameter,
    PathParameter,
    QueryParameter,
)
from litestar.testing import TestClient, create_test_client


def test_simple_form_handler() -> None:
    @get("/{path_param:int}")
    def handler(
        path_param: FromPath[int],
        query_param: FromQuery[int],
        header_param: FromHeader[int],
        cookie_param: FromCookie[int],
    ) -> dict[str, int]:
        return {"query": query_param, "header": header_param, "cookie": cookie_param, "path": path_param}

    with create_test_client([handler], raise_server_exceptions=True) as client:
        client.cookies.set("cookie_param", "4")
        res = client.get("/1?query_param=2", headers={"header_param": "3"})
        assert res.status_code == 200
        assert res.json() == {"path": 1, "query": 2, "header": 3, "cookie": 4}


def test_explicit_form_handler() -> None:
    @get("/{path_param:int}")
    def handler(
        path_param: Annotated[int, PathParameter()],
        query_param: Annotated[int, QueryParameter()],
        header_param: Annotated[int, HeaderParameter()],
        cookie_param: Annotated[int, CookieParameter()],
    ) -> dict[str, int]:
        return {"query": query_param, "header": header_param, "cookie": cookie_param, "path": path_param}

    with create_test_client([handler], raise_server_exceptions=True) as client:
        client.cookies.set("cookie_param", "4")
        res = client.get("/1?query_param=2", headers={"header_param": "3"})
        assert res.status_code == 200
        assert res.json() == {"path": 1, "query": 2, "header": 3, "cookie": 4}


def test_explicit_form_with_alias_handler() -> None:
    @get("/{path_param:int}")
    def handler(
        path_p: Annotated[int, PathParameter(name="path_param")],
        query_p: Annotated[int, QueryParameter(name="query_param")],
        header_p: Annotated[int, HeaderParameter(name="header_param")],
        cookie_p: Annotated[int, CookieParameter(name="cookie_param")],
    ) -> dict[str, int]:
        return {"query": query_p, "header": header_p, "cookie": cookie_p, "path": path_p}

    app = Litestar([handler])
    schema_params = app.openapi_schema.paths["/{path_param}"].get.parameters  # type: ignore[index, union-attr]

    assert sorted([dataclasses.replace(p, schema=None) for p in schema_params], key=lambda p: p.name) == [  # type: ignore[union-attr]
        OpenAPIParameter(name="cookie_param", param_in=ParamType.COOKIE, required=True),
        OpenAPIParameter(name="header_param", param_in=ParamType.HEADER, required=True),
        OpenAPIParameter(name="path_param", param_in=ParamType.PATH, required=True),
        OpenAPIParameter(name="query_param", param_in=ParamType.QUERY, required=True),
    ]

    with TestClient(app, raise_server_exceptions=True) as client:
        client.cookies.set("cookie_param", "4")
        res = client.get("/1?query_param=2", headers={"header_param": "3"})
        assert res.status_code == 200
        assert res.json() == {"path": 1, "query": 2, "header": 3, "cookie": 4}


def test_simple_form_dependency() -> None:
    async def dependency(
        path_param: FromPath[int],
        query_param: FromQuery[int],
        header_param: FromHeader[int],
        cookie_param: FromCookie[int],
    ) -> dict[str, int]:
        return {"query": query_param, "header": header_param, "cookie": cookie_param, "path": path_param}

    @get("/{path_param:int}", dependencies={"dep": dependency})
    def handler(dep: dict[str, int]) -> dict[str, int]:
        return dep

    with create_test_client([handler], raise_server_exceptions=True) as client:
        client.cookies.set("cookie_param", "4")
        res = client.get("/1?query_param=2", headers={"header_param": "3"})
        assert res.status_code == 200
        assert res.json() == {"path": 1, "query": 2, "header": 3, "cookie": 4}


def test_explicit_form_dependency() -> None:
    async def dependency(
        path_param: Annotated[int, PathParameter()],
        query_param: Annotated[int, QueryParameter()],
        header_param: Annotated[int, HeaderParameter()],
        cookie_param: Annotated[int, CookieParameter()],
    ) -> dict[str, int]:
        return {"query": query_param, "header": header_param, "cookie": cookie_param, "path": path_param}

    @get("/{path_param:int}", dependencies={"dep": dependency})
    def handler(dep: dict[str, int]) -> dict[str, int]:
        return dep

    with create_test_client([handler], raise_server_exceptions=True) as client:
        client.cookies.set("cookie_param", "4")
        res = client.get("/1?query_param=2", headers={"header_param": "3"})
        assert res.status_code == 200
        assert res.json() == {"path": 1, "query": 2, "header": 3, "cookie": 4}


def test_explicit_form_with_alias_dependency() -> None:
    async def dependency(
        path_p: Annotated[int, PathParameter(name="path_param")],
        query_p: Annotated[int, QueryParameter(name="query_param")],
        header_p: Annotated[int, HeaderParameter(name="header_param")],
        cookie_p: Annotated[int, CookieParameter(name="cookie_param")],
    ) -> dict[str, int]:
        return {"query": query_p, "header": header_p, "cookie": cookie_p, "path": path_p}

    @get("/{path_param:int}", dependencies={"dep": dependency})
    def handler(dep: dict[str, int]) -> dict[str, int]:
        return dep

    app = Litestar([handler])
    schema_params = app.openapi_schema.paths["/{path_param}"].get.parameters  # type: ignore[index, union-attr]

    assert sorted([dataclasses.replace(p, schema=None) for p in schema_params], key=lambda p: p.name) == [  # type: ignore[union-attr]
        OpenAPIParameter(name="cookie_param", param_in=ParamType.COOKIE, required=True),
        OpenAPIParameter(name="header_param", param_in=ParamType.HEADER, required=True),
        OpenAPIParameter(name="path_param", param_in=ParamType.PATH, required=True),
        OpenAPIParameter(name="query_param", param_in=ParamType.QUERY, required=True),
    ]

    with TestClient(app, raise_server_exceptions=True) as client:
        client.cookies.set("cookie_param", "4")
        res = client.get("/1?query_param=2", headers={"header_param": "3"})
        assert res.status_code == 200
        assert res.json() == {"path": 1, "query": 2, "header": 3, "cookie": 4}
