"""Provider registry.

The registry is the *only* component that knows the concrete provider
classes. Business code (sync engine, admin API) talks to providers
through ``get_provider(name)`` and ``all_providers()``.

To add a new data source:

1. Implement a class subclassing ``BaseProvider`` in
   ``app.funding_intel.providers``.
2. Append it to ``_PROVIDER_FACTORIES`` below.
3. Add an ``ENABLED`` flag to ``FundingIntelSettings``.
"""
from __future__ import annotations

from typing import Dict, List, Optional, Type

from .base import BaseProvider
from .config import funding_intel_settings, provider_flags


_PROVIDER_FACTORIES: Dict[str, Type[BaseProvider]] = {}


def register_provider(cls: Type[BaseProvider]) -> Type[BaseProvider]:
    """Class decorator that adds a provider to the registry."""
    if not cls.name:
        raise ValueError(f"{cls.__name__} must set class attribute `name`")
    _PROVIDER_FACTORIES[cls.name] = cls
    return cls


def all_providers() -> List[BaseProvider]:
    """Instantiate every registered provider, respecting enable flags.

    A failure during ``initialize()`` is logged and the provider is
    returned in a disabled state so the rest of the system can still
    operate.
    """
    flags = provider_flags()
    instances: List[BaseProvider] = []
    for name, cls in _PROVIDER_FACTORIES.items():
        instance = cls()
        if not flags.get(name, False):
            instance._health.enabled = False
            instances.append(instance)
            continue
        try:
            # initialize is async, but we construct synchronously and
            # the caller (e.g. scheduler startup) will await it.
            instances.append(instance)
        except Exception:
            # Construction itself should not fail; defensive only.
            instance._record_failure("construction failed")
            instances.append(instance)
    return instances


def get_provider(name: str) -> Optional[BaseProvider]:
    """Look up a single provider by name. Returns ``None`` if unknown."""
    cls = _PROVIDER_FACTORIES.get(name)
    if cls is None:
        return None
    return cls()


def known_providers() -> List[str]:
    """Names of every registered provider class."""
    return list(_PROVIDER_FACTORIES.keys())


def enabled_provider_names() -> List[str]:
    """Names of providers that are both registered and enabled."""
    flags = provider_flags()
    return [n for n in _PROVIDER_FACTORIES if flags.get(n, False)]
