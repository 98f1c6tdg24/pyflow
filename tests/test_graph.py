import pytest
from pyflow.models import Task
from pyflow.graph import (
    Workflow,
    WorkflowValidation,
    topological_order,
    execution_layers
)


def example_function(inputs, params):
    return 10


# Test poprawnego dodawania zadań
def test_add_task():
    workflow = Workflow()
    task = Task(name="extract", function=example_function)

    workflow.add_task(task)

    assert "extract" in workflow.tasks


# Test wykrywania duplikatów
def test_duplicate_task():
    workflow = Workflow()
    task = Task(name="extract", function=example_function)

    workflow.add_task(task)

    with pytest.raises(WorkflowValidation):
        workflow.add_task(task)


# Test brakującej zależności
def test_missing_dependency():
    workflow = Workflow()

    task = Task(
        name="clean",
        function=example_function,
        dependencies=frozenset({"extract"})
    )

    workflow.add_task(task)

    with pytest.raises(WorkflowValidation):
        workflow.validate()


# Test wykrywania cyklu
def test_cycle():
    workflow = Workflow()

    task_a = Task(
        name="A",
        function=example_function,
        dependencies=frozenset({"B"})
    )

    task_b = Task(
        name="B",
        function=example_function,
        dependencies=frozenset({"A"})
    )

    workflow.add_task(task_a)
    workflow.add_task(task_b)

    with pytest.raises(WorkflowValidation):
        workflow.validate()


# Test poprawnego workflow
def test_valid_workflow():
    workflow = Workflow()

    extract = Task(
        name="extract",
        function=example_function
    )

    clean = Task(
        name="clean",
        function=example_function,
        dependencies=frozenset({"extract"})
    )

    report = Task(
        name="report",
        function=example_function,
        dependencies=frozenset({"clean"})
    )

    workflow.add_task(extract)
    workflow.add_task(clean)
    workflow.add_task(report)

    workflow.validate()

    assert len(workflow.tasks) == 3


# Test prawidłowej kolejności topologicznej
def test_topological_order():
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

    order = topological_order(workflow)

    assert order == [
        "extract", "clean_a", "clean_b", "report"
    ]


# Test deterministyczności kolejności
def test_deterministic_order():
    workflow = Workflow()

    for name in ["C", "A", "B"]:
        workflow.add_task(Task(
            name=name,
            function=example_function
        ))

    assert topological_order(workflow) == ["A", "B", "C"]


# Test, czy każde zadanie pojawia się jeden raz
def test_no_duplicates_in_order():
    workflow = Workflow()

    workflow.add_task(Task(
        name="A",
        function=example_function
    ))

    workflow.add_task(Task(
        name="B",
        function=example_function,
        dependencies=frozenset({"A"})
    ))

    order = topological_order(workflow)

    assert len(order) == len(set(order))
    assert len(order) == 2


# Test wykrywania cyklu przy sortowaniu
def test_topological_cycle():
    workflow = Workflow()

    workflow.add_task(Task(
        name="A",
        function=example_function,
        dependencies=frozenset({"B"})
    ))

    workflow.add_task(Task(
        name="B",
        function=example_function,
        dependencies=frozenset({"A"})
    ))

    with pytest.raises(WorkflowValidation):
        topological_order(workflow)

# Test warstw wykonywania zadań
def test_execution_layers():
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

    layers = execution_layers(workflow)

    assert layers == [
        ["extract"],
        ["clean_a", "clean_b"],
        ["report"]
    ]


# Test niezależnych zadań
def test_independent_tasks():
    workflow = Workflow()

    for name in ["C", "A", "B"]:
        workflow.add_task(Task(
            name=name,
            function=example_function
        ))

    layers = execution_layers(workflow)

    assert layers == [["A", "B", "C"]]


# Test pustego workflow
def test_empty_workflow():
    workflow = Workflow()

    assert execution_layers(workflow) == []


# Test cyklu w warstwach
def test_execution_layers_cycle():
    workflow = Workflow()

    workflow.add_task(Task(
        name="A",
        function=example_function,
        dependencies=frozenset({"B"})
    ))

    workflow.add_task(Task(
        name="B",
        function=example_function,
        dependencies=frozenset({"A"})
    ))

    with pytest.raises(WorkflowValidation):
        execution_layers(workflow)

# Test pojedynczego zadania
def test_single_task():
    workflow = Workflow()

    workflow.add_task(Task(
        name="only",
        function=example_function
    ))

    assert topological_order(workflow) == ["only"]
    assert execution_layers(workflow) == [["only"]]


# Test brakującej zależności podczas sortowania
def test_topological_missing_dependency():
    workflow = Workflow()

    workflow.add_task(Task(
        name="report",
        function=example_function,
        dependencies=frozenset({"missing"})
    ))

    with pytest.raises(WorkflowValidation):
        topological_order(workflow)


# Test niezależności wyniku od kolejności dodawania
def test_insertion_order_independence():
    workflow1 = Workflow()
    workflow2 = Workflow()

    for name in ["C", "A", "B"]:
        workflow1.add_task(Task(
            name=name,
            function=example_function
        ))

    for name in ["B", "C", "A"]:
        workflow2.add_task(Task(
            name=name,
            function=example_function
        ))

    assert topological_order(workflow1) == ["A", "B", "C"]
    assert topological_order(workflow2) == ["A", "B", "C"]

    assert execution_layers(workflow1) == [["A", "B", "C"]]
    assert execution_layers(workflow2) == [["A", "B", "C"]]


# Test poprawnego rozdzielenia warstw
def test_multiple_execution_layers():
    workflow = Workflow()

    workflow.add_task(Task(
        name="A",
        function=example_function
    ))

    workflow.add_task(Task(
        name="B",
        function=example_function,
        dependencies=frozenset({"A"})
    ))

    workflow.add_task(Task(
        name="C",
        function=example_function,
        dependencies=frozenset({"B"})
    ))

    assert execution_layers(workflow) == [
        ["A"], ["B"], ["C"]
    ]
