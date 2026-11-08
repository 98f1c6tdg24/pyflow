from dataclasses import dataclass, field
from typing import Any, Callable, Mapping
from types import MappingProxyType
from copy import deepcopy


@dataclass(frozen=True)
class Task:
    name: str
    function: Callable[[Mapping[str, Any], Mapping[str, Any]], Any]
    dependencies: frozenset[str] = field(default_factory=frozenset)
    params: Mapping[str, Any] = field(default_factory=dict)
    description: str = ""

    def __post_init__(self):
        # Walidacja nazwy zadania
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("Nazwa zadania nie może być pusta")

        # Walidacja funkcji
        if not callable(self.function):
            raise TypeError("function musi być funkcją")

        # Walidacja zależności
        if isinstance(self.dependencies, (str, bytes)):
            raise TypeError("Nieprawidłowy typ zależności")

        dependencies = frozenset(self.dependencies)

        for dep in dependencies:
            if not isinstance(dep, str) or not dep.strip():
                raise ValueError("Nieprawidłowa nazwa zależności")

        if self.name in dependencies:
            raise ValueError("Zadanie nie może zależeć od samego siebie")

        # Walidacja parametrów
        if not isinstance(self.params, Mapping):
            raise TypeError("params musi być mapowaniem")

        # Zabezpieczenie danych przed modyfikacją
        object.__setattr__(self, "dependencies", dependencies)
        object.__setattr__(
            self,
            "params",
            MappingProxyType(deepcopy(dict(self.params)))
        )