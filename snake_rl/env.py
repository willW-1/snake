"""构建游戏逻辑：只有规则，没有画面、没有算法。"""

from dataclasses import dataclass
import random

# 坐标一律 (row, col)，与 board[r][c] 一致；pygame 的 (x, y) 只在 render.py 里转换。
#0=上(-1,0)  1=下(+1,0)  2=左(0,-1)  3=右(0,+1)
ACTIONS: dict[int, tuple[int, int]] = {0: (-1, 0), 1: (1, 0), 2: (0, -1), 3: (0, 1)}


@dataclass(frozen=True)
class StepResult:
    """一步之后世界的全部原始信息。"""
    snake: tuple[tuple[int, int], ...]
    food: tuple[int, int]
    direction: int
    done: bool
    event: str
    #event:  "reset" / "moved" / "ate" / "hit_wall" / "hit_self" / "timeout"


class SnakeEnv:
    def __init__(self, grid_size: int = 12, seed: int | None = None) -> None:
        self.grid_size = grid_size
        self._rng = random.Random(seed)
        self.reset()

    def reset(self) -> StepResult:
        """开一局新的，返回初始局面。"""
        # TODO: 蛇 3 格放中间、朝右；随机放食物（不能落在蛇身上）；步数归零
        self.snake = [(self.grid_size // 2, self.grid_size // 2 + 1),
                      (self.grid_size // 2, self.grid_size // 2),
                      (self.grid_size // 2, self.grid_size // 2 - 1)]
        self.direction = 3
        #随机放食物
        empty = [(r, c) for r in range(self.grid_size) for c in range(self.grid_size) if (r, c) not in self.snake]      
        self.food = self._rng.choice(empty)
        self.steps = 0
        return StepResult(tuple(self.snake), self.food, self.direction, False, "reset")

    def step(self, action: int) -> StepResult:
        """让蛇按 action 走一步，返回新世界。"""
        #决定3：反向=忽略
        if action + self.direction == 5 or action + self.direction == 1 : action = self.direction
        self.direction = action
        new_head = (self.snake[0][0] + ACTIONS[action][0], self.snake[0][1] + ACTIONS[action][1])
        tail = self.snake[-1]
        del self.snake[-1]
        if new_head[0] in (-1, self.grid_size) or new_head[1] in (-1, self.grid_size): event = "hit_wall"
        elif new_head in self.snake: event = "hit_self"
        elif new_head == self.food: 
            event = "ate"
            self.steps = 0
            empty = [(r, c) for r in range(self.grid_size) for c in range(self.grid_size) if (r, c) not in self.snake]      
            self.food = self._rng.choice(empty)
            self.snake.append(tail)
        else:
            self.steps += 1
            event = "moved"
        self.snake = [new_head, ] + self.snake
        if self.steps >= 100: #连续没吃到苹果的最大步数,默认100
            event = "timeout"
        if event in ("hit_wall", "hit_self", "timeout"): 
            return StepResult(tuple(self.snake), self.food, self.direction, True, event)
        else: return StepResult(tuple(self.snake), self.food, self.direction, False, event)
        # TODO: 1) action → (dr, dc)；反向怎么处理（决定③）
        # TODO: 2) 算出新头坐标
        # TODO: 3) 依次判定：撞墙 → 撞自己 → 吃食物 → 正常移动
        # TODO: 4) 判超时
        # TODO: 5) 组装 StepResult（返回拷贝，见下面的坑①）


if __name__ == "__main__":
    # 调试用：打一局随机策略的文字棋盘，达到 M1
    table = [['*'] * 12 for i in range(12)]
    rng = random.Random(0)
    snake1 = SnakeEnv()
    SnakeEnv.reset(snake1)
    state = SnakeEnv.step(snake1, rng.randint(0, 3))
    while(not state.done):
        for i in range(12):
            for j in range(12):
                if (i, j) in state.snake: table[i][j] = "o"
                elif (i, j) == state.food: table[i][j] = "@"
                else: table[i][j] = "*"
        for i in range(12):
            print(" ".join(table[i]))
        state = SnakeEnv.step(snake1, rng.randint(0, 3))
        print(state.event)
        print()
    print(state.event)
