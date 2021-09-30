import numpy as np

base_stamina_consume = -4.8
base_acting_time = 1.3
angles = {'D':0., 'W':np.pi/2, 'A':np.pi, 'S':-np.pi/2,
         'WD':np.pi/4, 'WA':np.pi*3/4, 'SD':-np.pi/4, 'SA':-np.pi*3/4}

def rotate_matrix(angle):
    return np.array([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]])

def change_direction(direction, input_key):
    # direction is numpy array vector
    return rotate_matrix(angles[input_key]) * rotate_matrix(angle=0) * direction
    

class Action:
    def __init__(self, action_id, velocity, acting_time=1.3, stamina_consume=-4.8, input_key=None):
        self.acting_time = acting_time
        self.action_id = action_id
        self.input_key = input_key
        self.velocity = velocity # numpy array vector
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
            return agent_dir
        
        agent_dir = change_direction(agent_dir, input_key)  
        self.velocity = 4 * agent_dir
        if 's' in input_key:
            self.velocity = self.velocity / 4 * 6
        return agent_dir
        