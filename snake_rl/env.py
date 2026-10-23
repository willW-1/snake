"""构建游戏逻辑：只有规则，没有画面、没有算法。"""

from dataclasses import dataclass
import random

# 坐标一律 (row, col)，与 board[r][c] 一致；pygame 的 (x, y) 只在 render.py 里转换。
#0=上(-1,0)  1=下(+1,0)  2=左(0,-1)  3=右(0,+1)
ACTIONS: dict[int, tuple[int, int]] = {0: (-1, 0), 1: (1, 0), 2: (0, -1), 3: (0, 1)}

#吃 bonus 后，新 obs 里的 bonus 已经是 (0, ()) 或者新生成的 6。 所以奖励函数要取"吃到的 bonus 值"，必须从前一帧 prev.bonus[0] 读，不能从 new.bonus 读。

@dataclass(frozen=True)
class StepResult:
    """一步之后世界的全部原始信息。"""
    snake: tuple[tuple[int, int], ...]
    food: tuple[int, int]
    bonus: tuple[int, tuple[int, int]] | tuple[int, tuple()]
    direction: int
    done: bool
    event: str
    #event:  "reset" / "moved" / "ate" / "hit_wall" / "hit_self" / "timeout" / "win" / "ate_bonus"


class SnakeEnv:
    def __init__(self, grid_size: int = 12, seed: int | None = None) -> None:
        self.grid_size = grid_size
        self._rng = random.Random(seed)
        self.reset()

    def reset(self) -> StepResult:
        """开一局新的，返回初始局面。
        """
        self._done = False
        self.snake = [(self.grid_size // 2, self.grid_size // 2 + 1),
                      (self.grid_size // 2, self.grid_size // 2),
                      (self.grid_size // 2, self.grid_size // 2 - 1)]
        self.direction = 3
        #随机放食物
        empty = [(r, c) for r in range(self.grid_size) for c in range(self.grid_size) if (r, c) not in self.snake]      
        self.food = self._rng.choice(empty)
        self.steps = 0
        self.scores = 0
        self.bonus = [0, ()]
        self.haveeaten = False
        return StepResult(tuple(self.snake), self.food, tuple(self.bonus), self.direction, False, "reset")

    def step(self, action: int) -> StepResult:
        """让蛇按 action 走一步，返回新世界。
            0=上(-1,0)  1=下(+1,0)  2=左(0,-1)  3=右(0,+1)
        """
        #决定3：反向=忽略
        if self._done:
            raise ValueError("蛇已经死了，先 reset()")
        if action + self.direction == 5 or action + self.direction == 1 : action = self.direction
        self.direction = action
        new_head = (self.snake[0][0] + ACTIONS[action][0], self.snake[0][1] + ACTIONS[action][1])

        #撞死的时候朝向就是准备朝向的地方
        tail = self.snake[-1]
        del self.snake[-1]

        #撞墙判定
        if new_head[0] in (-1, self.grid_size) or new_head[1] in (-1, self.grid_size): 
            event = "hit_wall"
            self.snake.append(tail)

        #撞自己判定
        elif new_head in self.snake: 
            event = "hit_self"
            self.snake.append(tail)
        
        #吃bonus，会变长一格，也会重置timeout判例，这是设计
        elif new_head == self.bonus[1]:
            event = "ate_bonus"
            self.haveeaten = False
            self.steps = 0
            self.scores += self.bonus[0]
            self.snake.append(tail)
            self.snake = [new_head, ] + self.snake
            self.bonus = [0, ()]
        
        #吃food
        elif new_head == self.food: 
            event = "ate"
            self.steps = 0
            self.scores += 1
            self.snake.append(tail)
            self.snake = [new_head, ] + self.snake
            self.haveeaten = True
            empty = [(r, c) for r in range(self.grid_size) for c in range(self.grid_size) if ((r, c) not in self.snake and (r, c) != self.bonus[1])]
            #设计，win excludes bonus grid
            if not empty: event = "win"#赢了之后food 无意义
            else: self.food = self._rng.choice(empty)

        #move
        else:
            self.steps += 1
            event = "moved"
            self.snake = [new_head, ] + self.snake
            if self.steps >= 100: #连续没吃到苹果的最大步数,默认100
                event = "timeout"

        #bonus-1
        if self.bonus[0] > 0: 
            self.bonus[0] -= 1
            if self.bonus[0] == 0: self.bonus[1] = ()

        #bonus的判定与生成
        if(self.bonus[0] == 0 and self.scores % 6 == 0 and self.haveeaten):
            empty = [(r, c) for r in range(self.grid_size) for c in range(self.grid_size) if (r, c) not in self.snake + [new_head ,self.food]]
            if empty:
                self.bonus[0] = 6
                self.bonus[1] = self._rng.choice(empty)
                self.haveeaten = False

        if event in ("hit_wall", "hit_self", "timeout", "win"): 
            self._done = True
        return StepResult(tuple(self.snake), self.food, tuple(self.bonus), self.direction, self._done, event)
    
    '''
    def return_status(self) -> StepResult:
        """ONLY FOR TEST !!!"""
        return StepResult(tuple(self.snake), self.food, tuple(self.bonus), self.direction, self._done, "test")
    '''


if __name__ == "__main__":
    # 调试用：打一局随机策略的文字棋盘，达到 M1
    rng = random.Random(1)
    snake1 = SnakeEnv(seed = 1)
    table = [['*'] * snake1.grid_size for _ in range(snake1.grid_size)]
    state = snake1.step(rng.randint(0, 3))
    while(not state.done):
        for i in range(snake1.grid_size):
            for j in range(snake1.grid_size):
                if (i, j) in state.snake: table[i][j] = "o"
                elif (i, j) == state.food: table[i][j] = "@"
                elif state.bonus[1] == (i, j): table[i][j] = str(state.bonus[0])
                else: table[i][j] = "*"
        for i in range(snake1.grid_size):
            print(" ".join(table[i]))
        state = snake1.step(rng.randint(0, 3))
        print(len(snake1.snake), snake1.scores)
        print()
    print(state.event)
