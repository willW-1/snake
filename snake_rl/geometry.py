"""棋盘几何与死亡判定 —— 全项目唯一一份「边界 / 环绕」规则。
"""

from collections.abc import Sequence
from dataclasses import dataclass

Pos = tuple[int, int]

ACTIONS: dict[int, Pos] = {0: (-1, 0), 1: (1, 0), 2: (0, -1), 3: (0, 1)}
LEFT_OF: dict[int, int] = {0: 2, 1: 3, 2: 1, 3: 0}
RIGHT_OF: dict[int, int] = {0: 3, 1: 2, 2: 0, 3: 1}


@dataclass(frozen=True)
class Board:
    grid_size: int = 12
    wrap: bool = False

    def next_pos(self, pos: Pos, action: int) -> Pos:
        """走一步之后的新坐标（单轴，不对整条蛇负责）。
        """
        if self.wrap:
            x = (pos[0] + ACTIONS[action][0]) % self.grid_size
            y = (pos[1] + ACTIONS[action][1]) % self.grid_size
        else:
            x = pos[0] + ACTIONS[action][0]
            y = pos[1] + ACTIONS[action][1]
        return (x, y)

    def signed_delta(self, a: int, b: int) -> float:
        """从 a 到 b 的有符号差，归一化到 [-1, 1]。
        """
        if self.wrap:
            d = (b - a + (self.grid_size // 2)) % self.grid_size - self.grid_size // 2
            return d / (self.grid_size // 2)
        else:
            return (b - a) / (self.grid_size - 1)

    def dist(self, p: Pos, q: Pos) -> float:
        """p 到 q 的距离，归一化到 [0, 1]。
        """
        abs_x = abs(self.signed_delta(p[0], q[0]))
        abs_y = abs(self.signed_delta(p[1], q[1]))
        return (abs_x + abs_y) / 2
        


def death_reason(snake: Sequence[Pos], action: int, board: Board) -> str | None:
    """朝 action 走一步会死吗？
    死因返回 "hit_wall" / "hit_self"，活着返回 None。, size=1必死
    """
    next_head = board.next_pos(pos=snake[0], action=action)
    if board.wrap:
        if next_head in snake[:-1]:
            return "hit_self"
        else:
            return None
    else:
        if next_head in snake[:-1]:
            return "hit_self"
        elif next_head[0] in (-1, board.grid_size) or next_head[1] in (-1, board.grid_size):
            return "hit_wall"
        else:
            return None
