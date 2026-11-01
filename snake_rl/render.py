"""把游戏画面画到电脑屏幕上"""


from typing import TYPE_CHECKING
import pygame

if TYPE_CHECKING:
    from snake_rl.env import StepResult

CELL = 50
BG_COLOR = (20, 20, 150)
LINE_COLOR = (0, 0, 0)
FOOD_COLOR = (255, 103, 204)
BODY_COLOR = (255, 255, 0)
HEAD_COLOR = (204, 102, 0)
NUMBER_SIZE = 40


def make_screen(grid_size: int, cell: int = CELL) -> pygame.Surface:
    """记得最后 pygame.quit()。
    上方留3CELL的空位写分数，其他三边留1CELL
    """
    pygame.init()
    screen = pygame.display.set_mode((cell * (grid_size + 2), cell * (grid_size + 4)))
    pygame.display.set_caption("Snake")
    return screen


def draw(screen, font, scores: int, obs: "StepResult", grid_size: int, cell: int = CELL) -> None:
    """把一帧画到 screen 上。"""
    #background
    pygame.draw.rect(screen, BG_COLOR, (0, 0, cell * (grid_size + 2), cell * (grid_size + 4)))

    #points
    header_w = (grid_size + 2) * cell
    header_h = 3 * cell
    score_surf = font.render(f"Score: {scores}", True, (255, 255, 255))
    w, h = score_surf.get_size()
    screen.blit(score_surf, ((header_w - w) // 2, (header_h - h) // 2))

    #snake body
    for snake in obs.snake:
        pygame.draw.rect(screen, BODY_COLOR, (cell * (snake[1] + 1), cell * (snake[0] + 3), cell, cell))
    
    #snake head
    pygame.draw.rect(screen, HEAD_COLOR, (cell * (obs.snake[0][1] + 1), cell * (obs.snake[0][0] + 3), cell, cell))

    #food
    pygame.draw.rect(screen, FOOD_COLOR, (cell * (obs.food[1] + 1), cell * (obs.food[0] + 3), cell, cell))

    #bonus
    bonus = obs.bonus
    if bonus[0] > 0:
        x = cell * (bonus[1][1] + 1)
        y = cell * (bonus[1][0] + 3)
        pygame.draw.rect(
            screen, (200 - 15 * bonus[0], 10, 200 - 15 * bonus[0]), (x, y, cell, cell))
        surf = font.render(str(bonus[0]), True, (0, 0, 0)) 
        w, h = surf.get_size()                                    
        screen.blit(surf, (x + (cell - w) // 2, y + (cell - h) // 2))                 

    #seperate line
    for x in range(cell, cell * (grid_size + 1), cell):
        for y in range(cell * 3, cell * (grid_size + 3), cell):
            pygame.draw.rect(screen, LINE_COLOR, (x, y, cell, cell), 1)    
    pygame.display.flip()


if __name__ == "__main__":
    from snake_rl.env import SnakeEnv
    import random

    screen = make_screen(grid_size=12, cell=CELL)
    font = pygame.font.Font(None, NUMBER_SIZE)
    running = True
    env = SnakeEnv()
    obs = env.reset()
    env.bonus = [6, (0, 0)]
    rng = random.Random(1)
    clock = pygame.time.Clock()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        if obs.done:
            obs = env.reset()
            env.bonus = [6, (0, 0)]
        draw(screen=screen, font=font, scores=env.scores, obs=obs, grid_size=12, cell=CELL)
        obs = env.step(rng.randint(0, 3))
        clock.tick(3)
    pygame.quit()

