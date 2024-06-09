import pygame
import numpy as np
import random

# Параметры симуляции
GRID_SIZE = 50  # Размер сетки
NUM_AGENTS = 5  # Количество агентов
FIRE_SPREAD_PROB = 0.3  # Базовая скорость распространения огня (0.0 - 1.0)
FIRE_LIFE = 5  # Продолжительность ж0изни огня в шагах
EXTINGUISH_AREA = 3  # Размер области тушения агентов (должен быть нечетным)
FPS = 10  # Количество кадров в секунду

# Факторы, влияющие на распространение пожара
WIND_DIRECTION = "N"  # Направление ветра: 'N', 'S', 'E', 'W'
WIND_STRENGTH = 0.5  # Влияние ветра на распространение огня (0.0 - 1.0)
RAIN_PROBABILITY = (
    0.1  # Вероятность дождя, замедляющего распространение огня (0.0 - 1.0)
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

    agents = [
        (random.randint(0, GRID_SIZE - 1), random.choice([0, GRID_SIZE - 1]))
        for _ in range(NUM_AGENTS)
    ]

    total_burned_cells = 0
    extinguished_cells = 0
    adding_fire = True

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
        for agent in agents:
            pygame.draw.circle(
                screen,
                BLUE,
                (
                    agent[0] * CELL_SIZE + CELL_SIZE // 2,
                    agent[1] * CELL_SIZE + CELL_SIZE // 2,
                ),
                CELL_SIZE // 2,
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

    def move_agents():
        nonlocal extinguished_cells
        for i, (x, y) in enumerate(agents):
            distances = {
                ((x2 - x) ** 2 + (y2 - y) ** 2): (x2, y2)
                for y2, row in enumerate(grid)
                for x2, val in enumerate(row)
                if val == 1
            }
            if distances:
                target_x, target_y = distances[min(distances)]
                agents[i] = (
                    max(0, min(GRID_SIZE - 1, x + (1 if target_x > x else -1))),
                    max(0, min(GRID_SIZE - 1, y + (1 if target_y > y else -1))),
                )

                for dy in range(-(EXTINGUISH_AREA // 2), (EXTINGUISH_AREA // 2) + 1):
                    for dx in range(
                        -(EXTINGUISH_AREA // 2), (EXTINGUISH_AREA // 2) + 1
                    ):
                        if (
                            0 <= y + dy < GRID_SIZE
                            and 0 <= x + dx < GRID_SIZE
                            and grid[y + dy][x + dx] == 1
                        ):
                            grid[y + dy][x + dx] = 3
                            extinguished_cells += 1

                print(f"Agent {i} moved to {(target_x, target_y)}")

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
                    adding_fire = False
                else:
                    if adding_fire:
                        mouse_x, mouse_y = event.pos
                        grid_x, grid_y = mouse_x // CELL_SIZE, mouse_y // CELL_SIZE
                        if 0 <= grid_x < GRID_SIZE and 0 <= grid_y < GRID_SIZE:
                            grid[grid_y][grid_x] = 1
                            fire_duration[grid_y][grid_x] = 1

        if simulation_running:
            grid = spread_fire()
            move_agents()

        screen.fill(WHITE)
        draw_grid()

        pygame.draw.rect(screen, GREY, button_rect)
        button_text = "Start" if not simulation_running else "Stop"
        font = pygame.font.Font(None, 30)
        text_surface = font.render(button_text, True, BLACK)
        screen.blit(text_surface, (button_rect.x + 10, button_rect.y + 5))

        pygame.display.flip()
        clock.tick(FPS)

    if total_burned_cells > 0:
        efficiency = extinguished_cells / total_burned_cells
    else:
        efficiency = 0

    print(f"Total burned cells: {total_burned_cells}")
    print(f"Extinguished cells: {extinguished_cells}")
    print(f"Agents' efficiency: {efficiency:.2f}")

    pygame.quit()


start_simulation()
