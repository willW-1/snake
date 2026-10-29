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
    screen =  pygame.display.set_mode((CELL * (grid_size + 2), CELL * (grid_size + 4)))
    pygame.display.set_caption("Snake")
    return screen


def draw(screen, font, scores: int, obs: "StepResult", grid_size: int, cell: int = CELL) -> None:
    """把一帧画到 screen 上。"""
    #background
    pygame.draw.rect(screen, BG_COLOR, (0, 0, CELL * (grid_size + 2), CELL * (grid_size + 4)))

    #points
    header_w = (grid_size + 2) * CELL
    header_h = 3 * CELL
    score_surf = font.render(f"Score: {scores}", True, (255, 255, 255))
    w, h = score_surf.get_size()
    screen.blit(score_surf, ((header_w - w) // 2, (header_h - h) // 2))

    #snake body
    for snake in obs.snake:
        pygame.draw.rect(screen, BODY_COLOR, (CELL * (snake[1] + 1), CELL * (snake[0] + 3), CELL, CELL))
    
    #snake head
    pygame.draw.rect(screen, HEAD_COLOR, (CELL * (obs.snake[0][1] + 1), CELL * (obs.snake[0][0] + 3), CELL, CELL))

    #food
    pygame.draw.rect(screen, FOOD_COLOR, (CELL * (obs.food[1] + 1), CELL * (obs.food[0] + 3), CELL, CELL))

    #bonus
    bonus = obs.bonus
    if bonus[0] > 0:
        x = CELL * (bonus[1][1] + 1)
        y = CELL * (bonus[1][0] + 3)
        pygame.draw.rect(
            screen, (200 - 15 * bonus[0], 10, 200 - 15 * bonus[0]), (x, y, CELL, CELL))
        surf = font.render(str(bonus[0]), True, (0, 0, 0)) 
        w, h = surf.get_size()                                    
        screen.blit(surf, (x + (CELL - w) // 2, y + (CELL - h) // 2))                 

    #seperate line
    for x in range(CELL, CELL * (grid_size + 1), CELL):
        for y in range(CELL * 3, CELL * (grid_size + 3), CELL):
            pygame.draw.rect(screen, LINE_COLOR, (x, y, CELL, CELL), 1)    
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
    while running:
        for _ in range(1000):
            if obs.done:
                obs = env.reset()
            draw(screen=screen, font=font, scores=env.scores, obs=obs, grid_size=12, cell=CELL)
            obs = env.step(rng.randint(0, 3))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break
            if not running:
                break
            pygame.time.Clock().tick(3)
    pygame.quit()

'''

import pygame

pygame.init()
screen = pygame.display.set_mode((1024, 768))
clock = pygame.time.Clock()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    screen.fill((30, 30, 30))
    index = 0
    for _ in range(10):     
        pygame.draw.rect(screen, (220, 80, 80), (100, 40 + index, 40, 40))
        pygame.display.flip()
        index += 40
        clock.tick(5)

pygame.quit()
'''
