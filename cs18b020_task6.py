# import modules
import pygame
from pygame.locals import *
import numpy as np
import random
import json


pygame.init()

screen_height = 300
screen_width = 300
line_width = 6
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Tic Tac Toe')


# define colours
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)

# define font
font = pygame.font.SysFont(None, 40)


# setup a rectangle for "Play Again" Option
again_rect = Rect(screen_width // 2 - 80, screen_height // 2, 160, 50)

# define variables
clicked = False
player = 1
pos = (0, 0)
markers = np.zeros((3, 3), int)
game_over = False
winner = 0

transition_func = np.zeros((3139, 9, 3139), dtype=float)
states = np.zeros((3139), int)
states_ptr = 0


def draw_board():
    bg = (255, 255, 210)
    grid = (50, 50, 50)
    screen.fill(bg)
    for x in range(1, 3):
        pygame.draw.line(screen, grid, (0, 100 * x),
                         (screen_width, 100 * x), line_width)
        pygame.draw.line(screen, grid, (100 * x, 0),
                         (100 * x, screen_height), line_width)


def draw_markers():
    x_pos = 0
    for x in markers:
        y_pos = 0
        for y in x:
            if y == 1:
                pygame.draw.line(screen, red, (x_pos * 100 + 15, y_pos * 100 + 15),
                                 (x_pos * 100 + 85, y_pos * 100 + 85), line_width)
                pygame.draw.line(screen, red, (x_pos * 100 + 85, y_pos * 100 + 15),
                                 (x_pos * 100 + 15, y_pos * 100 + 85), line_width)
            if y == -1:
                pygame.draw.circle(
                    screen, green, (x_pos * 100 + 50, y_pos * 100 + 50), 38, line_width)
            y_pos += 1
        x_pos += 1


def find_winner(state):
    # 0 - nothing; 1-X ; 2-O ; 3-tie
    markers = dec_to_mat(state)
    markers[markers == 2] = -1
    winner = 0
    game_over = False

    def checker():
        x_pos = 0
        nonlocal winner
        for x in markers:
            # check columns
            if np.sum(x) == -3:
                winner = 2
                game_over = True
            if np.sum(x) == 3:
                winner = 1
                game_over = True
            # check rows
            if markers[0][x_pos] + markers[1][x_pos] + markers[2][x_pos] == -3:
                winner = 2
                game_over = True
            if markers[0][x_pos] + markers[1][x_pos] + markers[2][x_pos] == 3:
                winner = 1
                game_over = True
            x_pos += 1

        # check cross
        if markers[0][0] + markers[1][1] + markers[2][2] == -3 or markers[2][0] + markers[1][1] + markers[0][2] == -3:
            winner = 2
            game_over = True
        if markers[0][0] + markers[1][1] + markers[2][2] == 3 or markers[2][0] + markers[1][1] + markers[0][2] == 3:
            winner = 1
            game_over = True
    checker()
    no_zeros = 0
    # check for tie
    if game_over == False:
        for row in markers:
            for i in row:
                if i == 0:
                    no_zeros += 1
        # if it is a tie, then call game over and set winner to 0 (no one)
        if no_zeros == 1:
            markers[markers == 0] = 1
            winner = 3
            checker()
    return winner

# '222212212's matrix to 19598 . Returns index of matrix
# States is an array of these values


def mat_to_dec(matrix):
    s = ""
    for i in range(3):
        for j in range(3):
            s += str(matrix[i][j])
    return int(s, 3)

# Converts index to a matrix. 19598 returns '222212212's matrix


def dec_to_mat(index):
    s = np.base_repr(index, 3)
    s = s.zfill(9)
    mat = np.zeros((3, 3), int)
    x = 0
    for i in range(3):
        for j in range(3):
            mat[i][j] = s[x]
            x = x + 1
    return mat

# Converts a decimal to the position in matrix. eg. 3 to (1,0)


def dec_to_pos(dec):
    s = np.base_repr(dec, 3)
    s = s.zfill(2)
    x = int(s[0])
    y = int(s[1])
    return (x, y)


def pos_to_dec(pos):
    s = ""
    s += str(pos[0])
    s += str(pos[1])
    return int(s, 3)


def find_zero_pos(mat):
    zero_pos = []
    for i in range(3):
        for j in range(3):
            if mat[i][j] == 0:
                zero_pos.append((i, j))
    return zero_pos


def add_two_marks(mat):
    global states
    global states_ptr
    zero_pos = find_zero_pos(mat)
    for i in zero_pos:
        mat[i] = 1
        for j in zero_pos:
            if i != j:
                mat[j] = 2
                dec = mat_to_dec(mat)
                if dec in states:
                    pass
                else:
                    states[states_ptr] = dec
                    states_ptr += 1
                mat[j] = 0
        mat[i] = 0


def generate_states_internal(start_index, end_index):
    global states
    for i in range(start_index, end_index):
        mat = dec_to_mat(states[i])
        add_two_marks(mat)


def generate_states():
    global states
    global states_ptr
    states[states_ptr] = 0
    states_ptr += 1
    start_index = 1
    mat = dec_to_mat(0)
    # Added first 'X'and 'O'
    add_two_marks(mat)
    end_index = states_ptr
    # Add second markers
    generate_states_internal(start_index, end_index)
    start_index = end_index
    end_index = states_ptr
    # Add third markers
    generate_states_internal(start_index, end_index)
    start_index = end_index
    end_index = states_ptr
    # Add fourth markers
    generate_states_internal(start_index, end_index)
    end_index = states_ptr


def check_is_terminal_state(state):
    if states_type[state] == 0:
        return False
    else:
        return True


def generate_transition_func():
    global states
    total_states = len(states)
    for i in range(total_states):
        if check_is_terminal_state(states[i]):
            # DO STUFF
            for p in range(0, 9):
                transition_func[i][p][0] = 1
            continue
        mat = dec_to_mat(states[i])

        zero_pos = find_zero_pos(mat)
        for j in zero_pos:
            no_of_zeros = len(zero_pos)
            if(no_of_zeros <= 1):
                continue
            mat[j] = 1
            pdf = np.random.choice(range(1, 1 + no_of_zeros), no_of_zeros - 1)
            pdf = list(pdf/pdf.sum())
            for k in zero_pos:
                if k != j:
                    mat[k] = 2
                    next_state_dec = mat_to_dec(mat)
                    next_state_index = np.where(states == next_state_dec)[0]
                    transition_func[i][pos_to_dec(
                        j)][next_state_index] = pdf.pop()
                    mat[k] = 0
            mat[j] = 0


policy = np.zeros((3139), int)
Q_Table = np.zeros((3139, 9), dtype=float)


def build_QTable():
    no_iterations = 5000000
    alpha = 0.1
    gamma = 0.1
    epsilon = 0.1
    curr_state_index = 0
    i = 0
    while i < no_iterations:
        if i % 100 == 0:
            print("PROGRESS-", i)
        i += 1

        p = np.random.random()

        mat = dec_to_mat(states[curr_state_index])
        zero_pos = find_zero_pos(mat)
        action_index = np.random.randint(len(zero_pos))
        action_pos = zero_pos[action_index]
        action_random = pos_to_dec(action_pos)

        max_val = float('-inf')
        max_pos = 0
        for j in range(9):
            if Q_Table[curr_state_index][j] > max_val:
                max_val = Q_Table[curr_state_index][j]
                max_pos = j
        action_QTable = max_pos

        if p < epsilon:
            action = action_random
        else:
            # Check if the action is valid
            action = action_QTable
            pos = dec_to_pos(action)
            if pos not in zero_pos:
                action = action_random

        p = transition_func[curr_state_index][action]

        next_state_index = np.random.choice(
            range(3139), 1, p=p)[0]
        next_state = states[next_state_index]
        reward = get_reward(next_state)
        max_Q = float('-inf')
        for j in range(9):
            if Q_Table[next_state_index][j] > max_Q:
                max_Q = Q_Table[next_state_index][j]

        Q_Table[curr_state_index][action] = Q_Table[curr_state_index][action] + \
            alpha * (reward + gamma*max_Q - Q_Table[curr_state_index][action])
        curr_state_index = next_state_index
    with open('sarsa_table.json', 'w') as f:
        json.dump(Q_Table.tolist(), f)


def build_policy():
    global policy

    for i in range(3139):
        max_val = float('-inf')
        max_pos = 0
        for j in range(9):
            if Q_Table[i][j] > max_val:
                max_val = Q_Table[i][j]
                max_pos = j
        policy[i] = max_pos
    policy_list = policy.tolist()
    with open('sarsa_policy.json', 'w') as f:
        json.dump(policy_list, f)


states_type = {}


def get_reward(state):
    if states_type[state] == 3:
        return 10
    elif states_type[state] == 2:
        # LOSE
        return -100
    elif states_type[state] == 1:
        # WIN
        return 100
    else:
        # NONE
        return 0


def build_states_type():
    for state in states:
        states_type[state] = find_winner(state)


generate_states()


build_states_type()

generate_transition_func()

try:
    with open('sarsa_table.json') as f:
        data = f.read()
        f.close()
    Q_Table = json.loads(data)
except:
    build_QTable()


try:
    with open('sarsa_policy.json') as f:
        data = f.read()
        f.close()
    policy = json.loads(data)
except:
    build_policy()

# main loop
run = True
wins = 0
losses = 0
ties = 0
total = 0
while total < 1000:
    # draw board and markers first
    draw_board()
    draw_markers()

    markers[markers == -1] = 2
    current_state = mat_to_dec(markers)
    current_state_index = np.where(
        states == current_state)[0][0]
    policy_pos = policy[current_state_index]
    policy_x, policy_y = dec_to_pos(policy_pos)
    markers[policy_x][policy_y] = 1

    markers[markers == 2] = -1

    action_taken = pos_to_dec((policy_x, policy_y))
    p = transition_func[current_state_index][action_taken]

    next_state_index = np.random.choice(
        range(3139), 1, p=p)[0]
    next_state = states[next_state_index]
    markers = dec_to_mat(next_state)
    markers[markers == 2] = -1

    # print(markers)
    rew = get_reward(next_state)
    if rew == 100:
        wins += 1
        total += 1
    elif rew == -100:
        losses += 1
        total += 1
    elif rew == 10:
        ties += 1
        total += 1
    # update display
    pygame.display.update()
print("TOTAL - ", total)
print("WINS", wins)
print("LOSSES", losses)
print("TIES", ties)
print("Win Ratio", float(wins/total))
pygame.quit()
