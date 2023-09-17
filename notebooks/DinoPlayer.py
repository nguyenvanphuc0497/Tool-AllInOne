
import trex_nn
from SeleniumHelper import GameDino
import numpy as np
import time


clever_params = {
    'b2': np.array([[0.27304736]]),
    'W2': np.array([[0.91572382, -0.29862268,  0.30955728]]),
    'W1': np.array([[-0.02062025,  0.00016742,  0.00381535],
                    [0.00226537,  0.01325698,  0.02389935],
                    [0.02300561,  0.01351209,  0.00588823]]),
    'b1': np.array([[-0.73119972],
                    [-0.05157346],
                    [-0.00290758]])
}


GAMEOVER_BOX = {'Y_GAMEOVER': 30, 'X_GAMEOVER': 115,
                'W_GAMEOVER': 200, 'H_GAMEOVER': 15}
GAMEOVER_RANGE = [630000, 670000]
TIME_BETWEEN_FRAMES = 0.01
TIME_BETWEEN_GAMES = 0.5

MAX_SPEED_STEP = 15
INIT_SPEED = 270
N_X = 3  # kich thuoc input layer
N_H = 3  # kich thuoc Hidden layer
N_Y = 1  # kich thuoc output layer
LANDSCAPE = False


dinoHelper = GameDino()
dinoHelper.init_bot()


def play_game():

    while True:
        time.sleep(0.1)
        speed = dinoHelper.get_current_speed()
        distance, size = dinoHelper.get_distance_obstacles(), dinoHelper.get_size_of_obstacle()
        input_set = [distance, speed, size]
        if None not in input_set:
            trex_nn.wrap_model(input_set, clever_params, N_X)
        print(input_set)


play_game()
