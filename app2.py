import pygame
import numpy as np
import os
import tensorflow as tf

# Параметры
GRID_SIZE = 50
CELL_SIZE = 10
SIMULATIONS = 50
MAX_STEPS = 100

# Цвета
COLORS = {
    0: (255, 255, 255),  # Негорящая область
    1: (255, 0, 0),  # Огонь
    3: (0, 0, 0),
}  # Сгоревшая область

# Инициализация Pygame
pygame.init()
screen = pygame.display.set_mode((GRID_SIZE * CELL_SIZE * 2, GRID_SIZE * CELL_SIZE))
pygame.display.set_caption("Fire Simulation with Predictions")

# Загрузка модели
model = tf.keras.models.load_model("fire_spread_predictor.h5")
print("Модель загружена.")


# Функция для предсказания следующего шага
def predict_next_step(current_grid):
    current_grid = current_grid.reshape(1, GRID_SIZE, GRID_SIZE, 1)
    prediction = model.predict(current_grid)
    next_grid = prediction.reshape(GRID_SIZE, GRID_SIZE, 4).argmax(
        axis=-1
    )  # Преобразование обратно в 2D
    return next_grid


# Функция для отрисовки сетки
def draw_grid(grid, offset_x=0):
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            color = COLORS.get(
                grid[y, x], (0, 0, 255)
            )  # Синий цвет для неопределенных значений
            pygame.draw.rect(
                screen,
                color,
                (x * CELL_SIZE + offset_x, y * CELL_SIZE, CELL_SIZE, CELL_SIZE),
            )


# Переменные для навигации
current_sim = 0
current_step = 0
running = True
clock = pygame.time.Clock()


# Загрузка данных симуляции
def load_simulation_data(sim, step):
    file_path = f"fire_simulation_data/sim_{sim}_step_{step}.npy"
    if os.path.exists(file_path):
        return np.load(file_path)
    return None


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                current_step = max(0, current_step - 1)
            elif event.key == pygame.K_RIGHT:
                current_step = min(MAX_STEPS - 1, current_step + 1)
            elif event.key == pygame.K_UP:
                current_sim = max(0, current_sim - 1)
            elif event.key == pygame.K_DOWN:
                current_sim = min(SIMULATIONS - 1, current_sim + 1)

    # Загрузка и отображение данных
    current_grid = load_simulation_data(current_sim, current_step)
    if current_grid is not None:
        predicted_grid = predict_next_step(current_grid)
        screen.fill((200, 200, 200))
        draw_grid(current_grid, offset_x=0)
        draw_grid(predicted_grid, offset_x=GRID_SIZE * CELL_SIZE)
        pygame.display.set_caption(f"Simulation {current_sim}, Step {current_step}")
        pygame.display.flip()

    clock.tick(5)  # Ограничение частоты обновления экрана для лучшей восприимчивости

pygame.quit()
