from action import Action

class PositionVec:
    def __init__(self, x, y, z):
        self.x=x
        self.y=y
        self.z=z
    def get_position(self):
        return self.x, self.y, self.z

class Agent:
    def __init__(self, start_x=0.0, start_y=0.0, start_z=0.0, HP=100, stamina=100, agent_action=Action(speed=0, action_id=0)):
        self.pos = PositionVec(start_x, start_y, start_z)
        self.HP = HP
        self.stamina = stamina
        self.action = agent_action
    
    def get_current_position(self):
        return self.pos
    
    def get_current_action(self):
        return self.action
    
    def get_current_direction(self):
        return self.action.direction
    
    def update_position(self, pos):
        self.pos = pos