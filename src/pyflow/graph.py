from pyflow.models import Task
from heapq import heappush, heappop

# Wyjątek zgłaszany przy błędnej definicji workflow
class WorkflowValidation(Exception):
    pass


class Workflow:
    def __init__(self):
        # Słownik przechowujący zadania według nazw
        self.tasks: dict[str, Task] = {}

    def add_task(self, task: Task) -> None:
        # Sprawdzenie typu zadania
        if not isinstance(task, Task):
            raise TypeError("Można dodawać tylko obiekty Task")

        # Sprawdzenie duplikatów
        if task.name in self.tasks:
            raise WorkflowValidation(
                f"Zadanie '{task.name}' już istnieje"
            )

        self.tasks[task.name] = task

    def validate(self) -> None:
        # Sprawdzenie brakujących zależności
        for task in self.tasks.values():
            for dependency in sorted(task.dependencies):
                if dependency not in self.tasks:
                    raise WorkflowValidation(
                        f"Zadanie '{task.name}' zależy od "
                        f"nieistniejącego zadania '{dependency}'"
                    )

        # Wykrywanie cykli metodą DFS
        visited: set[str] = set()
        active: set[str] = set()
        path: list[str] = []

        def visit(name: str) -> None:
            if name in active:
                start = path.index(name)
                cycle = path[start:] + [name]
                raise WorkflowValidation(
                    "Wykryto cykl: " + " -> ".join(cycle)
                )

            if name in visited:
                return

            active.add(name)
            path.append(name)

            for dependency in sorted(
                self.tasks[name].dependencies
            ):
                visit(dependency)

            path.pop()
            active.remove(name)
            visited.add(name)

        for name in sorted(self.tasks):
            visit(name)

def topological_order(workflow: Workflow) -> list[str]:
    # Najpierw sprawdzamy poprawność grafu
    workflow.validate()

    # Liczba zależności każdego zadania
    in_degree = {
        name: len(task.dependencies)
        for name, task in workflow.tasks.items()
    }

    # Lista zadań zależnych od danego zadania
    dependents: dict[str, list[str]] = {
        name: [] for name in workflow.tasks
    }

    for name, task in workflow.tasks.items():
        for dependency in task.dependencies:
            dependents[dependency].append(name)

    # Kolejka zadań bez zależności
    ready = []

    for name, degree in in_degree.items():
        if degree == 0:
            heappush(ready, name)

    order = []

    while ready:
        # Pobranie alfabetycznie pierwszego zadania
        current = heappop(ready)
        order.append(current)

        # Aktualizacja zależności kolejnych zadań
        for dependent in dependents[current]:
            in_degree[dependent] -= 1

            if in_degree[dependent] == 0:
                heappush(ready, dependent)

    # Sprawdzenie, czy przetworzono wszystkie zadania
    if len(order) != len(workflow.tasks):
        raise WorkflowValidation("Wykryto cykl w grafie")

    return order

def execution_layers(workflow: Workflow) -> list[list[str]]:
    # Sprawdzenie poprawności grafu
    workflow.validate()

    # Liczba zależności dla każdego zadania
    in_degree = {
        name: len(task.dependencies)
        for name, task in workflow.tasks.items()
    }

    # Zadania zależne od innych zadań
    dependents: dict[str, list[str]] = {
        name: [] for name in workflow.tasks
    }

    for name, task in workflow.tasks.items():
        for dependency in task.dependencies:
            dependents[dependency].append(name)

    # Pierwsza warstwa - zadania bez zależności
    ready = sorted(
        name for name, degree in in_degree.items()
        if degree == 0
    )

    layers = []
    processed = 0

    while ready:
        # Dodanie bieżącej warstwy
        layers.append(ready)
        processed += len(ready)

        next_ready = []

        # Przetwarzanie zadań z bieżącej warstwy
        for current in ready:
            for dependent in dependents[current]:
                in_degree[dependent] -= 1

                if in_degree[dependent] == 0:
                    next_ready.append(dependent)

        # Sortowanie kolejnej warstwy alfabetycznie
        ready = sorted(next_ready)

    # Kontrola liczby przetworzonych zadań
    if processed != len(workflow.tasks):
        raise WorkflowValidation("Wykryto cykl w grafie")

    return layers
