"""Fixtures for the Pyroscope tests."""

from collections.abc import Generator
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations: None) -> None:
    """Load integrations from custom_components/."""


@pytest.fixture
def mock_pyroscope() -> Generator[MagicMock]:
    """Stop tests from starting the real profiler."""
    with patch("custom_components.pyroscope.pyroscope") as mock:
        yield mock
