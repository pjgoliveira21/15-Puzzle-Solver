import logging
import time
from collections import deque

from puzzle15.solver.board import Board, get_neighbors, matrix_to_tuple
from puzzle15.solver.result import SearchTimeout, SolveResult, make_result

logger = logging.getLogger(__name__)


def solve_bfs(initial_matrix: Board, goal_matrix: Board, timeout: float | None = None) -> SolveResult:
    initial = matrix_to_tuple(initial_matrix)
    goal = matrix_to_tuple(goal_matrix)

    queue = deque([(initial, [initial])])
    visited = {initial}
    start_time = time.time()
    explored = 0

    logger.debug("[BFS] starting (timeout=%s)", timeout)
    try:
        while queue:
            if timeout and (time.time() - start_time > timeout):
                raise SearchTimeout()

            state, path = queue.popleft()
            explored += 1

            if state == goal:
                result = make_result(True, start_time, explored, path)
                logger.debug("[BFS] solution found (%ss, %s steps)", result.time_seconds, result.steps)
                return result

            for neighbor in get_neighbors(state):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))

        return make_result(False, start_time, explored)

    except SearchTimeout:
        logger.debug("[BFS] timeout reached (explored=%s)", explored)
        return make_result(False, start_time, explored)
