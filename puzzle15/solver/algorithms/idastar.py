import logging
import time

from puzzle15.solver.board import Board, BoardTuple, get_neighbors, manhattan_distance, matrix_to_tuple
from puzzle15.solver.result import SearchTimeout, SolveResult, make_result

logger = logging.getLogger(__name__)


def solve_idastar(initial_matrix: Board, goal_matrix: Board, timeout: float | None = None) -> SolveResult:
    initial = matrix_to_tuple(initial_matrix)
    goal = matrix_to_tuple(goal_matrix)

    threshold = manhattan_distance(initial, goal)
    start_time = time.time()
    stats = {"explored": 0, "iterations": 0}

    logger.debug("[IDA*] starting (timeout=%s)", timeout)
    try:
        while True:
            if timeout and (time.time() - start_time > timeout):
                raise SearchTimeout()

            stats["iterations"] += 1
            visited = {initial}

            next_threshold, path = _idastar_kernel(initial, goal, 0, threshold, [initial], visited, start_time, timeout, stats)

            if path:
                result = make_result(True, start_time, stats["explored"], path)
                logger.debug("[IDA*] solution found (%ss, %s steps)", result.time_seconds, result.steps)
                return result

            if next_threshold == float("inf"):
                return make_result(False, start_time, stats["explored"])
            threshold = next_threshold

    except SearchTimeout:
        logger.debug("[IDA*] timeout reached (explored=%s)", stats["explored"])
        return make_result(False, start_time, stats["explored"])


def _idastar_kernel(
    state: BoardTuple,
    goal: BoardTuple,
    g: int,
    threshold: float,
    path: list[BoardTuple],
    visited: set[BoardTuple],
    start_time: float,
    timeout: float | None,
    stats: dict,
) -> tuple[float, list[BoardTuple] | None]:
    if timeout and (time.time() - start_time > timeout):
        raise SearchTimeout()

    stats["explored"] += 1

    f_val = g + manhattan_distance(state, goal)
    if f_val > threshold:
        return f_val, None
    if state == goal:
        return f_val, path

    min_threshold = float("inf")

    for neighbor in get_neighbors(state):
        if neighbor not in visited:
            visited.add(neighbor)
            next_threshold, result = _idastar_kernel(neighbor, goal, g + 1, threshold, path + [neighbor], visited, start_time, timeout, stats)
            if result:
                return next_threshold, result
            if next_threshold < min_threshold:
                min_threshold = next_threshold
            visited.remove(neighbor)

    return min_threshold, None
