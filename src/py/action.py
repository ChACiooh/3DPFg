from numpy import dtype
from basic_math import *

base_stamina_consume = -4.8
base_acting_time = 1.3
angles = {'D':0., 'W':np.pi/2, 'A':np.pi, 'S':-np.pi/2,
         'WD':np.pi/4, 'WA':np.pi*3/4, 'SD':-np.pi/4, 'SA':-np.pi*3/4}

import json

with open('json/action_ids.json', 'r') as f:
    action_ids = json.load(f)
    
action_input_keys = {}
for item in action_ids.items():
    action_input_keys[item[1]] = item[0]


def change_direction(direction, input_key):
    # direction is numpy array vector
    if input_key == 'Wait' or input_key == 'j':
        return direction
    key = ''
    for k in input_key:
        if k in 'WASD':
            key += k
    return np.matmul(np.matmul(rotate_matrix(angles[key]), rotate_matrix(angle=0)), direction)
    

class Action:
    def __init__(self, action_id, velocity, acting_time=base_acting_time, stamina_consume=base_stamina_consume, input_key='Wait'):
        self.acting_time = acting_time
        self.id = action_id
        self.input_key = input_key
        self.velocity = np.copy(velocity) # numpy array vector
        self.stamina_consume = stamina_consume
       
    # agent_dir : unit vector which points the direction that agent is looking
    def action_update(self, action_id, input_key, stamina_consume, acting_time, agent_dir, velocity, given='None'):
        self.id = action_id
        self.input_key = input_key
        self.acting_time = acting_time
        self.stamina_consume = stamina_consume
        
        if given == 'wall':
            self.velocity = np.copy(velocity)
            return

        if input_key == 'Wait' or input_key == 'j':
            self.velocity = np.array([0., 0., 0.])
        else:
            self.velocity = 4 * change_direction(agent_dir, input_key)
        if given == 'parachute':
            self.velocity += np.array([0., -3., 0.])
            return
        elif 'j' in input_key:
            self.velocity += np.array([0., 3.822, 0.])

        if 's' in input_key:
            self.velocity[0] *= 6/4
            self.velocity[2] *= 6/4
        
    def Update(self, action):
        self.acting_time = action.acting_time
        self.id = action.id
        self.input_key = action.input_key
        self.velocity = np.copy(action.velocity)
        self.stamina_consume = action.stamina_consume
        
    def get_action_vector(self):
        return np.array([self.id, self.acting_time, self.velocity[0], self.velocity[1], self.velocity[2], self.stamina_consume], dtype=np.float32)
    


def cnv_vec2obj(emb_vec):
    id = round(emb_vec[0])
    acting_time = emb_vec[1]
    input_key = action_input_keys[id]
    velocity = np.array([emb_vec[2], emb_vec[3], emb_vec[4]])
    stamina_consume = emb_vec[5]
    
    #action_id, velocity, acting_time=base_acting_time, stamina_consume=base_stamina_consume, input_key='Wait'
    return Action(action_id=id, velocity=velocity, acting_time=acting_time, stamina_consume=stamina_consume, input_key=input_key)