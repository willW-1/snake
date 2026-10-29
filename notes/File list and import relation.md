# File list and import relation

> A4（项目骨架设计）的记录。分三部分：初稿 → 复审发现的问题 → 定稿。
> 保留初稿是为了以后能看清"当时错在哪、为什么改"。

## 0. 五个依赖各自的作用（前置知识）

| 包          | 角色   | 一句话                                   |
| ---------- | ---- | ------------------------------------- |
| numpy      | 数据容器 | 状态向量、棋盘、批量样本                          |
| torch      | 算法引擎 | 网络结构 + 自动求导（`loss.backward()` 替我们算梯度） |
| pygame-ce  | 眼睛   | 画格子、接收键盘（**只在观战时用，不参与训练**）            |
| matplotlib | 仪表盘  | 把训练曲线（得分/损失/ε）存成图                     |
| pytest     | 保险丝  | 自动测试，防止改坏了自己不知道                       |

---

## 1. 我的初稿（复审前）

| file | responsibility | need pygame? | need torch? | who to import? |
| --- | --- | --- | --- | --- |
| env.py | game rule | no | no | numpy |
| render.py | show the scene to screen | yes | no | pygame, env |
| state.py | 表示当前状态 | no | no | numpy, env |
| reward.py | 奖励函数 | no | no | env in __main__ |
| replay.py | 经验回放缓冲区 | no | no | state |
| network.py | Q网络 | no | yes | numpy, torch |
| agent.py | 动作选择与推理 | no | no | state, replay, env, network, config |
| train.py | 训练循环 | no | yes | all above |
| config.py | 超参数 | no | no | NA |
| play.py | 玩游戏 | yes | no | pygame, env |

---

## 2. 复审发现的问题

**总评**：`need pygame?` 那一列 **10/10 全对**；没有循环依赖。
所有问题都是同一个毛病 —— **import 写多了**。

| 位置 | 问题 | 原因 |
|---|---|---|
| `state.py` | 多写了 `env` | state 只需要**原始数据**，不需要游戏对象。这样能拿假数据单独测它 |
| `replay.py` | 多写了 `state` | replay 是个**盒子**，只负责存取，不需要知道状态长什么样 |
| `agent.py` | 多了 `state`、`replay`、`env` | agent 只回答"这个局面走哪"，不需要知道经历存在哪、游戏规则是什么 |
| `train.py` | 写了 "all above" | 它是顶层组装者，允许 import 全部，但要能列出**具体**用了谁 |
| `play.py` | 漏了 `network` | play 的意义是"加载权重看 AI 玩"，没有 network 就加载不了模型 |
| `render.py` | `env` 其实可以不要 | 渲染只需要"画什么"的数据，由调用者传进来 |

**提炼成一条通则**：

> 依赖不是越多越方便，而是**越少越好**。每多一个 import，就多一根绳子把你绑住。

**一行自检**：把这个 import 删掉，跑一下 —— **还能用，它就是多余的**。

---

## 3. 我做出的两个设计决定

1. **封装**：把"numpy → 张量"的转换和"加载/保存权重"都封进 `network.py`。
   → 好处：`agent.py` 和 `play.py` 都不用直接 import torch。
2. **`env` 只返回原始信息**（蛇的位置、食物位置、方向、结束标志、事件），
   **不返回特征向量**。特征向量的转换交给 `state.py`。
   → 好处：环境不认识"状态表示"，以后换一种状态设计不用改环境。
   → 代价：调用方（`train` / `play`）要自己多调一次 `state.build(...)`。

---

## 4. 定稿表

| #   | 文件           | 职责                                      | 需要 pygame? | 需要 torch? | 它 import 谁                                                                |
| --- | ------------ | --------------------------------------- | ---------- | --------- | ------------------------------------------------------------------------- |
| 1   | `config.py`  | 超参数集中定义（只有数据，没有逻辑）                      | 否          | 否         | 无                                                                         |
| 2   | `env.py`     | 游戏规则：`reset` / `step`，返回**原始信息**        | 否          | 否         | `numpy`（可选）                                                               |
| 3   | `reward.py`  | 按"这一步发生了什么"算出奖励                         | 否          | 否         | 无（纯函数）                                                                    |
| 4   | `state.py`   | 把原始信息翻译成一组数字（特征向量）                      | 否          | 否         | `numpy`                                                                   |
| 5   | `replay.py`  | 存经历、随机抽一批                               | 否          | 否         | `numpy`                                                                   |
| 6   | `network.py` | Q 网络：状态 → 4 个 Q 值；封装张量转换与 `save`/`load` | 否          | **是**     | `torch`                                                                   |
| 7   | `agent.py`   | 看局面选动作（ε-greedy / 纯贪心）                  | 否          | 否         | `network`, `config`, `random`                                             |
| 8   | `render.py`  | 把局面画到屏幕（只接收要画的数据）                       | **是**      | 否         | `pygame`, `config`                                                        |
| 9   | `train.py`   | 训练循环，组装一切                               | 否          | **是**     | `env`, `state`, `reward`, `replay`, `network`, `agent`, `config`, `torch` |
| 10  | `play.py`    | 加载权重，看 AI 玩                             | **是**      | 否         | `pygame`, `env`, `state`, `render`, `network`, `config`                   |

**关于两个"看设计"的格子（已按上面的决定定下来）**：

- `agent.py` 不需要 torch（张量转换在 network 里）✅
- `play.py` 不需要 torch（加载权重在 network 里）✅
- `train.py` **仍然**需要 torch —— 它要建优化器（`torch.optim.Adam`）和损失函数。
  如果哪天想把"训练一步"也封进 `agent.py`，train 就能不碰 torch。这是**可选的重构**，现在不做。

---

## 5. 两条不变量（以后随时可自检）

- **pygame 只出现在 2 个文件里**：`render.py`、`play.py`。
  哪天它出现在别处 → 说明训练被界面污染了。
- **torch 只出现在 2 个文件里**：`network.py`、`train.py`。
  哪天它出现在 `env.py` → 说明游戏逻辑被算法污染了。

这两条比记住每一格答案有用，因为它们**可以在 10 秒内查完**。

---

## 6. 依赖分层（最后一列就是箭头）

```
第 0 层  地基
    config.py            谁都能用；它不 import 任何项目内模块

第 1 层  互不依赖的原语
    env.py               → numpy
    reward.py            → （无）
    state.py             → numpy
    replay.py            → numpy
    network.py           → torch

第 2 层  组装原语
    agent.py             → network, config, random
    render.py            → pygame, config

第 3 层  顶层（可以 import 下面所有）
    train.py             → env, state, reward, replay, network, agent, config, torch
    play.py              → env, state, render, network, config
```

**三条铁律**

1. 底层不许 import 上层（`env.py` 里出现 `import train` 就是错的）
2. `env.py` 里不许出现 `pygame` 和 `torch`
3. 不许有循环依赖
