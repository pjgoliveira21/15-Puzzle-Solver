import threading

from puzzle15.integration.compare_service import CompareService
from puzzle15.solver.registry import ALGORITHMS

GOAL = [
    [1, 2, 3, 4],
    [5, 6, 7, 8],
    [9, 10, 11, 12],
    [13, 14, 15, -1],
]

ONE_MOVE_AWAY = [
    [1, 2, 3, 4],
    [5, 6, 7, 8],
    [9, 10, 11, 12],
    [13, 14, -1, 15],
]


def test_run_all_async_calls_on_done_with_all_results():
    service = CompareService()
    done = threading.Event()
    captured: dict = {}

    def on_done(results, error):
        captured["results"] = results
        captured["error"] = error
        done.set()

    # A short timeout keeps this fast: DFS at the default max_depth=30
    # explores millions of nodes without finding this shallow solution (see
    # test_algorithms.py's DFS notes), so it reliably reports failure here
    # rather than succeeding - this test is about the threaded wrapper
    # returning one result per algorithm, not about every algorithm
    # succeeding (that's covered by test_registry's run_all_algorithms
    # tests with a generous timeout).
    service.run_all_async(ONE_MOVE_AWAY, GOAL, timeout=0.5, on_done=on_done)
    assert done.wait(timeout=10)

    assert captured["error"] is None
    assert set(captured["results"].keys()) == set(ALGORITHMS.keys())
