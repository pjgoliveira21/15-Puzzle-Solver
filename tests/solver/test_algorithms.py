import time as time_module

import pytest

from puzzle15.solver.registry import ALGORITHMS, run_algorithm, run_all_algorithms

GOAL = [
    [1, 2, 3, 4],
    [5, 6, 7, 8],
    [9, 10, 11, 12],
    [13, 14, 15, -1],
]

# One move away from GOAL (blank swapped with 15).
ONE_MOVE_AWAY = [
    [1, 2, 3, 4],
    [5, 6, 7, 8],
    [9, 10, 11, 12],
    [13, 14, -1, 15],
]


# DFS explores depth-first up to max_depth before backtracking, so it isn't
# guaranteed to find a shallow solution quickly at the default max_depth=30
# (same characteristic as the original algorithm) - tested separately below
# with a max_depth tight enough to force it.
NON_DFS_KEYS = [key for key in ALGORITHMS if key != "dfs"]


@pytest.mark.parametrize("key", NON_DFS_KEYS)
def test_solves_one_move_away(key):
    result = run_algorithm(key, ONE_MOVE_AWAY, GOAL, timeout=10)
    assert result.success
    assert result.steps == 1
    assert result.path[0] == ONE_MOVE_AWAY
    assert result.path[-1] == GOAL


def test_dfs_solves_one_move_away_within_matching_max_depth():
    result = run_algorithm("dfs", ONE_MOVE_AWAY, GOAL, timeout=10, max_depth=1)
    assert result.success
    assert result.steps == 1
    assert result.path[0] == ONE_MOVE_AWAY
    assert result.path[-1] == GOAL


@pytest.mark.parametrize("key", list(ALGORITHMS.keys()))
def test_already_at_goal(key):
    result = run_algorithm(key, GOAL, GOAL, timeout=10)
    assert result.success
    assert result.steps == 0
    assert result.path == [GOAL]


def test_dfs_fails_with_too_small_max_depth():
    result = run_algorithm("dfs", ONE_MOVE_AWAY, GOAL, timeout=10, max_depth=0)
    assert not result.success


@pytest.mark.parametrize("key", list(ALGORITHMS.keys()))
def test_vanishing_timeout_reports_failure(key, monkeypatch):
    # A near-zero (but truthy) timeout should trip on the first check for
    # every algorithm. timeout=0 would NOT do this: `if timeout and ...`
    # treats 0 as "no timeout", same quirk as the original implementation.
    #
    # Racing a tiny timeout against real wall-clock time is flaky on
    # coarser clocks (observed in CI: a whole multi-node search completed
    # with elapsed reading back as 0.0 across every check, since
    # time.time()'s resolution isn't guaranteed to be nanosecond-grade).
    # Mock time.time() instead so the first elapsed-time check is always
    # deterministically over the threshold, regardless of the host clock.
    call_count = 0

    def fake_time() -> float:
        nonlocal call_count
        call_count += 1
        return 0.0 if call_count == 1 else 1000.0

    monkeypatch.setattr(time_module, "time", fake_time)

    result = run_algorithm(key, ONE_MOVE_AWAY, GOAL, timeout=1e-9, max_depth=0)
    assert not result.success


def test_run_all_algorithms_returns_every_key():
    results = run_all_algorithms(ONE_MOVE_AWAY, GOAL, timeout=10)
    assert set(results.keys()) == set(ALGORITHMS.keys())


def test_run_all_algorithms_already_at_goal():
    results = run_all_algorithms(GOAL, GOAL, timeout=10)
    assert all(result.success and result.steps == 0 for result in results.values())


def test_run_all_algorithms_vanishing_timeout_reports_failure(monkeypatch):
    # Unlike test_vanishing_timeout_reports_failure above, this drives five
    # sequential run_algorithm calls off one shared fake clock, so a simple
    # "first call small, rest large" toggle isn't enough - the second call
    # of each later algorithm (its first elapsed-time check) would read the
    # same "large" value as its own start time, making elapsed look like 0
    # again. A monotonically increasing clock guarantees every check reads
    # strictly after its own start time, by a wide enough margin to clear
    # the near-zero timeout regardless of how many algorithms already ran.
    counter = 0

    def fake_time() -> float:
        nonlocal counter
        counter += 1
        return counter * 1000.0

    monkeypatch.setattr(time_module, "time", fake_time)

    results = run_all_algorithms(ONE_MOVE_AWAY, GOAL, timeout=1e-9)
    assert all(not result.success for result in results.values())
