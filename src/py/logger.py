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

def gen_log_msg(log:list):
    log_msg = f'coord:{log[5]}\n'
    log_msg += f'state:{log[0]}-{log[1]}, action:{log[2]}, timestep:{log[3]}, reward:{log[4]}\n'
    log_msg += '=' * 50 + '\n\n'
    return log_msg

def save_log(logger:Stack, id, goal_position, state_id, cnt):
    t = time.strftime('%Y%m%d_%H-%M-%S', time.localtime(time.time()))
    gx = int(goal_position[0])
    gz = int(goal_position[2])
    g_pos = f'x{gx}z{gz}'
    path = f'logs/env{id}_gpos{g_pos}/'

    if not os.path.exists(path):
        os.makedirs(path)

    filename = path + f'{state_id}{cnt}_{t}.log'
    with open(f'{filename}', 'w') as f:
        for log in logger.getTotal():
            log_msg = gen_log_msg(log)
            f.write(log_msg)
    return

def print_log(logger:Stack, n=20):
    print('')
    print('logs>')
    len_log = len(logger)
    if len_log < 2*n:
        for log in logger.getTotal():
            log_msg = gen_log_msg(log)
            print(log_msg)
    elif len_log >= 2*n:
        for log in logger.getTotal(n):
            log_msg = gen_log_msg(log)
            print(log_msg)
        print('\n\n')
        print('A Few Moments Later...')
        print('\n\n')
        for log in logger.getTotal(-n):
            log_msg = gen_log_msg(log)
            print(log_msg)
    return