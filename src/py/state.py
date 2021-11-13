import numpy as np
import json

with open('json/state_ids.json', 'r') as f:
    state_ids = json.load(f)

state_names = list(state_ids.keys())

def stateId2Val(id) -> int:
    _ids = {'field':0, 'air':1, 'wall':2, 'parachute':3, 'death':4, 'goal':5}
    return _ids[id]

class State:
    def __init__(self, remained_distance, state_id, state_no, spend_time=0):
        self.remained_distance = remained_distance
        self.id = state_id # field, wall, air, parachute, death, death
        self.no = state_no # 0 ~ 65
        self.spend_time = spend_time
    
    @classmethod
    def from_state(cls, state) -> 'State':
        return cls(remained_distance=state.remained_distance, state_id=state.id, state_no=state.no, spend_time=state.spend_time)    
    
    def Update(self, state):
        self.remained_distance = state.remained_distance
        self.id = state.id
        self.no = state.no
        self.spend_time = state.spend_time

    def get_state_vector(self):
        state = [self.remained_distance, stateId2Val(self.id), self.no, self.spend_time]
        return np.array(state, dtype=np.float32)
    

def cnv_state_vec2obj(emb_vec):
    remained_distance = emb_vec[0]
    id = round(emb_vec[1])
    id = state_names[id]
    no = emb_vec[2]
    spend_time = emb_vec[3]
    
    #action_id, velocity, acting_time=base_acting_time, stamina_consume=base_stamina_consume, input_key='Wait'
    return State(remained_distance=remained_distance, state_id=id, state_no=no, spend_time=spend_time)