from action import Action
from basic_math import *


class Agent:
    def __init__(self, start_x=2.0, start_y=0.0, start_z=2.0, HP=100, stamina=200):
        self.pos = np.array([start_x, start_y, start_z])
        self.HP = HP
        self.stamina = stamina
        #Action(action_id, veclocity, acting_time=1.3, stamina_consume=-4.8, input_key=None)
        self.action = Action(action_id=0, velocity=np.array([0.,0.,0.]))
        self.dir = np.array([0., 0., 1.])   # base direction. D 버튼을 눌렀을 때 cos = 1인 방향. 크기 = 1

    @classmethod
    def from_agent(cls, agent) -> 'Agent':
        return cls(start_x=agent.pos[0], start_y=agent.pos[1], start_z=agent.pos[2], HP=agent.HP, stamina=agent.stamina)

    def Update(self, agent):
        self.pos = agent.get_current_position()
        self.HP = agent.HP
        self.stamina = agent.stamina
        self.action.Update(agent.action)
        self.dir = agent.get_current_direction()
    
    def get_current_position(self):
        return np.copy(self.pos)
    
    def get_current_action(self):
        return self.action
    
    def get_current_direction(self):
        return np.copy(self.dir)
    
    def update_position(self, pos):
        self.pos = np.copy(pos)
        
    def update_action(self, action):
        self.action.Update(action)
        
    def update_direction(self, direction):
        direction[1] = 0    # make y-axis velocity feature be 0.
        self.dir = norm(np.matmul(rotate_matrix(angle=-np.pi/2), direction))