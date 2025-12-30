from src.structures import collect_control_blocks_connected_vars


def test_returns_only_start_var_when_no_adjacency():
    graph = {}

    result = collect_control_blocks_connected_vars("X", graph)

    assert result == {"X"}


def test_returns_directly_connected_vars():
    graph = {
        "A": {"B", "C"},
    }

    result = collect_control_blocks_connected_vars("A", graph)

    assert result == {"A", "B", "C"}


def test_returns_transitive_dependencies():
    graph = {
        "A": {"B"},
        "B": {"C"},
        "C": {"D"},
    }

    result = collect_control_blocks_connected_vars("A", graph)

    assert result == {"A", "B", "C", "D"}


def test_handles_cycles_without_infinite_loop():
    graph = {
        "A": {"B"},
        "B": {"C"},
        "C": {"A"},
    }

    result = collect_control_blocks_connected_vars("A", graph)

    assert result == {"A", "B", "C"}


def test_shared_variable_connects_multiple_control_blocks():
    graph = {
        "LISTA": {"VAR1"},
        "LISTA2": {"VAR1"},
        "VAR1": {"LISTA", "LISTA2"},
    }

    result = collect_control_blocks_connected_vars("LISTA", graph)

    assert result == {"LISTA", "LISTA2", "VAR1"}


def test_realistic_template_control_block_dependencies():
    graph = {
        "LISTA2": {"VARIAVEL", "VAR1"},
        "VARIAVEL": {"LISTA2"},
        "VAR1": {"LISTA2", "LISTA", "VAR2", "VAR3"},
        "LISTA": {"VAR1", "VAR2", "VAR3"},
        "VAR2": {"VAR1", "VAR3"},
        "VAR3": {"VAR1"},
    }

    result = collect_control_blocks_connected_vars("LISTA2", graph)

    assert result == {
        "LISTA2",
        "VARIAVEL",
        "VAR1",
        "LISTA",
        "VAR2",
        "VAR3",
    }
