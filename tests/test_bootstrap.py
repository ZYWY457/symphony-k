"""Verify that the configured environment can import both package boundaries."""

import symphony_k
import symphony_k.domain


def test_package_import() -> None:
    assert symphony_k.__name__ == "symphony_k"


def test_domain_package_import() -> None:
    assert symphony_k.domain.__name__ == "symphony_k.domain"
