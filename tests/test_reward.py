from snake_rl.env import SnakeEnv
from snake_rl import reward
import pytest

def test_reward_compute() -> None:
    actions = [2, 0, 2, 0]
    rewards = []
    env = SnakeEnv(grid_size=12, seed=1)
    env.snake = [(3, 5)]
    env.bonus = [6, (1, 2)]
    env.food = (2, 2)
    env.direction = 2
    new = env.step(2)
    total = 0.0
    for action in actions:
        prev = new
        new = env.step(action)
        r = reward.compute(prev=prev, new=new)
        rewards.append(r)
        pos_total = sum(r for r in rewards if r > 0)
        if new.event == "move":
            assert r == 0.0, "move wrong"
        elif new.event == "ate":
            assert r == 1.0, "ate wrong"
        assert pos_total == env.scores, "reward wrong"

def test_reward_death() -> None:
    env = SnakeEnv(grid_size=12, seed=1)
    env.snake = [(0, 1)]
    env.food = (12, 12)
    env.direction = 2
    prev = env.step(2)
    new = env.step(2)
    assert reward.compute(prev=prev, new=new) == reward.DIE, "hit_wall wrong"
    prev = env.reset()
    env.food = (12, 12)
    env.snake = [(5, 5), (5, 6), (4, 6), (4, 5), (4, 4), (4, 3), (5, 3), (6, 3), (7, 3)]
    env.direction = 2
    prev = env.step(2)
    new = env.step(2)
    assert reward.compute(prev=prev, new=new) == reward.DIE, "hit_self wrong"

def test_reward_timeout() -> None:
    env = SnakeEnv(grid_size=12, seed=1)
    env.steps = 99
    state = env.step(3)
    assert reward.compute(prev=state, new=state) == reward.TIMEOUT, "Timeout wrong"

def test_reward_uses_prev_value() -> None:
    env = SnakeEnv(grid_size=12, seed=1)
    env.snake = [(5, 5)]
    env.direction = 2
    env.food = (0, 0)
    env.bonus = [6, (5, 3)]
    prev = env.step(2)
    new = env.step(2)
    assert new.event == "ate_bonus", f"wrong event, event = {new.event}"
    assert reward.compute(prev=prev, new=new) == 5.0, f"bonus wrong, point get = {reward.compute(prev=prev, new=new)}"

def test_reward_rejects_reset_frame() -> None:
    env = SnakeEnv(grid_size=12, seed=1)
    state = env.reset()
    with pytest.raises(ValueError):
        reward.compute(state, state)
