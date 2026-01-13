from templaterx.helpers import structures as st


def test_returns_only_start_var_when_no_adjacency():
    graph = {}

    result = st.collect_control_blocks_connected_vars("X", graph)

    assert result == {"X"}


def test_returns_directly_connected_vars():
    graph = {
        "A": {"B", "C"},
    }

    result = st.collect_control_blocks_connected_vars("A", graph)

    assert result == {"A", "B", "C"}


def test_returns_transitive_dependencies():
    graph = {
        "A": {"B"},
        "B": {"C"},
        "C": {"D"},
    }

    result = st.collect_control_blocks_connected_vars("A", graph)

    assert result == {"A", "B", "C", "D"}


def test_handles_cycles_without_infinite_loop():
    graph = {
        "A": {"B"},
        "B": {"C"},
        "C": {"A"},
    }

    result = st.collect_control_blocks_connected_vars("A", graph)

    assert result == {"A", "B", "C"}


def test_shared_variable_connects_multiple_control_blocks():
    graph = {
        "LIST": {"VAR1"},
        "LIST2": {"VAR1"},
        "VAR1": {"LIST", "LIST2"},
    }

    result = st.collect_control_blocks_connected_vars("LIST", graph)

    assert result == {"LIST", "LIST2", "VAR1"}


def test_realistic_template_control_block_dependencies():
    graph = {
        "LIST2": {"VAR", "VAR1"},
        "VAR": {"LIST2"},
        "VAR1": {"LIST2", "LIST", "VAR2", "VAR3"},
        "LIST": {"VAR1", "VAR2", "VAR3"},
        "VAR2": {"VAR1", "VAR3"},
        "VAR3": {"VAR1"},
    }

    result = st.collect_control_blocks_connected_vars("LIST2", graph)

    assert result == {
        "LIST2",
        "VAR",
        "VAR1",
        "LIST",
        "VAR2",
        "VAR3",
    }
