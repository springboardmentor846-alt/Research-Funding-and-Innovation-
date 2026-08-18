"""Provider registry for the Patent Intelligence Service.

The registry is the only component that knows the concrete provider
classes.  Business code (sync engine, admin API) talks to providers
through ``all_patent_providers()`` and ``get_patent_provider(name)``.

To add a new data source:

1. Implement a class subclassing ``BasePatentProvider`` in
   ``app.patents.providers``.
2. Append it to ``app.patents.providers.__init__`` so the class is
   imported and therefore registered.
3. Add an ``ENABLED`` flag to ``PatentIntelSettings``.
"""
from __future__ import annotations

from typing import Dict, List, Optional, Type

from .base import BasePatentProvider
from .config import patent_intel_settings, provider_flags


_PROVIDER_FACTORIES: Dict[str, Type[BasePatentProvider]] = {}


def register_patent_provider(cls: Type[BasePatentProvider]) -> Type[BasePatentProvider]:
    """Class decorator that adds a provider to the registry."""
    if not cls.name:
        raise ValueError(f"{cls.__name__} must set class attribute `name`")
    _PROVIDER_FACTORIES[cls.name] = cls
    return cls


def all_patent_providers() -> List[BasePatentProvider]:
    """Instantiate every registered provider, respecting enable flags.

    A failure during construction is logged and the provider is
    returned in a disabled state so the rest of the system can still
    operate.
    """
    flags = provider_flags()
    instances: List[BasePatentProvider] = []
    for name, cls in _PROVIDER_FACTORIES.items():
        instance = cls()
        if not flags.get(name, False):
            instance._health.enabled = False
            instances.append(instance)
            continue
        try:
            instances.append(instance)
        except Exception:
            instance._record_failure("construction failed")
            instances.append(instance)
    return instances


def get_patent_provider(name: str) -> Optional[BasePatentProvider]:
    """Look up a single provider by name. Returns ``None`` if unknown."""
    cls = _PROVIDER_FACTORIES.get(name)
    if cls is None:
        return None
    return cls()


def known_patent_providers() -> List[str]:
    """Names of every registered provider class."""
    return list(_PROVIDER_FACTORIES.keys())


def enabled_patent_provider_names() -> List[str]:
    """Names of providers that are both registered and enabled."""
    flags = provider_flags()
    return [n for n in _PROVIDER_FACTORIES if flags.get(n, False)]
