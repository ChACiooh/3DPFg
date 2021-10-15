from matplotlib.pyplot import xcorr
from basic_math import *

base_stamina_consume = -4.8
base_acting_time = 1.3
angles = {'D':0., 'W':np.pi/2, 'A':np.pi, 'S':-np.pi/2,
         'WD':np.pi/4, 'WA':np.pi*3/4, 'SD':-np.pi/4, 'SA':-np.pi*3/4}



def change_direction(direction, input_key):
    # direction is numpy array vector
    if input_key == 'None':
        return direction
    key = ''
    for k in input_key:
        if k in 'WASD':
            key += k
    return np.matmul(np.matmul(rotate_matrix(angles[key]), rotate_matrix(angle=0)), direction)
    

class Action:
    def __init__(self, action_id, velocity, acting_time=base_acting_time, stamina_consume=base_stamina_consume, input_key='None'):
        self.acting_time = acting_time
        self.action_id = action_id
        self.input_key = input_key
        self.velocity = np.copy(velocity) # numpy array vector
        self.stamina_consume = stamina_consume

        
    # agent_dir : unit vector which points the direction that agent is looking
    def action_update(self, action_id, input_key, stamina_consume, acting_time, agent_dir):
        self.action_id = action_id
        self.input_key = input_key
        self.acting_time = acting_time
        self.stamina_consume = stamina_consume
        
        if self.action_id == 'Wait':
            self.velocity = np.array([0., 0., 0.])
            self.acting_time = self.base_acting_time
            
        
        self.velocity = 4 * change_direction(agent_dir, input_key)  
        if 'j' in input_key:
            self.velocity += np.array([0., 3.822, 0.])

        if 's' in input_key:
            self.velocity[0] *= 6/4
            self.velocity[2] *= 6/4
        

    def Update(self, action):
        self.acting_time = action.acting_time
        self.action_id = action.action_id
        self.input_key = action.input_key
        self.velocity = np.copy(action.velocity)
        self.stamina_consume = action.stamina_consume
        