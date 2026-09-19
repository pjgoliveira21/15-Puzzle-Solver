import heapq
import logging
import time

from puzzle15.solver.board import Board, get_neighbors, manhattan_distance, matrix_to_tuple
from puzzle15.solver.progress import ProgressLogger
from puzzle15.solver.result import SearchTimeout, SolveResult, make_result

logger = logging.getLogger(__name__)


def solve_astar(initial_matrix: Board, goal_matrix: Board, timeout: float | None = None) -> SolveResult:
    initial = matrix_to_tuple(initial_matrix)
    goal = matrix_to_tuple(goal_matrix)

    heap = []
    tie_breaker = 0
    g_costs = {initial: 0}
    start_time = time.time()
    explored = 0
    progress = ProgressLogger(logger, "A*", start_time)

    h_init = manhattan_distance(initial, goal)
    heapq.heappush(heap, (h_init, tie_breaker, initial, [initial]))

    logger.debug("[A*] starting: timeout=%s initial_distance=%d", timeout, h_init)
    try:
        while heap:
            if timeout and (time.time() - start_time > timeout):
                raise SearchTimeout()

            f, _, state, path = heapq.heappop(heap)
            explored += 1
            progress.maybe_log(explored, heap=len(heap), f=f)

            if state == goal:
                result = make_result(True, start_time, explored, path)
                logger.debug("[A*] solved: time=%ss steps=%d explored=%d", result.time_seconds, result.steps, explored)
                return result

            for neighbor in get_neighbors(state):
                new_g = g_costs[state] + 1
                if neighbor not in g_costs or new_g < g_costs[neighbor]:
                    g_costs[neighbor] = new_g
                    tie_breaker += 1
                    h = manhattan_distance(neighbor, goal)
                    heapq.heappush(heap, (new_g + h, tie_breaker, neighbor, path + [neighbor]))

        logger.debug("[A*] exhausted search space with no solution: explored=%d", explored)
        return make_result(False, start_time, explored)

    except SearchTimeout:
        logger.debug("[A*] timeout reached: explored=%d heap=%d", explored, len(heap))
        return make_result(False, start_time, explored)
