"""所有超参数集中在这里：只有数据，没有逻辑。"""

from dataclasses import dataclass


@dataclass
class TrainConfig:
    """一次训练需要的全部参数。"""

    grid_size: int = 12             # 棋盘大小：12x12
    gamma: float = 0.9              # 折扣因子：未来奖励打几折
    lr: float = 1e-3                # 学习率：参数每次拧多大
    batch_size: int = 64            # 每次复习几条经历
    replay_capacity: int = 100_000  # 记忆库最多存多少条
    