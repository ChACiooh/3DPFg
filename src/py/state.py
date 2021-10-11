class State:
    def __init__(self, remained_distance, state_id, state_no, spend_time=0):
        self.remained_distance = remained_distance
        self.id = state_id # field, wall, highair, lowair, goal, death
        self.no = state_no # 0 ~ 65
        self.spend_time = spend_time
        
    def Update(self, state):
        self.remained_distance = state.remained_distance
        self.id = state.id
        self.no = state.no
        self.spend_time = state.spend_time
    
    @classmethod
    def from_state(cls, state) -> 'State':
        return cls(remained_distance=state.remained_distance, state_id=state.id, state_no=state.no, spend_time=state.spend_time)