import logging
import time
from collections import deque

from puzzle15.solver.board import Board, get_neighbors, manhattan_distance, matrix_to_tuple
from puzzle15.solver.progress import ProgressLogger
from puzzle15.solver.result import SearchTimeout, SolveResult, make_result

logger = logging.getLogger(__name__)


def solve_bfs(initial_matrix: Board, goal_matrix: Board, timeout: float | None = None) -> SolveResult:
    initial = matrix_to_tuple(initial_matrix)
    goal = matrix_to_tuple(goal_matrix)

    queue = deque([(initial, [initial])])
    visited = {initial}
    start_time = time.time()
    explored = 0
    progress = ProgressLogger(logger, "BFS", start_time)

    logger.debug("[BFS] starting: timeout=%s initial_distance=%d", timeout, manhattan_distance(initial, goal))
    try:
        while queue:
            if timeout and (time.time() - start_time > timeout):
                raise SearchTimeout()

            state, path = queue.popleft()
            explored += 1
            progress.maybe_log(explored, queue=len(queue), visited=len(visited))

            if state == goal:
                result = make_result(True, start_time, explored, path)
                logger.debug("[BFS] solved: time=%ss steps=%d explored=%d", result.time_seconds, result.steps, explored)
                return result

            for neighbor in get_neighbors(state):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))

        logger.debug("[BFS] exhausted search space with no solution: explored=%d", explored)
        return make_result(False, start_time, explored)

    except SearchTimeout:
        logger.debug("[BFS] timeout reached: explored=%d queue=%d", explored, len(queue))
        return make_result(False, start_time, explored)
