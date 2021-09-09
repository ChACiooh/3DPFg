from action import Action

class Agent:
    def __init__(self, start_x=0.0, start_y=0.0, start_z=0.0, HP=100, stamina=100, agent_action=Action(speed=0, action_id=0)):
        self.xpos = start_x
        self.ypos = start_y
        self.zpos = start_z
        self.HP = HP
        self.stamina = stamina
        self.action = agent_action
    
    def get_current_position(self):
        return self.xpos, self.ypos, self.zpos
    
    def get_current_action(self):
        return self.action
    
    def get_current_direction(self):
        return self.action.direction
    
    def update_position(self, x, y, z):
        self.xpos = x
        self.ypos = y
        self.zpos = z