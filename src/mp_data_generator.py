import sys
import pathlib

user_lib_path = str(pathlib.Path().absolute())
user_lib_path += '/py'

if user_lib_path not in sys.path:
    sys.path.insert(0, user_lib_path)
    print('path insert succeeded.')

from map_designer import *
from map_designer import MapDesigner as MD

md = MD('pkl/maps/')

import json

with open('json/state_ids.json', 'r') as f:
    state_ids = json.load(f)

with open('json/action_ids.json', 'r') as f:
    action_ids = json.load(f)
    
print(state_ids)
print(len(state_ids['field']))

num_states = 0
for state in state_ids.keys():
    if type(state_ids[state]) != int:
        num_states += len(state_ids[state])
    else:
        num_states += state_ids[state]
num_actions = len(action_ids)

print(num_states, num_actions)
#print(action_ids)

from environment import *
envs = []
print('goal positions')
for i in range(12):
    with open(f'pkl/data/my_env33_{i+1}.pkl', 'rb') as f:
        my_env = pickle.load(f)
        print(my_env.goal_position)
        envs.append(my_env)

for my_env in envs:
    my_env.reset(dataset_initialize=True)

#trajectories = my_env.make_scenarios(n=10)
def ms(env, n=5, threshold=-3):
    env.make_scenarios(n=n, threshold=threshold)
    return


# multi-processing
from multiprocessing import Pool
import multiprocessing as mp

if __name__ == '__main__':
    mp.set_start_method('spawn')
    with Pool(processes=12) as pool:
        pool.map(ms, envs)

