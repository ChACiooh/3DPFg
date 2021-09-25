class Action:
    def __init__(self, acting_time, action_id, veclocity, input_key=None):
        self.acting_time = acting_time
        self.id = action_id
        self.input_key = input_key
        self.velocity = veclocity
        