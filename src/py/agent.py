from action import Action

class Agent:
    def __init__(self, start_x=0.0, start_z=0.0, agent_action=Action(speed=0, action_id=0)):
        self.xpos = start_x
        self.zpos = start_z
        self.action = agent_action
    
    def get_current_position(self):
        return self.xpos, self.zpos
    
    def get_current_action(self):
        return self.action