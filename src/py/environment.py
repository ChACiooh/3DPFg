from state import State
from action import Action
from agent import Agent
import numpy as np
import math

stamina_area = [19, 39, 59, 79, 100]
len_stamina_area = len(stamina_area)
state_maps = {'field':0, 'wall':len_stamina_area, 
              'highair':len_stamina_area*2, 
              'lowair':len_stamina_area*3, 
              'goal':len_stamina_area*4, 'death':len_stamina_area*4+1}

def EuclideanDistance(pos1, pos2):
    pos3 = pos2 - pos1
    return math.sqrt(np.dot(pos3, pos3))



class Environment:
    # agent : agent object
    # map_info : 2d array to represent current map's heights
    # goal_position : position object
    # num_states : number of states
    # num_actions : number of actions
    # consume_stamina_info : stamina consume amount / fps with respect to action id(integer)
    # fall_damage : damage that reduces agents' HP when he fall.
    # fall_min_height : the height that can make damage
    # MAX_timestep : cutting size
    # MAX_stamina : maximum stamina value that agent can have
    # waiting_time : time until gain next action, unit_time=sec
    # parachute_height : minimum height that agent can unfold his parachute.
    def __init__(self, agent, map_info, goal_position,
                 num_states, num_actions, 
                 state_ids, action_ids, 
                 consume_stamina_info, 
                 fall_damage,
                 fall_min_height,
                 MAX_timestep=500,
                 MAX_stamina=200, 
                 unit_time=1.3, 
                 parachute_height=3,
                 gravitial_acc=9.8):
        self.initial_agent = agent
        self.agent = agent
        self.initial_state = State(EuclideanDistance(self.agent.get_current_pos(), goal_position), state_id='field',
                                             spend_time=state_maps['field']+len_stamina_area-1)
        self.state = self.initial_state
        self.map_info = map_info
        self.goal_position = goal_position
        self.num_states = num_states
        self.num_actions = num_actions
        self.state_ids = state_ids
        self.action_ids = action_ids
        self.consume_stamina_info = consume_stamina_info
        self.fall_damage = fall_damage
        self.fall_min_height = fall_min_height
        self.MAX_timestep = MAX_timestep
        self.MAX_stamina = MAX_stamina
        self.unit_time = unit_time
        self.parachute_height = parachute_height
        self.g = np.array([0., gravitial_acc, 0.])
        self.dataset = []

    def cal_next_pos(self, state, action):
        pos = self.agent.get_current_position()
        if state.id == 'death' or state.id == 'goal' or action.action_id == 'Wait':
            return pos
        
        next_pos = pos + action.velocity*self.unit_time - 1/2 * self.g * (self.unit_time ** 2)
        
        return next_pos
    
    def state_transition(self, state, action):
        if state.id == 'death' or state.id == 'goal':
            return state
        
        next_pos = cal_next_pos(state, action)
        nx, ny, nz = next_pos.get_position()
        
        def calc_fall_damage():
            fall_height = y - ny - self.fall_min_height
            return 0 if fall_height <= 0 else fall_height * self.fall_damage
        
        stamina = self.agent.stamina - self.consume_stamina_info[action.id]
        if stamina < 0:
            stamina = 0
        elif stamina > self.MAX_stamina:
            stamina = self.MAX_stamina

        remained_distance = EuclideanDistance(next_pos, self.goal_position)
        
        #next_state = State(remained_distance, state_id, spend_time=state.spend_time+self.unit_time)
        if y == ny or ny == self.map_info[nx][nz]:
            next_state_id  = state.id
            self.agent.HP -= calc_fall_damage()
            if self.agent.HP <= 0:
                next_state_id = 'death'
        elif y < ny:
            if state.id == 'wall':
                if ny < self.map_info[nx][nz]:
                    next_state_id = 'wall'
                else:
                    next_state_id = 'field'
        elif y > ny:
            if ny > self.map_info[nx][nz] + self.parachute_height:
                next_state_id = 'highair'
            else:
                next_state_id = 'lowair'
        
        if next_state_id != 'death' and next_state_id != 'goal':
            for i in range(len_stamina_area):
                if stamina <= stamina_area[i]:
                    next_state_no = state_maps[next_state_id] + i
                    break
                
        #self.agent.action = action
        #self.agent.update_position(nx, ny, nz)
        next_state = State(remained_distance, next_state_id, next_state_no, spend_time=state.spend_time+self.unit_time)
        
        return next_state, next_pos
    
    def reward(self, state, action):
        next_state, next_pos = state_transition(state, action)
        deltaDistance = next_state.remained_distance - state.remained_distance
        
        return -deltaDistance, next_state, next_pos
    
    def make_scenarios(self, n=10):
        for batch in range(n):
            scenario = []
            self.agent = self.initial_agent
            self.state = self.initial_state
            action = self.agent.action
            for t in range(self.MAX_timestep):
                r, ns, np = reward(state, action)
                scenario.append((r, state, action))
                if ns.state_id == 'death' or ns.state_id == 'goal':
                    break
            r_sum = 0
            for scene in scenario:
                r_sum += scene[0]
            for t in range(1, len(scenario)):
                scenario[t][0] -= scenario[t-1][0] # calculate return to go
                
            self.dataset.append(scenario)
        
        return self.dataset
    
    def reset(self, dataset_initialize=False):
        self.agent = self.initial_agent
        self.state = self.initial_state
        if dataset_initialize == True:
            self.dataset = []
    
    
    
    