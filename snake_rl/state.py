"""把原始信息翻译成特征向量"""

from typing import TYPE_CHECKING
from collections.abc import Sequence

import numpy as np

from snake_rl import geometry

if TYPE_CHECKING:
    from snake_rl.env import StepResult

#if bonus doesnt exist, distance values = -1
FEATURES = [
    "danger_front", "danger_left", "danger_right",
    "heading_up", "heading_down", "heading_left", "heading_right",
    "food_dr", "food_dc", "food_dist",
    "bonus_dr", "bonus_dc", "bonus_dist", "bonus_exists", "bonus_value",
]

def is_danger(snake: Sequence[tuple[int, int]], action: int, board: geometry.Board) -> float:
    """朝 action 走一步会不会死。
    """
    if geometry.death_reason(snake=snake, action=action, board=board):
        return 1.0
    else:
        return 0.0

def build(obs: "StepResult") -> np.ndarray:
    values: list[float] = []
    direction_ = obs.direction
    values.append(is_danger(snake=obs.snake, action=direction_, board=obs.board))
    values.append(is_danger(snake=obs.snake, action=geometry.LEFT_OF[direction_], board=obs.board))
    values.append(is_danger(snake=obs.snake, action=geometry.RIGHT_OF[direction_], board=obs.board))
    heading = [0.0] * 4
    heading[obs.direction] = 1.0
    values += heading
    food_dr = obs.board.signed_delta(obs.snake[0][0], obs.food[0])
    food_dc = obs.board.signed_delta(obs.snake[0][1], obs.food[1])
    values += [food_dr, food_dc, (abs(food_dr) + abs(food_dc)) / 2]
    if obs.bonus[0] > 0:
        bonus_dr = obs.board.signed_delta(obs.snake[0][0], obs.bonus[1][0])
        bonus_dc = obs.board.signed_delta(obs.snake[0][1], obs.bonus[1][1])
        values += [bonus_dr, bonus_dc, (abs(bonus_dr) + abs(bonus_dc)) / 2]
        values.append(1.0)
    else:
        values += [-1.0, -1.0, -1.0, 0.0]
    values.append(obs.bonus[0] / 6)
    return np.array(values, dtype=np.float32)

