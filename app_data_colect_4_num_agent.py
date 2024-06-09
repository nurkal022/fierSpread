import numpy as np
import random
import threading
import pandas as pd
from queue import Queue

# Параметры симуляции
GRID_SIZE = 50  # Размер сетки
NUM_AGENTS_LIST = [5, 10, 15, 20]  # Количество агентов для каждой симуляции
FIRE_SPREAD_PROB = 0.3  # Базовая скорость распространения огня (0.0 - 1.0)
FIRE_LIFE = 5  # Продолжительность жизни огня в шагах
EXTINGUISH_AREA = 3  # Размер области тушения агентов (должен быть нечетным)
FPS = 10  # Количество кадров в секунду

# Факторы, влияющие на распространение пожара
WIND_DIRECTION = "N"  # Направление ветра: 'N', 'S', 'E', 'W'
WIND_STRENGTH = 0.5  # Влияние ветра на распространение огня (0.0 - 1.0)
RAIN_PROBABILITY = (
    0.1  # Вероятность дождя, замедляющего распространение огня (0.0 - 1.0)
)


def start_simulation(seed, num_agents, start_fire_pos, result_queue):
    random.seed(seed)
    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=int)
    fire_duration = np.zeros((GRID_SIZE, GRID_SIZE), dtype=int)

    agents = [
        (random.randint(0, GRID_SIZE - 1), random.choice([0, GRID_SIZE - 1]))
        for _ in range(num_agents)
    ]
    agent_moves = [0] * num_agents
    extinguished_by_agent = [0] * num_agents
    steps_to_extinguish = [[] for _ in range(num_agents)]

    total_burned_cells = 0
    extinguished_cells = 0
    total_steps_to_extinguish = 0
    total_steps = 0

    grid[start_fire_pos[1], start_fire_pos[0]] = 1
    fire_duration[start_fire_pos[1], start_fire_pos[0]] = 1

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
        nonlocal total_steps_to_extinguish
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
                agent_moves[i] += 1
                steps_to_extinguish[i].append(agent_moves[i])
                total_steps_to_extinguish += 1

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
                            extinguished_by_agent[i] += 1

    simulation_running = True

    while simulation_running:
        total_steps += 1
        grid = spread_fire()
        move_agents()

        if np.all((grid == 0) | (grid == 3)):
            simulation_running = False

    if total_burned_cells > 0:
        efficiency = extinguished_cells / total_burned_cells
    else:
        efficiency = 0

    if extinguished_cells > 0:
        avg_steps_to_extinguish = total_steps_to_extinguish / extinguished_cells
    else:
        avg_steps_to_extinguish = 0

    percent_extinguished = (
        (extinguished_cells / total_burned_cells) * 100 if total_burned_cells > 0 else 0
    )

    result = {
        "Number of Agents": num_agents,
        "Total burned cells": total_burned_cells,
        "Extinguished cells": extinguished_cells,
        "Efficiency": efficiency,
        "Average steps to extinguish": avg_steps_to_extinguish,
        "Percentage extinguished": percent_extinguished,
        "Total Steps": total_steps,
        "Agent Moves": sum(agent_moves),
    }

    result_queue.put(result)


def run_simulations(num_simulations, num_agents_list, num_runs):
    result_queue = Queue()
    threads = []

    for _ in range(num_runs):
        start_fire_pos = (
            random.randint(0, GRID_SIZE - 1),
            random.randint(0, GRID_SIZE - 1),
        )
        seeds = [random.randint(0, 1000000) for _ in range(num_simulations)]
        for i in range(num_simulations):
            t = threading.Thread(
                target=start_simulation,
                args=(seeds[i], num_agents_list[i], start_fire_pos, result_queue),
            )
            threads.append(t)

    for t in threads:
        t.start()

    for t in threads:
        t.join()

    results = []
    while not result_queue.empty():
        results.append(result_queue.get())

    return results


def save_results_to_excel(results):
    df = pd.DataFrame(results)
    df.to_excel("fire_simulation_results.xlsx", index=False)


def main():
    num_simulations = len(NUM_AGENTS_LIST)
    num_runs = 100  # Количество запусков симуляции
    results = run_simulations(num_simulations, NUM_AGENTS_LIST, num_runs)
    save_results_to_excel(results)
    print("Simulation results saved to fire_simulation_results.xlsx")


if __name__ == "__main__":
    main()
