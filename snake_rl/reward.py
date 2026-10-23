"""按照这一步发生了什么来算出奖励"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from snake_rl.env import StepResult

#默认数字
EAT = 1.0
DIE = -1.0
TIMEOUT = -0.8
BONUS_SCALE = 1.0
WIN = 1.0

MOVE = 0.0
#v1不做引导，没有靠近/远离食物的reward


def compute(prev: "StepResult", new: "StepResult") -> float:
    """返回这一步的即时奖励 r。"""
    # TODO: 按 new.event 分支
    if new.event == "ate":
        return EAT
    elif new.event == "ate_bonus":
        return BONUS_SCALE * prev.bonus[0]
    elif new.event in ("hit_wall", "hit_self"):
        return DIE
    elif new.event == "timeout":
        return TIMEOUT
    elif new.event == "win":
        return WIN
    elif new.event == "moved":
        return MOVE
    else:
        raise ValueError("这一步不能算reward")

if __name__ == "__main__":
    import random
    from snake_rl.env import SnakeEnv
    rng = random.Random(14)
    env = SnakeEnv(grid_size = 12, seed = 23)
    total = 0.0
    new = env.reset()
    for _ in range(1000):
        action = rng.randint(0, 3)
        prev = new
        new = env.step(action)
        r = compute(prev, new)
        total += r
        if r != 0:
            print(f"{new.event:<10} r = {r:.2f}  scores = {env.scores}")
        if new.done:
            break
    print("累计奖励", round(total, 2), "game scores", env.scores)
