class State:
    def __init__(self, remained_distance, state_id, state_no, spend_time=0):
        self.remained_distance = remained_distance
        self.id = state_id # field, wall, highair, lowair, goal, death
        self.no = state_no # 0 ~ 65
        self.spend_time = spend_time
        
    