"""env.py 的测试。

跑法（在项目根目录）：
    python -m pytest -q

为什么必须带 `python -m`：它会把当前目录放进 sys.path，
import snake_rl 才找得到 —— 和 `python -m snake_rl.env` 是同一个道理。
直接敲 `pytest -q` 很可能给你 ModuleNotFoundError。

用例命名规则（pytest 只认这个）：
    - 文件名 test_*.py
    - 函数名 test_*
    - 用 assert 直接断言（不需要 assertEqual 那一套）
"""

import pytest
import random

from snake_rl.env import SnakeEnv


# ============================================================
# 示范 1：最基本的三明治结构（Arrange 摆 → Act 做 → Assert 断言）
# ============================================================

def test_reset_initial_state() -> None:
    """开局的蛇是 3 格、居中朝右，食物不与蛇重叠。"""
    # --- Arrange：摆出被测对象 ---
    env = SnakeEnv(grid_size=5, seed=0)

    # --- Act：做那个动作 ---
    result = env.reset()

    # --- Assert：断言结果 ---
    assert len(result.snake) == 3
    assert result.snake[0] == (2, 3)      # 头在中间偏右
    assert result.direction == 3          # 3 = 右
    assert result.done is False
    assert result.event == "reset"
    assert result.food not in result.snake


# ============================================================
# 示范 2：白盒摆局面（这个项目最需要的技巧）
#
# 随机测试探不到"尾巴让位"这条规则：我实测 5932 步里只出现过
# 1 次 hit_self。所以必须手工摆一个确定的局面。
# 测试可以直接改 env 的内部状态 —— 测环境时这是正当的。
# ============================================================

def test_moving_into_vacating_tail_survives() -> None:
    """头走进"尾巴正要腾出的那一格"不算撞自己。

    局面（grid 5）：
        (1,3) (1,4)          <- 身体绕了个 U 形
        (2,3) (2,4)          <- 头在 (2,3)，尾巴在 (2,4)
    头往右走 → (2,4)，正是尾巴那一格。尾巴会腾出来，所以不该死。
    """
    # --- Arrange：手工摆 ---
    env = SnakeEnv(grid_size=5, seed=0)
    env.snake = [(2, 3), (1, 3), (1, 4), (2, 4)]   # 头在前
    env.direction = 3                              # 朝右
    env.food = (0, 0)                              # 别让它吃到，干扰判断

    # --- Act ---
    result = env.step(3)                           # 3 = 右

    # --- Assert ---
    assert result.done is False
    assert result.event == "moved"
    assert result.snake[0] == (2, 4)               # 头确实进了那一格
    assert len(result.snake) == 4                  # 没吃食物，长度不变


# ============================================================
# 下面 7 个是 TODO：骨架和名字我给了，"怎么断言"由你写。
# 写完把 pytest.skip(...) 那一行删掉。
#
# 提示：Assert 部分请用固定局面或明确的循环上界，
#      别写成"跑随机然后祈祷它能碰到"。
# ============================================================

def test_food_never_on_snake() -> None:
    """回归测试：食物永远不能落在蛇身上。

    这是修掉的那个 bug 的守卫。建议：对 grid 4/5/6 各几个 seed，
    随机走若干步，断言 `result.food not in result.snake`（win 的终局除外）。
    """
    #arrange
    combo = [(4, 123), (4, 214), (5, 2139), (5, 1234), (6, 1238), (6, 19238)]
    for grid, seed in combo:
        env = SnakeEnv(grid_size = grid, seed = seed)
        action_rng = random.Random(seed + 100)
        result = env.reset()
        #act
        for _ in range(500):
            if result.done:
                result = env.reset()
            action = action_rng.randint(0, 3)
            result = env.step(action)
            if result.event == "win": continue
            #assert
            assert result.food not in result.snake, (
                f"food {result.food} 落在蛇上: "
                f"grid = {grid}, seed = {seed}"
            )

def test_length_grows_only_when_eating() -> None:
    """长度只在 ate 时 +1，其他事件长度不变。"""
    env = SnakeEnv(grid_size = 6, seed = 1234)
    env.snake = [(2, 2), (2, 3), (2, 4)]
    env.food = (2, 1)
    env.direction = 2
    result = env.step(2)
    assert len(result.snake) == 4, f"特殊情况的eat出错了, len = {len(result.snake)}"
    result = env.reset()
    action_rng = random.Random(123)
    for _ in range(500):
        if result.done:
            result = env.reset()
        action = action_rng.randint(0, 3)
        len1 = len(result.snake)
        result = env.step(action)
        len2 = len(result.snake)
        if result.event == "win": continue
        elif result.event == "ate":
            assert len1 == len2 - 1, f"eat出错了，原len = {len1}, 新len = {len2}"
        else:
            assert len1 == len2, f"其他情况出错了，原len = {len1}, 新len = {len2}, event = {result.event}"


def test_reverse_action_is_ignored() -> None:
    """朝右时选"左"，蛇仍然往右走。

    白盒摆一个只有 3 格的横条局面，然后传反向 action，
    断言新头落在"继续直行"的位置，而不是掉头。
    """
    env = SnakeEnv(grid_size = 6, seed = 1234)
    env.snake = [(2, 4), (2, 3), (2, 2)]
    env.food = (0, 0)
    env.direction = 3
    result = env.step(2)
    assert result.snake[0] == (2, 5), f"蛇头在, {result.snake[0]}, 应该在（2，5）"


def test_hit_wall_terminal_state_is_in_bounds() -> None:
    """撞墙的终局观测里，每一格都还在棋盘内（这是修掉的 bug 2）。"""
    env = SnakeEnv(grid_size = 6, seed = 1233)
    result = env.reset()
    action_rng = random.Random(123)
    saw_wall = False
    for _ in range(500):
        if result.done: result = env.reset()
        action = action_rng.randint(0, 3)
        result = env.step(action)
        if result.event == "hit_wall":
            saw_wall = True
            assert all(0 <= i < 6 and 0 <= j < 6 for i, j in result.snake), (
                f"撞墙后, 有蛇出现"
            )
    assert saw_wall, "这次检测没随机到，要不再测一次？"

def test_timeout_after_max_steps_without_food() -> None:
    """连续 100 步没吃到食物 → event == "timeout"。

    白盒提示：把 env.steps 直接摆到 99，再走一步合法的、
    不会吃到食物的移动。
    """
    env = SnakeEnv(grid_size = 12, seed = 123)
    env.snake = [(1, 1)]
    env.food = (0, 0)
    env.steps = 99
    env.direction = 0
    result = env.step(0)
    assert result.done == True and result.event == "timeout", (
        f"没有正常timeout, event = {result.event}, done = {result.done}"
    )


def test_hit_wall_is_not_reported_as_timeout() -> None:
    """撞墙时必须报 hit_wall，不能被 timeout 覆盖（这是修掉的 bug 3）。"""
    env = SnakeEnv(grid_size = 12, seed = 123)
    env.steps = 99
    env.snake = [(0, 0)]
    env.food = (12, 12)
    env.direction = 2
    result = env.step(2)
    assert result.done == True and result.event == "hit_wall", (
        f"撞墙覆盖失败，event = {result.event}, done = {result.done}"
    )


def test_step_after_done_raises() -> None:
    """done 之后再 step 应该抛 ValueError。

    用 with pytest.raises(ValueError): 包住那次调用。
    """
    env = SnakeEnv(grid_size = 12, seed = 12)
    env.steps = 99
    env.snake = [(6, 6)]
    env.food = (12, 12)
    env.direction = 1
    result = env.step(1)
    with pytest.raises(ValueError):
        result = env.step(1)
    

def test_same_seed_same_trajectory() -> None:
    """同一个 seed + 同一串动作 → 完全一样的轨迹（含食物位置）。
    
    提示：给两个 env 相同的 seed，喂同一串**固定**动作（别用 env._rng，
    测试不该依赖私有属性），然后用 == 比较它们的 StepResult。
    frozen dataclass 已经帮你实现了 ==。
    """
    actions = [1, 2, 3, 0, 2, 3, 0, 1, 3, 2]
    env_a = SnakeEnv(grid_size = 12, seed = 1)
    env_b = SnakeEnv(grid_size = 12, seed = 1)
    result_a = env_a.reset()
    result_b = env_b.reset()
    assert result_a == result_b, (
        "reset出错"
    )
    for action in actions:
        result_a = env_a.step(action)
        result_b = env_b.step(action)
        assert result_a == result_b, (
            f"action{action} 后出错，\n"
            f"result_a = {result_a}\n"
            f"result_b = {result_b}"
        )


def test_spawn_bonus_point() -> None:
    """
    确认bonus point确实实现了六的倍数的时候生成
    """
    env = SnakeEnv(grid_size = 12, seed = 1213)
    for i in range(1, 5):
        env.reset()
        env.scores = i * 6 - 1
        env.snake = [(3, 1), (3, 2), (3, 3), (3, 4), (3, 5), (3, 6), (3, 7), (3, 8)]
        env.direction = 2
        env.food = (3, 0)
        result = env.step(2)
        assert result.bonus[0] == 6, (f"bonus生成有问题， bonus point originally = {result.bonus[0]}, scores = {env.scores}")
        assert len(result.bonus[1]) == 2 and result.bonus[1] not in result.snake and result.bonus[1] != result.food, (
            f"bonus has problem, generated at {result.bonus}, food at {result.food}, snake should at (3,0) ~ (3, 8)"
        )


def test_eat_bonus_point() -> None:
    """
    verify bonus point has been correctly subtracted and eaten, and the coming generation
    """
    env = SnakeEnv(grid_size = 12, seed = 1231)
    result = env.reset()
    env.snake = [(3, 6)]
    env.food = (0, 0)
    env.bonus = [6, (3, 3)]
    env.scores = 2
    env.direction = 2
    result = env.return_status()
    for i in range(3):
        assert result.bonus[0] == 6 - i, (
            f"calculte wrong, snake at {result.snake}, bonus point = {result.bonus[0]}"
        )
        result = env.step(2)
    assert env.scores == 6, (
        f"scores wrong, scores = {env.scores}, snake = {result.snake}")
    assert result.bonus[0] == 0, (f"bonus生成有问题， bonus point originally = {result.bonus[0]}")
    assert len(result.bonus[1]) == 0, (
        f"bonus has problem, generated"
    )
