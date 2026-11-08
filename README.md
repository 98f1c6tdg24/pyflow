# PyFlow

PyFlow to biblioteka napisana w Pythonie, służąca do
definiowania zadań i zarządzania ich zależnościami
w skierowanym grafie acyklicznym (DAG).

## Wymagania

- Python 3.11 lub nowszy
- pip
- pytest
- Git

## Instalacja

Utworzenie środowiska wirtualnego:

```powershell
python -m venv .venv
```

Aktywacja środowiska w PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Instalacja biblioteki:

```powershell
python -m pip install -e .
```

Instalacja pytest:

```powershell
python -m pip install pytest
```

## Funkcjonalności

- Definiowanie zadań za pomocą klasy Task.
- Przechowywanie zadań w klasie Workflow.
- Walidacja nazw zadań i ich zależności.
- Wykrywanie zduplikowanych zadań.
- Wykrywanie brakujących zależności.
- Wykrywanie cykli w grafie DAG.
- Deterministyczne sortowanie topologiczne.
- Wyznaczanie warstw wykonywania zadań.

## Przykład użycia

```python
from pyflow import (
    Task,
    Workflow,
    topological_order,
    execution_layers,
)


def example_function(inputs, params):
    return params.get("value", 0)


workflow = Workflow()

workflow.add_task(Task(
    name="extract",
    function=example_function
))

workflow.add_task(Task(
    name="clean_a",
    function=example_function,
    dependencies=frozenset({"extract"})
))

workflow.add_task(Task(
    name="clean_b",
    function=example_function,
    dependencies=frozenset({"extract"})
))

workflow.add_task(Task(
    name="report",
    function=example_function,
    dependencies=frozenset({"clean_a", "clean_b"})
))

workflow.validate()

print(topological_order(workflow))
print(execution_layers(workflow))
```

### Oczekiwany wynik

```text
['extract', 'clean_a', 'clean_b', 'report']

[['extract'], ['clean_a', 'clean_b'], ['report']]
```

Biblioteka wyznacza kolejność i warstwy zadań,
ale na tym etapie nie uruchamia jeszcze ich funkcji.

## Zastosowane algorytmy

### Walidacja DAG

Do wykrywania cykli zastosowano algorytm
przeszukiwania grafu w głąb (DFS).

Algorytm sprawdza zależności między zadaniami
i wykrywa sytuacje, w których zadania tworzą cykl.

Złożoność podstawowego DFS: O(V + E).

### Sortowanie topologiczne

Do ustalania kolejności wykonywania zadań
wykorzystano algorytm Kahna.

Kolejka priorytetowa zapewnia deterministyczną
kolejność alfabetyczną dostępnych zadań.

Złożoność sortowania z kolejką priorytetową:
O((V + E) log V).

### Warstwy wykonywania

Funkcja execution_layers() grupuje zadania
według ich zależności.

Zadania należące do tej samej warstwy mogą
zostać wykonane równolegle.

## Testy

Testy znajdują się w folderze tests/.

Uruchomienie testów:

```powershell
python -m pytest -v
```

Testy sprawdzają między innymi:

- Poprawność modelu Task.
- Nieprawidłowe nazwy zadań.
- Zależności od samego siebie.
- Duplikaty zadań.
- Brakujące zależności.
- Wykrywanie cykli.
- Sortowanie topologiczne.
- Deterministyczność wyników.
- Poprawność warstw wykonywania.
- Pusty workflow i pojedyncze zadania.

## Struktura projektu

```text
pyflow/
|-- src/
|   `-- pyflow/
|       |-- __init__.py
|       |-- models.py
|       `-- graph.py
|-- tests/
|   |-- test_models.py
|   `-- test_graph.py
|-- pyproject.toml
|-- README.md
`-- .gitignore
```
