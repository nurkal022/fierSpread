import pygame
import numpy as np
import random
import os

# Параметры симуляции
GRID_SIZE = 50  # Размер сетки
FIRE_SPREAD_PROB = 0.3  # Базовая скорость распространения огня (0.0 - 1.0)
FIRE_LIFE = 5  # Продолжительность жизни огня в шагах
SIMULATIONS = 50  # Количество симуляций
MAX_STEPS = 100  # Максимальное количество шагов в каждой симуляции

# Инициализация Pygame
pygame.init()
pygame.display.set_mode((1, 1))  # Минимальное окно


def spread_fire(grid, fire_duration):
    new_grid = grid.copy()
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            if grid[y, x] == 1:
                fire_duration[y, x] += 1
                if fire_duration[y, x] > FIRE_LIFE:
                    new_grid[y, x] = 3
                else:
                    spread_prob = FIRE_SPREAD_PROB
                    if random.random() < 0.1:
                        spread_prob *= 0.5

                    directions = [(y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)]
                    for dy, dx in directions:
                        if (
                            0 <= dy < GRID_SIZE
                            and 0 <= dx < GRID_SIZE
                            and grid[dy][dx] == 0
                        ):
                            if random.random() < spread_prob:
                                new_grid[dy][dx] = 1
    return new_grid


# Создание директории для данных
if not os.path.exists("fire_simulation_data"):
    os.makedirs("fire_simulation_data")

for sim in range(SIMULATIONS):
    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=int)
    fire_duration = np.zeros((GRID_SIZE, GRID_SIZE), dtype=int)

    # Начальная точка огня в центре
    grid[GRID_SIZE // 2, GRID_SIZE // 2] = 1

    for step in range(MAX_STEPS):
        current_grid = grid.copy()
        grid = spread_fire(grid, fire_duration)
        new_sources = (grid == 1) & (current_grid != 1)

        # Сохранение текущего шага
        np.save(
            f"fire_simulation_data/sim_{sim}_step_{step}_current.npy",
            current_grid.astype(int),
        )

        # Сохранение новых источников огня
        np.save(
            f"fire_simulation_data/sim_{sim}_step_{step}_new.npy",
            new_sources.astype(int),
        )

pygame.quit()
print("Симуляции завершены и данные сохранены.")
