# Snake DQN

用 PyTorch 手写 DQN，训练一个自己会玩贪吃蛇的 AI。

## 环境

需要 Python 3.14+：

    python -m venv .venv
    .\.venv\Scripts\Activate.ps1
    python -m pip install -r requirements.txt

## 运行

    python -m snake_rl.train     # 训练
    python -m snake_rl.play      # 观战

## 进度

- [x] A 准备工作：环境、Git、项目骨架
- [ ] M1 环境可用：随机策略能跑完一局
- [ ] M2 环境与状态定型
- [ ] M3 组件齐备（回放 / 网络 / 动作选择）
- [ ] M4 闭环跑通（能训练、能出曲线）
- [ ] M5 学会玩（平均分超过随机基线）
- [ ] M6 交付（观战程序 + 测试 + README 完稿）