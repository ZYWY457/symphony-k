"""Bounded AST/import and normal-API checks for the Stage 1 trust boundary."""

import ast
import builtins
import inspect
import socket
import sys
from collections.abc import Callable
from importlib.util import resolve_name
from pathlib import Path
from types import ModuleType
from typing import cast

import pytest

from symphony_k.domain import create_entity
from symphony_k.persistence import ports
from symphony_k.persistence.service import LifecycleService
from symphony_k.persistence.sqlite import (
    SQLiteEventRepository,
    SQLiteRepository,
    SQLiteStore,
)
from tests.test_creation_integrated import CASES, creation_context

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src/symphony_k"


def imported_modules(path: Path) -> set[str]:
    package = "symphony_k." + path.parent.name
    result: set[str] = set()
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Import):
            result.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if node.level:
                module = resolve_name("." * node.level + module, package)
            result.add(module)
            if node.module is None:
                result.update(module + "." + alias.name for alias in node.names)
    return result


def exercise_without(monkeypatch: pytest.MonkeyPatch, forbidden: set[str]) -> None:
    original = cast(Callable[..., ModuleType], builtins.__import__)

    def guarded(name: str, *args: object, **kwargs: object) -> ModuleType:
        assert name.split(".")[0] not in forbidden, name
        return original(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", guarded)
    for request in CASES:
        assert (
            create_entity(request, creation_context(request)).entity.version.value == 1
        )
    store = SQLiteStore()
    request = CASES[0]
    result = LifecycleService(store).create(request, creation_context(request))
    assert store.load(request.entity_id) == result.entity
    store.close()


def test_domain_kernel_requires_no_agent(monkeypatch: pytest.MonkeyPatch) -> None:
    exercise_without(monkeypatch, {"agent", "agents", "codex", "openai", "anthropic"})


def test_domain_kernel_requires_no_docker(monkeypatch: pytest.MonkeyPatch) -> None:
    exercise_without(monkeypatch, {"docker", "subprocess"})


def test_domain_kernel_requires_no_network(monkeypatch: pytest.MonkeyPatch) -> None:
    def forbidden_network(*args: object, **kwargs: object) -> None:
        raise AssertionError("Constitutional suite attempted network access")

    monkeypatch.setattr(socket.socket, "connect", forbidden_network)
    monkeypatch.setattr(socket, "create_connection", forbidden_network)
    exercise_without(monkeypatch, {"requests", "httpx", "urllib", "http", "socket"})


def test_domain_is_independent_of_persistence_and_io() -> None:
    forbidden = {
        "sqlite3",
        "pathlib",
        "os",
        "socket",
        "requests",
        "httpx",
        "urllib",
        "http",
        "subprocess",
        "docker",
        "openai",
        "codex",
    }
    for path in (SOURCE / "domain").glob("*.py"):
        for module in imported_modules(path):
            assert not module.startswith("symphony_k.persistence"), (path, module)
            assert module.split(".")[0] not in forbidden, (path, module)
            assert module.split(".")[0] in sys.stdlib_module_names | {"symphony_k"}


def test_persistence_cannot_dispatch_external_effects() -> None:
    forbidden = {
        "socket",
        "requests",
        "httpx",
        "urllib",
        "http",
        "subprocess",
        "docker",
        "openai",
        "codex",
        "agent",
        "agents",
    }
    calls = {
        "eval",
        "exec",
        "__import__",
        "import_module",
        "Popen",
        "system",
        "urlopen",
        "dispatch",
        "execute_effect",
    }
    for path in (SOURCE / "persistence").glob("*.py"):
        for module in imported_modules(path):
            assert module.split(".")[0] not in forbidden, (path, module)
            assert module.split(".")[0] in sys.stdlib_module_names | {"symphony_k"}
            if module.startswith("symphony_k."):
                assert module.startswith(
                    ("symphony_k.domain", "symphony_k.persistence")
                )
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, ast.Call):
                name = (
                    node.func.id
                    if isinstance(node.func, ast.Name)
                    else node.func.attr
                    if isinstance(node.func, ast.Attribute)
                    else ""
                )
                assert name not in calls, (path, name)


def public_methods(cls: type) -> set[str]:
    return {
        name
        for name, _ in inspect.getmembers(cls, inspect.isfunction)
        if not name.startswith("_")
    }


def test_normal_repository_api_has_no_state_or_history_mutators() -> None:
    for repository in (
        ports.ObjectiveRepository,
        ports.TaskRepository,
        ports.RunRepository,
        ports.OutcomeRepository,
        ports.EvaluationRepository,
        ports.EffectRepository,
        SQLiteRepository,
    ):
        assert public_methods(repository) == {"load", "load_version"}
    assert public_methods(ports.EventRepository) == {"load", "for_entity"}
    assert public_methods(SQLiteEventRepository) == {"load", "for_entity"}
    assert public_methods(SQLiteStore) == {
        "load",
        "load_version",
        "supporting_records",
        "close",
    }
    assert public_methods(LifecycleService) == {
        "create",
        "transition",
        "transition_batch",
    }
    assert public_methods(ports.UnitOfWork) == public_methods(LifecycleService)
