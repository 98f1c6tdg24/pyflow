import pytest
from pyflow.models import Task


def example_function(inputs, params):
    return 10


# Test prawidłowego utworzenia zadania
def test_create_task():
    task = Task(
        name="example",
        function=example_function
    )

    assert task.name == "example"
    assert task.dependencies == frozenset()
    assert task.params == {}


# Test pustej nazwy
def test_empty_name():
    with pytest.raises(ValueError):
        Task(name="", function=example_function)


# Test zależności od samego siebie
def test_self_dependency():
    with pytest.raises(ValueError):
        Task(
            name="example",
            function=example_function,
            dependencies=frozenset({"example"})
        )


# Test nieprawidłowej funkcji
def test_invalid_function():
    with pytest.raises(TypeError):
        Task(name="example", function="tekst")


# Test zabezpieczenia parametrów
def test_immutable_params():
    params = {"value": 10}

    task = Task(
        name="example",
        function=example_function,
        params=params
    )

    params["value"] = 20

    assert task.params["value"] == 10


# Test poprawnego przypisania zależności
def test_dependencies():
    task = Task(
        name="report",
        function=example_function,
        dependencies=frozenset({"extract", "clean"})
    )

    assert task.dependencies == frozenset({"extract", "clean"})
    
# Test nazwy zawierającej tylko spacje
def test_whitespace_name():
    with pytest.raises(ValueError):
        Task(
            name="   ",
            function=example_function
        )


# Test kopiowania zagnieżdżonych parametrów
def test_nested_params_copy():
    params = {"settings": {"limit": 10}}

    task = Task(
        name="example",
        function=example_function,
        params=params
    )

    # Zmiana oryginalnych danych
    params["settings"]["limit"] = 20

    # Definicja zadania nie powinna się zmienić
    assert task.params["settings"]["limit"] == 10