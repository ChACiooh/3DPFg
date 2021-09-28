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

def vector_size(vec):
    return math.sqrt(np.dot(vec, vec))

def norm(vec):
    _size_ = vector_size(vec)
    return vec / _size_

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
                 gravitial_acc=9.8,
                 gliding_down=10.0):
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
        self.gliding_down = np.array([0., gliding_down, 0.])
        self.dataset = []

    def cal_next_pos(self, state, action):
        pos = self.agent.get_current_position()
        if state.id == 'death' or state.id == 'goal' or action.action_id == 'Wait':
            return pos
        
        # 60 frame으로 나눠서 충돌 테스트
        t = action.action_time / 60
        next_pos = pos
        next_state_id = state.id
        while t <= action.action_time:
            
            x, y, z = next_pos[0], next_pos[1], next_pos[2]
            if y < self.map_info[int(x), int(z)]:
                if self.map_info[int(x), int(z)] - y > 10:  # 10보다 작거나 같은 경우에는 그냥 그 높이에 agent를 붙여준다.
                    y1 = self.map_info[int(x), int(z)]
                    y2 = self.map_info[int(x), int(z)]
                    theta = 0
                    v = norm(action.velocity)
                    x1 = x
                    z1 = z
                    x2 = x
                    z2 = z
                    while v1 != self.map_info[int(x), int(z)]:
                        x1 = x1 + v[0]*theta
                        z1 = z1 + v[2]*theta
                        y1 = self.map_info[int(x1), int(z1)]
                        theta += 1/60
                    theta = 0
                    while v2 != self.map_info[int(x), int(z)]:
                        x2 = x2 + v[0]*theta
                        z2 = z2 + v[2]*theta
                        y2 = self.map_info[int(x2), int(z2)]
                        theta += 1/60
                    
                    p1 = np.array([x1, 0., z1])
                    p2 = np.array([x2, 0., z2])
                    angle = np.arctan(y1 - y2, EuclideanDistance(p1, p2))
                    if math.abs(angle) >= math.pi / 2:
                        next_state_id = 'wall'
                    else:
                        next_state_id = 'field'
                break
                
            next_pos = next_pos + action.velocity*t
            
            if y > self.map_info[int(x), int(z)]:
                next_state_id = 'air'
            
            if next_state_id == 'air':
                next_pos = next_pos - 1/2 * self.g * (t ** 2)
            elif next_state_id == 'parachute':
                next_pos = next_pos - self.gliding_down * t
            t += action.action_time / 60
        
        if next_pos[1] > self.map_info[next_pos[0], next_pos[2]]:
            next_state_id = 'air'
        return next_pos, next_state_id
    
    def state_transition(self, state, action):
        if state.id == 'death' or state.id == 'goal':
            return state
        
        next_pos, next_state_id = cal_next_pos(state, action)
        nx, ny, nz = next_pos[0], next_pos[1], next_pos[2]
        
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
        if y == ny or ny == self.map_info[nx, nz]:
            next_state_id  = state.id
            self.agent.HP -= calc_fall_damage()
            if self.agent.HP <= 0:
                next_state_id = 'death'
        
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
    
    def get_random_action(self):
        _keys_ = list(self.action_ids.keys())
        return np.random.randint(len(_keys_), size=1)
    
    def make_scenarios(self, n=10):
        for batch in range(n):
            scenario = []
            self.agent = self.initial_agent
            state = self.initial_state
            action = self.agent.action
            for t in range(self.MAX_timestep):
                r, ns, np = reward(state, action)
                scenario.append((r, state, action))
                state = ns
                if state.state_id == 'death' or state.state_id == 'goal':
                    break
                next_action_id = self.get_random_action()
                action.action_update(next_action_id, self.action_ids[next_action_id], self.agent.dir)
                self.agent.action.update_action(action)
            r_sum = 0
            if state.state_id == 'goal':
                for scene in scenario:
                    r_sum += scene[0]
            elif state.state_id == 'death'
                r_sum = -10000000
                
            for t in range(1, len(scenario)):
                scenario[t][0] -= scenario[t-1][0] # calculate return to go
                
            self.dataset.append(scenario)
        
        return self.dataset
    
    
    def reset(self, dataset_initialize=False):
        self.agent = self.initial_agent
        if dataset_initialize == True:
            self.dataset = []
    
    
    
    