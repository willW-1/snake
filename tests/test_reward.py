from snake_rl.env import SnakeEnv
from snake_rl import reward

def test_reward_compute() -> None:
    actions = [2, 0, 2, 0]
    env = SnakeEnv()
    env.snake = [(3, 5)]
    env.bonus = [6, (1, 2)]
    env.food = (2, 2)
    env.direction = 2
    new = env.step(2)
    total = 0.0
    for action in actions:
        prev = new
        new = env.step(action)
        r = reward.compute(prev, new)
        total += r
        if new.event == "move":
            assert r == 0.0, "move wrong"
        elif new.event == "ate":
            assert r == 1.0, "ate wrong"
        assert total == env.scores, "reward wrong"

def 
