import time
import os
from ds import Stack

def logging(logger:Stack, pos, state, action, timestep, reward, next_pos):
    x, y, z = pos[0], pos[1], pos[2]
    nx, ny, nz = next_pos[0], next_pos[1], next_pos[2]
    logger.push([state.id, state.no, action.input_key, timestep, reward, str((x, y, z))+'->'+str((nx, ny, nz))])
    return

def delogging(logger:Stack):
    logger.pop()
    return

def save_log(logger, id, goal_position):
    t = time.strftime('%Y%m%d_%H-%M-%S', time.localtime(time.time()))
    gx = int(goal_position[0])
    gz = int(goal_position[2])
    g_pos = f'x{gx}z{gz}'
    path = f'logs/env{id}_{g_pos}/'

    if not os.path.exists(path):
        os.makedirs(path)

    filename = path + f'{t}.log'
    with open(f'{filename}', 'w') as f:
        for log in logger.getTotal():
            log_msg = f'coord:{log[4]}\n'
            log_msg += f'state:{log[0]}, action:{log[1]}, timestep:{log[2]}, reward:{log[3]}\n'
            log_msg += '=' * 50 + '\n\n'
            f.write(log_msg)
    return

def print_log(logger, n=20):
    print('')
    print('logs>')
    len_log = len(logger)
    if len_log < 2*n:
        for l in logger:
            print(f'coord:"{l[4]}"')
            print(f'state:"{l[0]}", action:"{l[1]}", timestep:"{l[2]}", reward:"{l[3]}"')
    elif len_log >= 2*n:
        for l in logger[:20]:
            print(f'coord:"{l[4]}"')
            print(f'state:"{l[0]}", action:"{l[1]}", timestep:"{l[2]}", reward:"{l[3]}"')
        for l in logger[len_log-20:]:
            print(f'coord:"{l[4]}"')
            print(f'state:"{l[0]}", action:"{l[1]}", timestep:"{l[2]}", reward:"{l[3]}"')
    return