import numpy as np
import visualkeras

import os
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import (
    Conv2D,
    MaxPooling2D,
    Flatten,
    Dense,
    Reshape,
    Dropout,
)

# Параметры
GRID_SIZE = 50
SIMULATIONS = 50
MAX_STEPS = 100

# Конфигурация модели
input_shape = (GRID_SIZE, GRID_SIZE, 1)  # Ожидаемые размеры входных данных
num_classes = 2  # Количество возможных классов состояний клетки (0 и 1)

# Создание модели
model = Sequential(
    [
        Conv2D(
            64,
            kernel_size=(3, 3),
            activation="relu",
            input_shape=input_shape,
            padding="same",
        ),
        MaxPooling2D(pool_size=(2, 2)),
        Dropout(0.25),
        Conv2D(128, (3, 3), activation="relu", padding="same"),
        MaxPooling2D(pool_size=(2, 2)),
        Dropout(0.25),
        Flatten(),
        Dense(256, activation="relu"),
        Dropout(0.5),
        Dense(GRID_SIZE * GRID_SIZE * num_classes, activation="softmax"),
        Reshape((GRID_SIZE, GRID_SIZE, num_classes)),
    ]
)
model.summary()

visualkeras.layered_view(model).show()  # display using your system viewer
visualkeras.layered_view(model, to_file="output.png")  # write to disk
visualkeras.layered_view(model, to_file="output.png").show()  # write and show
model.compile(
    optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"]
)


# Подготовка данных для обучения
def load_data():
    X = []
    Y = []
    for sim in range(SIMULATIONS):
        for step in range(MAX_STEPS - 1):
            current_grid = np.load(
                f"fire_simulation_data/sim_{sim}_step_{step}_current.npy"
            )
            new_sources = np.load(f"fire_simulation_data/sim_{sim}_step_{step}_new.npy")
            X.append(current_grid)
            Y.append(new_sources)

    X = np.array(X).reshape((-1, GRID_SIZE, GRID_SIZE, 1))  # Добавляем канал
    Y = np.array(Y).reshape(
        (-1, GRID_SIZE, GRID_SIZE)
    )  # Преобразуем в 3D для соответствия меткам
    return X, Y


X, Y = load_data()

# Разделение данных на обучающую и тестовую выборки
from sklearn.model_selection import train_test_split

X_train, X_test, Y_train, Y_test = train_test_split(
    X, Y, test_size=0.2, random_state=42
)

# Обучение модели
model.fit(X_train, Y_train, epochs=3, validation_data=(X_test, Y_test), batch_size=32)

# Сохранение модели
model.save("fire_spread_predictor.h5")
print("Модель сохранена.")
