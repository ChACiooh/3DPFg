class Action:
    def __init__(self, speed, action_id, input_key=None):
        self.speed = speed
        self.action_id = action_id
        self.input_key = input_key
        
    def get_action_id(self):
        return self.action_id
    
    def get_action_key(self):
        return self.input_key