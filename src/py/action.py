class Action:
    def __init__(self, speed, action_id, input_key=None, direction={'x':0, 'y':0, 'z':'1'}):
        self.speed = speed
        self.id = action_id
        self.input_key = input_key
        self.direction = direction
        