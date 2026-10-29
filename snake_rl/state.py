"""把原始信息翻译成特征向量"""

from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from snake_rl.env import StepResult

FEATURES = [
    "danger_front", "danger_left", "danger_right",
    "heading_up", "heading_down", "heading_left", "heading_right",
    "food_dr", "food_dc", "food_dist",
    "bonus_dr", "bonus_dc", "bonus_dist", "bonus_exists", "bonus_value",
]

LEFT_OF = {0: 2, 1: 3, 2: 1, 3: 0}
RIGHT_OF = {0: 3, 1: 2, 2: 0, 3: 1}

ACTIONS = {0: (-1, 0), 1: (1, 0), 2: (0, -1), 3: (0, 1)}

def _is_danger(snake: list, action: int, grid_size: int = 12) -> float:
    """朝 action 走一步会不会死。

    只用 snake[:-1]（排除尾巴）判定：尾巴会让位。
    不需要特判"这一步是否吃到东西"——吃到东西意味着 new_head == food，
    而食物永远不在蛇身上，所以那一步 new_head 不可能撞到任何蛇身（含尾巴）。
    这个结论依赖 env 的不变量「food/bonus 不与蛇重叠」，由
    tests/test_env.py::test_food_never_on_snake 守卫。
    """

    new = (snake[0][0] + ACTIONS[action][0], snake[0][1] + ACTIONS[action][1])
    if new[0] in (-1, grid_size) or new[1] in (-1, grid_size) or new in snake[:-1]:
        return 1.0
    else:
        return 0.0

def build(state: "StepResult", grid_size: int = 12) -> np.ndarray:
    values: list[float] = []
    direction_ = state.direction
    values.append(_is_danger(snake=state.snake, action=direction_, grid_size=grid_size))
    values.append(_is_danger(snake=state.snake, action=LEFT_OF[direction_], grid_size=grid_size))
    values.append(_is_danger(snake=state.snake, action=RIGHT_OF[direction_], grid_size=grid_size))
    heading = [0.0] * 4
    heading[state.direction] = 1.0
    values += heading
    food_dr = abs(state.food[0] - state.snake[0][0]) / (grid_size - 1)
    food_dc = abs(state.food[1] - state.snake[0][1]) / (grid_size - 1)
    values += [food_dr, food_dc, food_dr + food_dc]
    bonus_dr = abs(state.bonus[1][0] - state.snake[0][0]) / (grid_size - 1)
    bonus_dc = abs(state.bonus[1][1] - state.snake[0][1]) / (grid_size - 1)
    values += [bonus_dr, bonus_dc, bonus_dr + bonus_dc]
    if state.bonus[0] > 0:
        values.append(1.0)
    else:
        values.append(0.0)
    values.append(state.bonus[0] / 6)
    return np.array(values, dtype=np.float32)

