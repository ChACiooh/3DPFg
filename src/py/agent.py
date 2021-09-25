from action import Action
import numpy as np


class Agent:
    def __init__(self, start_x=0.0, start_y=0.0, start_z=0.0, HP=100, stamina=100):
        self.pos = np.array([start_x, start_y, start_z])
        self.HP = HP
        self.stamina = stamina
        self.action = Action(acting_time=1.3, action_id=0, velocity=np.array([0.,0.,0.]))
    
    def get_current_position(self):
        return self.pos
    
    def get_current_action(self):
        return self.action
    
    def get_current_direction(self):
        return self.action.direction
    
    def update_position(self, pos):
        self.pos = pos