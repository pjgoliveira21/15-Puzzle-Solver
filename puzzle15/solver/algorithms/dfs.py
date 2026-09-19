import logging
import time

from puzzle15.solver.board import Board, BoardTuple, get_neighbors, manhattan_distance, matrix_to_tuple
from puzzle15.solver.progress import ProgressLogger
from puzzle15.solver.result import SearchTimeout, SolveResult, make_result

logger = logging.getLogger(__name__)


def solve_dfs(
    initial_matrix: Board,
    goal_matrix: Board,
    max_depth: int = 30,
    timeout: float | None = None,
) -> SolveResult:
    initial = matrix_to_tuple(initial_matrix)
    goal = matrix_to_tuple(goal_matrix)

    start_time = time.time()
    stats = {"explored": 0, "progress": ProgressLogger(logger, "DFS", start_time)}
    visited: set[BoardTuple] = set()

    logger.debug("[DFS] starting: timeout=%s max_depth=%d initial_distance=%d", timeout, max_depth, manhattan_distance(initial, goal))
    try:
        path = _dfs_kernel(initial, goal, 0, max_depth, visited, [initial], start_time, timeout, stats)
        if path:
            result = make_result(True, start_time, stats["explored"], path)
            logger.debug("[DFS] solved: time=%ss steps=%d explored=%d", result.time_seconds, result.steps, stats["explored"])
            return result

        logger.debug("[DFS] no solution within max_depth=%d: explored=%d", max_depth, stats["explored"])
        return make_result(False, start_time, stats["explored"])

    except SearchTimeout:
        logger.debug("[DFS] timeout reached: explored=%d", stats["explored"])
        return make_result(False, start_time, stats["explored"])


def _dfs_kernel(
    current: BoardTuple,
    goal: BoardTuple,
    depth: int,
    max_depth: int,
    visited: set[BoardTuple],
    path: list[BoardTuple],
    start_time: float,
    timeout: float | None,
    stats: dict,
) -> list[BoardTuple] | None:
    if timeout and (time.time() - start_time > timeout):
        raise SearchTimeout()

    stats["explored"] += 1
    stats["progress"].maybe_log(stats["explored"], depth=depth, visited=len(visited))

    if current == goal:
        return path

    if depth >= max_depth:
        return None

    visited.add(current)

    for neighbor in get_neighbors(current):
        if neighbor not in visited:
            result = _dfs_kernel(neighbor, goal, depth + 1, max_depth, visited, path + [neighbor], start_time, timeout, stats)
            if result:
                return result
    return None
