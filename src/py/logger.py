import time

def logging(logger, pos, state, action, timestep, reward, next_pos):
    x, y, z = pos[0], pos[1], pos[2]
    nx, ny, nz = next_pos[0], next_pos[1], next_pos[2]
    logger.append([state.id, state.no, action.input_key, timestep, reward, str((x, y, z))+'->'+str((nx, ny, nz))])
    return

def save_log(logger, id, goal_position, task_no):
    t = time.strftime('%Y%m%d_%H-%M-%S', time.localtime(time.time()))
    task_no = str(task_no)
    gx = int(goal_position[0])
    gz = int(goal_position[2])
    g_pos = f'x{gx}z{gz}'
    filename = 'env' + id + '_' + g_pos + '_' + t + '_' + str(task_no) + '.log'
    with open(f'logs/{filename}', 'w') as f:
        for log in logger:
            log_msg = f'coord:{log[4]}\n'
            log_msg += f'state:{log[0]}, action:{log[1]}, timestep:{log[2]}, reward:{log[3]}\n'
            log_msg += '=' * 50 + '\n'
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