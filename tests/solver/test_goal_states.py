from puzzle15.solver.goal_states import get_goal_state, load_goal_states

EXPECTED_VALUES = sorted(list(range(1, 16)) + [-1])


def test_load_goal_states_has_numeric_and_colored():
    states = load_goal_states()
    assert "numeric" in states
    assert "colored" in states


def test_every_preset_has_one_blank_and_valid_values():
    states = load_goal_states()
    for group in ("numeric", "colored"):
        for key, board in states[group].items():
            flat = [v for row in board for v in row]
            assert len(flat) == 16, f"{group}.{key} is not 4x4"
            if group == "numeric":
                assert sorted(flat) == EXPECTED_VALUES, f"{group}.{key} is not a valid permutation"
            assert flat.count(-1) == 1, f"{group}.{key} does not have exactly one blank"


def test_get_goal_state_known_preset():
    board = get_goal_state("row_asc")
    assert board[0] == [1, 2, 3, 4]


def test_get_goal_state_unknown_key_falls_back():
    board = get_goal_state("does-not-exist")
    assert board == get_goal_state("row_asc")
