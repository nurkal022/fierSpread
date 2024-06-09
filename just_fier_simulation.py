import pygame
import numpy as np
import random

# Параметры симуляции
GRID_SIZE = 50  # Размер сетки
FIRE_SPREAD_PROB = 0.3  # Базовая скорость распространения огня (0.0 - 1.0)
FIRE_LIFE = 5  # Продолжительность жизни огня в шагах
FPS = 10  # Количество кадров в секунду

# Факторы, влияющие на распространение пожара
WIND_DIRECTION = "N"  # Направление ветра: 'N', 'S', 'E', 'W'
WIND_STRENGTH = 0.1  # Влияние ветра на распространение огня (0.0 - 1.0)
RAIN_PROBABILITY = (
    0.8  # Вероятность дождя, замедляющего распространение огня (0.0 - 1.0)
)

# Цвета
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREY = (200, 200, 200)

# Инициализация Pygame
pygame.init()


def draw_text(screen, text, position, font, color=BLACK):
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, position)


def start_simulation():
    CELL_SIZE = 10
    screen = pygame.display.set_mode(
        (GRID_SIZE * CELL_SIZE, GRID_SIZE * CELL_SIZE + 50)
    )
    pygame.display.set_caption("Fire Simulation")

    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=int)
    fire_duration = np.zeros((GRID_SIZE, GRID_SIZE), dtype=int)

    total_burned_cells = 0

    def draw_grid():
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                color = (
                    GREEN
                    if grid[y, x] == 0
                    else RED if grid[y, x] == 1 else BLUE if grid[y, x] == 2 else BLACK
                )
                pygame.draw.rect(
                    screen,
                    color,
                    pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE),
                )

    def spread_fire():
        nonlocal total_burned_cells
        new_grid = grid.copy()
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                if grid[y, x] == 1:
                    fire_duration[y, x] += 1
                    if fire_duration[y, x] > FIRE_LIFE:
                        new_grid[y, x] = 3
                    else:
                        spread_prob = FIRE_SPREAD_PROB
                        if random.random() < RAIN_PROBABILITY:
                            spread_prob *= 0.5

                        directions = [(y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)]
                        wind_effects = {
                            "N": (y + 1, x),
                            "S": (y - 1, x),
                            "E": (y, x - 1),
                            "W": (y, x + 1),
                        }
                        wind_y, wind_x = wind_effects[WIND_DIRECTION]

                        for dy, dx in directions:
                            if (
                                0 <= dy < GRID_SIZE
                                and 0 <= dx < GRID_SIZE
                                and grid[dy][dx] == 0
                            ):
                                if (dy, dx) == (wind_y, wind_x):
                                    if random.random() < spread_prob + WIND_STRENGTH:
                                        new_grid[dy][dx] = 1
                                        total_burned_cells += 1
                                else:
                                    if random.random() < spread_prob:
                                        new_grid[dy][dx] = 1
                                        total_burned_cells += 1

        return new_grid

    simulation_running = False
    running = True
    clock = pygame.time.Clock()

    button_rect = pygame.Rect(
        (GRID_SIZE * CELL_SIZE // 2 - 50, GRID_SIZE * CELL_SIZE + 10, 100, 30)
    )

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos):
                    simulation_running = not simulation_running
                else:
                    mouse_x, mouse_y = event.pos
                    grid_x, grid_y = mouse_x // CELL_SIZE, mouse_y // CELL_SIZE
                    if 0 <= grid_x < GRID_SIZE and 0 <= grid_y < GRID_SIZE:
                        grid[grid_y][grid_x] = 1
                        fire_duration[grid_y][grid_x] = 1

        if simulation_running:
            grid = spread_fire()

        screen.fill(WHITE)
        draw_grid()

        pygame.draw.rect(screen, GREY, button_rect)
        button_text = "Start" if not simulation_running else "Stop"
        font = pygame.font.Font(None, 30)
        text_surface = font.render(button_text, True, BLACK)
        screen.blit(text_surface, (button_rect.x + 10, button_rect.y + 5))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


start_simulation()
