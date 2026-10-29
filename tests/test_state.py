from snake_rl.env import SnakeEnv
from snake_rl import state

import random
import numpy as np

def test_shape_and_type() -> None:
    env = SnakeEnv(grid_size=12, seed=1)
    obs = env.reset()
    values = state.build(obs=obs, grid_size=env.grid_size)
    assert values.shape == (len(state.FEATURES), ), f"shape wrong, shape={values.shape}"
    assert values.dtype == np.float32

def test_values_range() -> None:
    env = SnakeEnv(grid_size=12, seed=1)
    obs = env.reset()
    values = state.build(obs=obs, grid_size=env.grid_size)
    assert values.min() >= -1, f"min wrong, values={values}"
    assert values.max() <= 1, f"max wrong, values={values}"

def test_towards_danger() -> None:
    env = SnakeEnv(grid_size=12, seed=1)
    env.snake = [(0, 1)]
    env.direction = 2
    env.food = (12, 12)
    obs = env.step(2)
    values = state.build(obs=obs, grid_size=env.grid_size)
    assert values[0] == 1.0, f"wrong danger, value={value[0]}"

def test_direction_change() -> None:
    env = SnakeEnv(grid_size=12, seed=1)
    obs = env.reset()
    env.snake = [(6, 6)]
    for i in range(4):
        real_dircection = [0.0] * 4
        real_dircection[i] = 1.0
        env.direction = i
        obs = env.step(i)
        values = state.build(obs=obs, grid_size=env.grid_size)
        assert all(values[i + 3] == real_dircection[i] for i in range(4)), f"wrong direction, direction={values[3:7]} real={real_dircection}"
    obs = env.reset()
    env.snake = [(1, 0)]
    env.direction = 0
    obs = env.step(0)
    values = state.build(obs=obs, grid_size=env.grid_size)
    assert values[0] == 1.0 and values[1] == 1.0 and values[2] == 0.0, f"wrong danger, values={vaules[0:3]}, real=[1, 1, 0]"
    obs = env.step(3)
    values = state.build(obs=obs, grid_size=env.grid_size)
    assert values[0] == 0.0 and values[1] == 1.0 and values[2] == 0.0, f"wrong danger, values={vaules[0:3]}, real=[0, 1, 0]"

def test_tail_can_move() -> None:
    env = SnakeEnv(grid_size=12, seed=1)
    env.food = (0, 0)
    env.snake = [(5, 5), (5, 6), (4, 6), (3, 6), (3, 5), (3, 4)]
    env.direction = 0
    obs = env.step(0)
    values = state.build(obs=obs, grid_size=env.grid_size)
    assert values[0] == 0.0, f"wrong danger, danger={values[0]}"

def test_real_danger() -> None:
    env = SnakeEnv(grid_size=8, seed=1)
    rng = random.Random(1234)
    obs = env.reset()
    env.snake = [(3, 2), (3, 3), (3, 4), (3, 5), (3, 6)]
    env.direction = 2
    for _ in range(10000):
        action = rng.randint(0, 3)
        for i in range(4):
            if state.is_danger(snake=env.snake, action=i, grid_size=env.grid_size) == 1.0 and i + env.direction != 1 and i + env.direction != 5:
                obs = env.step(i)
                assert obs.done == True, f"wrong done, snake={obs.snake}"
                obs = env.reset()
                env.snake = [(3, 2), (3, 3), (3, 4), (3, 5), (3, 6)]
                env.direction = 2
                break
        else:
            obs = env.step(action=action)

def test_food_distance() -> None:
    env = SnakeEnv(grid_size=12, seed=1)
    env.snake = [(5, 5)]
    env.food = (0, 0)
    obs = env.step(3)
    values = state.build(obs=obs, grid_size=env.grid_size)
    assert abs(values[7] - 5 / (env.grid_size - 1)) < 1e6, f"wrong food_row, fr={values[7]}"
    assert abs(values[8] - 6 / (env.grid_size - 1)) < 1e6, f"wrong food_column, fc={values[8]}"
    assert abs(values[9] - 11 / (env.grid_size - 1) * 2) < 1e6, f"wrong food_distance, fd={values[9]}"

def test_state_bonus() -> None:
    env = SnakeEnv(grid_size=12, seed=1)
    env.snake = [(5, 5)]
    env.food = (12, 12)
    env.bonus = [6, (0, 0)]
    obs = env.step(3)
    values = state.build(obs=obs, grid_size=env.grid_size)
    assert abs(values[10] - 5 / (env.grid_size - 1)) < 1e6, f"wrong bonus_row, r={values[10]}"
    assert abs(values[11] - 6 / (env.grid_size - 1)) < 1e6, f"wrong bonus_column, c={values[11]}"
    assert abs(values[12] - 11 / (env.grid_size - 1) * 2) < 1e6, f"wrong bonus_distance, d={values[12]}"
    assert values[13] == 1.0, f"wrong bonus_exist, exist={values[13]}"
    assert abs(values[14] - 5 / 6 < 1e6), f"wrong bonus points, point={values[13]}"

    