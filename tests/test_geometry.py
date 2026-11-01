from snake_rl.env import SnakeEnv
from snake_rl import geometry
import pytest

def test_next_pos() -> None:
    board = geometry.Board(grid_size=12, wrap=False)
    assert board.next_pos(pos=(0, 0), action=0) == (-1, 0), (
    f"wrong plain, pos={board.next_pos(pos=(0, 0), action=0)}")
    board = geometry.Board(grid_size=12, wrap=True)
    assert board.next_pos(pos=(0, 0), action=0) == (11, 0), (
    f"wrong plain, pos={board.next_pos(pos=(0, 0), action=0)}")

def test_correctly_wrap() -> None:
    env = SnakeEnv(grid_size=12, seed=1, wrap=True)
    env.snake = [(5, 5)]
    env.food = (0, 0)
    for _ in range(12):
        obs = env.step(3)
        assert obs.event != "hit_wall", f"wrong wrap event, event = {obs.event}"
    assert obs.snake[0] == (5, 5), f"wrong snake pos, pos = {obs.snake[0]}"
    env = SnakeEnv(grid_size=12, seed=1, wrap=False)
    env.snake = [(0, 11)]
    obs = env.step(3)
    assert obs.event == "hit_wall", f"wrong plain event, event = {obs.event}"
    
def test_correct_death_reason() -> None:
    env = SnakeEnv(grid_size=3, seed=1, wrap=True)
    env.snake = [(2, 2), (2, 1), (2, 0), (1, 0), (0, 0)]
    obs = env.step(3)
    assert obs.event == "hit_self", f"wrong event, event = {obs.event}"

def test_correct_signed_delta() -> None:
    board = geometry.Board(grid_size=12, wrap=True)
    assert abs(board.signed_delta(0, 11) - (-1/6)) < 1e-6

def test_dist_and_signed_delta_right_value() -> None:
    board = geometry.Board(grid_size=12, wrap=True)
    for r1 in range(12):
        for c1 in range(12):
            for r2 in range(12):
                for c2 in range(12):
                    assert 0 <= board.dist((r1, c1), (r2, c2)) <= 1, (
                    f"wrong dist, {r1}, {r2}, {c1}, {c2}, {board.dist((r1, c1), (r2, c2))}")
                    assert -1 <= board.signed_delta(r1, r2) <= 1, (
                    f"wrong delta, {r1}, {r2}, {board.signed_delta(r1, r2)}")

def test_hit_self() -> None:
    board = geometry.Board(grid_size=1, wrap=True)
    assert all(geometry.death_reason(snake=[(0, 0), (0, -1)], action=i, board=board) == "hit_self" for i in range(4)), (
        f"wrong event"
    ) 
