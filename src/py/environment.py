from numpy.random.mtrand import f
from state import State
from state import *
from action import Action
from action import *
from agent import Agent
from basic_math import *
from logger import *
from ds import Stack

import pickle
import os

stamina_area = [19, 39, 59, 79, 100]
len_stamina_area = len(stamina_area)
# starting point of state_ids
state_maps = {'field':0, 'wall':len_stamina_area, 
              'air':len_stamina_area*2, 
              'parachute':len_stamina_area*3, 
              'death':len_stamina_area*4, 'goal':len_stamina_area*4+1}

MINUS_INF = -999999

class Environment:
    # agent : agent object
    # map_info : 2d array to represent current map's heights
    # goal_position : position object
    # num_states : number of states
    # num_actions : number of actions
    # state_ids : {'state_kind':id}
    # action_ids : {'key_input':id}
    # consume_stamina_info : stamina consume amount / fps with respect to action id(integer)
    # fall_damage : damage that reduces agents' HP when he fall.
    # fall_min_height : the height that can make damage
    # MAX_timestep : cutting size
    # MAX_stamina : maximum stamina value that agent can have
    # waiting_time : time until gain next action, unit_time=sec
    # parachute_height : minimum height that agent can unfold his parachute.
    def __init__(self, id, agent, map_info, goal_position,
                 num_states, num_actions, 
                 state_ids, action_ids, 
                 fall_damage,
                 fall_min_height,
                 MAX_timestep=256,
                 MAX_stamina=200, 
                 unit_time=1.3, 
                 parachute_height=5,
                 gravitial_acc=9.8,
                 climb_angle=math.pi/3,
                 gliding_down=10.0):
        self.id = id
        self.initial_agent = agent
        self.agent = Agent.from_agent(agent)
        #State(remained_distance, state_id, state_no, spend_time=0)
        self.initial_state = State(EuclideanDistance(self.initial_agent.get_current_position(), goal_position), state_id='field',
                                    state_no=len_stamina_area-1)
        self.state = State.from_state(self.initial_state)
        self.map_info = map_info
        self.goal_position = goal_position
        self.num_states = num_states
        self.num_actions = num_actions
        self.state_ids = state_ids
        self.action_ids = action_ids
        self._keys_ = list(self.action_ids.keys())
        self.action_probs = softmax(np.ones(len(action_ids)))
        self.action_probs_vWall = softmax(np.ones(3))
        #self.consume_stamina_info = consume_stamina_info
        self.fall_damage = fall_damage
        self.fall_min_height = fall_min_height
        self.MAX_timestep = MAX_timestep
        self.MAX_stamina = MAX_stamina
        self.unit_time = unit_time
        self.parachute_height = parachute_height
        self.g = np.array([0., -gravitial_acc, 0.])
        self.climb_angle = climb_angle
        self.gliding_down = np.array([0., gliding_down, 0.])
        self.dataset = []
        self.death_cnt = 0
        self.goal_cnt = 0
        self.TL_cnt = 0
        self.logs = Stack()

    def convert_agent(self, agent):
        self.initial_agent = agent
        self.agent = Agent.from_agent(agent)

    def convert_map_info(self, map_info, goal_position):
        self.map_info = map_info
        self.goal_position = goal_position

    def isGoal(self, pos):
        d = EuclideanDistance(self.goal_position, pos)
        return d <= math.sqrt(3)/2    # sphere in a cubic with side=1

    def inBound(self, x, z):
        return not (x < 0 or x >= len(self.map_info) or z < 0 or z >= len(self.map_info[0]))

    def isWall(self, x1, z1, x2, z2):
        x1 = int(x1)
        z1 = int(z1)
        x2 = int(x2)
        z2 = int(z2)
        tangent = (self.map_info[x1, z1] - self.map_info[x2, z2])
        e = EuclideanDistance(np.array([x1, 0, z1]), np.array([x2, 0, z2]))
        if e == 0 and self.map_info[x1, z1] != self.map_info[x2, z2]:
            return True
        angle = np.arctan(abs(tangent))

        return angle >= self.climb_angle

    def canParachute(self, pos):
        x, y, z = pos[0], pos[1], pos[2]
        return y - self.map_info[int(x), int(z)] >= self.parachute_height

    def calc_fall_damage(self, y, ny):
        fall_height = y - ny - self.fall_min_height
        return 0 if fall_height <= 0 else fall_height * self.fall_damage

    def cal_next_pos(self, state, action):
        agent = Agent.from_agent(self.agent)    # copy current agent object
        next_pos = agent.get_current_position()
        next_state_id = state.id
        if state.id == 'death' or state.id == 'goal' or ((state.id == 'field' or state.id == 'wall') and action.input_key == 'Wait'):
            return state.id, agent
        elif state.id == 'air' and 'j' in action.input_key:
            # 현재 air 상태인데 입력된 action에 점프 키가 있다
            next_state_id = 'parachute'
            return next_state_id, agent
            # parachute mode on
        elif state.id == 'parachute' and 'j' in action.input_key:
            next_state_id = 'air'
            return next_state_id, agent
        elif state.id == 'field' and 'j' in action.input_key:
            next_state_id = 'air'
            
        # 60 frame으로 나눠서 충돌 테스트
        t = action.acting_time / 60
        st = action.stamina_consume / 60
        next_stamina = agent.stamina
        prev_pos = agent.pos    # DO NOT make be updated
        v_xz = np.array([action.velocity[0], 0., action.velocity[2]])   # distribute by x,z
        v_y = np.array([0., action.velocity[1], 0.])                    # distribute by y
            
        def goFront(pos, dir, cof):
            yangshim_cnt = 0
            nx, nz = pos[0], pos[2]
            while yangshim_cnt < 1000:
                nx += 0.05 * dir[0] * cof
                nz += 0.05 * dir[2] * cof
                yangshim_cnt += 1
                if int(pos[0]) != int(nx) or int(pos[2]) != int(nz):
                    break
            return np.array([nx, pos[1], nz])
        
        def isNextField(pos:np.ndarray, dir:np.ndarray, key_input='W') -> bool:
            cof = 1 if 'W' in key_input else (-1 if 'S' in key_input else 0)
            next_pos = goFront(pos, dir, cof)
            if not self.inBound(next_pos[0], next_pos[2]):
                return False
            ny = self.map_info[int(pos[0]), int(pos[2])]
            c = EuclideanDistance(np.array([int(next_pos[0]), ny, int(next_pos[2])]), pos)
            a = EuclideanDistance(np.array([int(next_pos[0]), 0 , int(next_pos[2])]), np.array([pos[0], 0, pos[2]]))
            angle = math.pi / 2 if a == 0 else math.acos(a / c)
            return angle < self.climb_angle
         
        if next_state_id == 'wall':
            # agent의 기저 벡터 space의 y-z평면을 기반으로 하지 않고,
            # 기존처럼 하되, 방향만 y-axis 방향으로 돌려둔 상태라고 가정.
            # 옆으로는 움직일 수 없음
        
            for _ in range(60):
                next_pos += v_y * t
                if next_stamina > 0 and st >= 0:
                    next_stamina -= st
                if next_stamina <= 0:   # 오르다가 air상태로 변경
                    next_stamina = 0
                    next_state_id = 'air'
                    agent.pos = next_pos
                    agent.stamina = next_stamina
                    return next_state_id, agent
                
            y_hat = next_pos[1]
            if 'W' in action.input_key and y_hat > self.map_info[int(next_pos[0]), int(next_pos[2])]:
                a = abs(y_hat - prev_pos[1])
                _next_pos_ = goFront(next_pos, agent.dir, 1)
                b = abs(_next_pos_[1] - y_hat)
                next_pos = interpolate(next_pos, _next_pos_, a, b)
            elif 'S' in action.input_key:
                _next_pos_ = goFront(next_pos, agent.dir, -1)
                if _next_pos_[1] < self.map_info[int(_next_pos_[0]), int(_next_pos_[2])]:
                    a = abs(y_hat - prev_pos[1])
                    b = abs(_next_pos_[1] - y_hat)
                    next_pos = interpolate(next_pos, _next_pos_, a, b)
            if isNextField(next_pos, agent.dir, action.input_key) == True:
                next_state_id = 'field'
            
        # if wall end
        else:
            for _ in range(60):
                next_pos = next_pos + (v_xz + v_y)*t 
                if next_state_id == 'air':
                    v_y += self.g * t
                x, y, z = next_pos[0], next_pos[1], next_pos[2]
                if not self.inBound(x, z):
                    next_state_id = 'death'
                    break
                next_stamina -= st
                if next_stamina < 1:
                    next_stamina = 0
                elif next_stamina >= self.MAX_stamina:
                    next_stamina = self.MAX_stamina

                if self.isWall(prev_pos[0], prev_pos[2], x, z) == True:
                    next_state_id = 'wall'
                    break
                
                if y <= self.map_info[int(x), int(z)]:
                    next_pos[1] = self.map_info[int(x), int(z)]
                    if next_state_id == 'air':
                        damage = self.calc_fall_damage(y=prev_pos[1], ny=next_pos[1])
                        agent.HP -= damage
                        if agent.HP < 1:
                            agent.HP = 0
                            next_state_id = 'death'
                        else:
                            next_state_id = 'field'
                        break
                    elif next_state_id == 'parachute':
                        next_state_id = 'field'
                        break
                elif next_state_id == 'field':   #걸어 내려가는 상황
                    """if isNextField(next_pos, agent.dir, action.input_key) == True:
                        next_state_id = 'field'
                    else:"""
                    next_state_id = 'air'
                        #break

                #prev_pos = np.copy(next_pos)
        agent.stamina = int(next_stamina)
        agent.pos = next_pos
        agent.action = action # ref
        return next_state_id, agent
    
    def state_transition(self, state, action):
        if state.id == 'death' or state.id == 'goal':
            return state, Agent.from_agent(self.agent)
        
        next_state_id, agent = self.cal_next_pos(state, action)
        next_pos = agent.pos
        remained_distance = EuclideanDistance(next_pos, self.goal_position)

        next_state_no = state.no
        if next_state_id != 'death' and next_state_id != 'goal':
            for i in range(len_stamina_area):
                if agent.stamina / self.MAX_stamina * 100.0 <= stamina_area[i]:
                    next_state_no = state_maps[next_state_id] + i
                    break
                
        if self.isGoal(next_pos) == True:
            next_state_id = 'goal'
        next_state = State(remained_distance, next_state_id, next_state_no, spend_time=state.spend_time+action.acting_time)
        return next_state, agent
    
    def get_random_action(self):
        key = np.random.randint(self.num_actions)
        return self._keys_[key], self.action_ids[self._keys_[key]]

    def update_softmax_prob(self, idx, kind='general'):
        if kind == 'general':
            self.action_probs[idx] *= 1.2
            self.action_probs = softmax(self.action_probs)
        else:
            self.action_probs_vWall[idx] *= 1.2
            self.action_probs_vWall = softmax(self.action_probs_vWall)

    def get_softmax_action_vWall(self, before_key_input='W'):
        _keys = ['W', 'S', 'Wj']
        _idx = {'W':0, 'S':1, 'Wj':2}
        r = np.random.random()
        k = 0
        for i in range(len(self.action_probs_vWall)):
            key_input = _keys[i]
            key_id = self.action_ids[key_input]
            if self.action_probs_vWall[i] + k > r and r >= k:
                self.update_softmax_prob(idx=_idx[key_input], kind='wall')
                return key_input, key_id

        self.update_softmax_prob(idx=_idx[before_key_input], kind='wall')
        return before_key_input, self.action_ids[before_key_input]

    def get_softmax_action(self, before_key_input, excepts=[], only=[]):
        if len(only) > 0:
            p = softmax(np.ones(len(only)))
            r = np.random.random()
            k = 0
            for i in range(len(only)):
                key_input = only[i]
                key_id = self.action_ids[key_input]
                if p[i] + k > r and r >= k:
                    self.update_softmax_prob(idx=key_id)
                    return key_input, key_id
                k += p[i]

            key_input = only[-1]
            key_id = self.action_ids[key_input]
            self.update_softmax_prob(idx=key_id)
            return key_input, key_id

        only = list(set(self._keys_) - set(excepts))
        key_input, key_id = before_key_input, self.action_ids[before_key_input]
        r = np.random.random()
        k = 0
        for i in range(len(only)):
            key_input = only[i]
            key_id = self.action_ids[key_input]
            if self.action_probs[key_id] + k > r and r >= k:
                self.update_softmax_prob(idx=key_id)
                return key_input, key_id
            k += self.action_probs[key_id]

        key_input = only[-1]
        key_id = self.action_ids[key_input]
        self.update_softmax_prob(idx=key_id)
        return key_input, key_id

    def reward(self, state, action):
        next_state, agent = self.state_transition(state, action)
        deltaDistance = next_state.remained_distance - state.remained_distance
        return -deltaDistance, next_state, agent
    
    # action is ndarray vector
    def step(self, action):
        action = cnv_action_vec2obj(action)
        reward, state, agent = self.reward(self.state, action)
        done = (state.id == 'goal')
        return state.get_state_vector(), reward, done, agent
    
    def get_valid_action_list(self, state_id, stamina):
        if state_id == 'field':
            if stamina <= 0:
                return list(set(self.action_ids)- set([key for key in self.action_ids if 's' in key]) - set([key for key in self.action_ids if 'j' in key]))
            elif stamina >= self.MAX_stamina:
                return list(set(list(self.action_ids.keys())) - set(['Wait']))
            else:
                return list(self.action_ids.keys())
        elif state_id == 'air' and stamina > 0:
            return ['Wait', 'j']
        elif state_id == 'wall' and stamina > 0:
            return ['Wait', 'W', 'S', 'Wj']
        elif state_id == 'parachute' and stamina > 0:
            return list(set(self.action_ids)- set([key for key in self.action_ids if 's' in key]))
        return ['Wait']

    def make_scenarios(self, n:int=10, threshold=MINUS_INF, log_printing=False):
        #tle_cnt = 0
        #scenario = []
        #task_no = 1
        #death_cnt = 0
        print(f'{self.id} - initialized to make scenarios')
        print(f'Max time step={self.MAX_timestep}')
        print(f'objective: find {n} paths')
        # while complete < n:
            
        # initialize
        scene = dict()
        self.reset()
        # state: 현재 보는 local object 대상
        # self.state: 현상을 유지해야 하는 state to calculate several things
        state = State.from_state(self.initial_state)
        action = Action(action_id=self.action_ids['Wait'], velocity=np.array([0.,0.,0.]))
        self.agent.action.Update(action)
        scene['observations'] = Stack()
        scene['actions'] = Stack()
        scene['rewards'] = Stack()
        scene['timesteps'] = Stack()
        #time_out = False
        #next_key_input, next_action_id = 'Wait', 0
        
        def _save_scene_(scene, state_id, postfix):
            time_t = time.strftime('%Y%m%d_%H-%M-%S', time.localtime(time.time()))
            path = f'pkl/scenario/{state_id}/env_{self.id}/'
            if not os.path.exists(path):
                os.makedirs(path)
            scene_filename = path + f'{time_t}_{postfix}.scn'
            save_scene = {}
            for K, V in scene.items():  # K: observations, actions, rewards, timesteps
                save_scene[K] = np.array(V.getTotal())    # list of numpy array
                scene[K].pop()  # 마지막 step을 roll-back
            with open(scene_filename, 'wb') as f:
                pickle.dump(save_scene, f)
            return
        
        visit = np.zeros((25, 101, 101), dtype=bool)

        def isVisited(pos) -> bool:
            x, y, z = int(pos[0]), int(pos[1]), int(pos[2])
            if y > 20:
                return True
            return visit[y, x, z]

        def check_visit(pos, check=True) -> None:
            x, y, z = int(pos[0]), int(pos[1]), int(pos[2])
            visit[y, x, z] = check
            return

        def stepDFS(timestep, state:State, action:Action):
            # 시작부터 goal인 건 data 만들기 전에 그러지 않다고 가정
            if self.goal_cnt >= n:
                return
            
            if timestep > self.MAX_timestep:  # time over
                # It works well even though the scene is empty
                print('Time over')
                scene['observations'].pop()
                state.id = 'death'            # fixed step timeout
                scene['observations'].push(state.get_state_vector())
                scene['rewards'].push(MINUS_INF)
                scene['timesteps'].push(timestep)
                if 'terminals' not in scene:
                    scene['terminals'] = Stack()
                scene['terminals'].push(MINUS_INF)
                # save point
                if self.TL_cnt < 10:
                    self.TL_cnt += 1
                    _save_scene_(scene, state.id, self.TL_cnt)
                    logging(self.logs, self.agent.pos, state, action, timestep, MINUS_INF, self.agent.pos)
                    save_log(logger=self.logs, id=self.id, goal_position=self.goal_position, state_id='TL', cnt=self.TL_cnt)
                    delogging(self.logs)
                    
                for K in scene.keys():
                    scene[K].pop()
                check_visit(self.agent.pos, check=False)
                return
            
            if timestep > 1 and action.input_key == 'Wait' and (self.agent.stamina >= self.MAX_stamina or state.id == 'wall'):   # 아무 득도 안 되는 행동
                return
            
            scene['observations'].push(state.get_state_vector())
            scene['actions'].push(action.get_action_vector())
            action = action.get_action_vector()
            # step
            ns, r, d, agent = self.step(action)  # npos is used to update agent and determine whether it can unfold parachute
            ns = cnv_state_vec2obj(ns)
            action = cnv_action_vec2obj(action)
            scene['rewards'].push(r)
            scene['timesteps'].push(timestep)

            if r < threshold:
                for K in scene.keys():
                    scene[K].pop()
                return
            else:
                check_visit(agent.pos)
            
            logging(self.logs, self.agent.pos, state, action, timestep, r, agent.pos)
            
            if d == True:   # same with goal
                # savepoint
                self.goal_cnt += 1
                if 'dones' not in scene:
                    scene['dones'] = Stack()
                scene['dones'].push(r)
                _save_scene_(scene, 'goal', self.goal_cnt)                
                print(f'env{self.id} found out {self.goal_cnt} path(s)!')
                save_log(logger=self.logs, id=self.id, goal_position=self.goal_position, state_id='G', cnt=self.goal_cnt)
                delogging(self.logs)
                for K in scene.keys():
                    scene[K].pop()
                check_visit(agent.pos, check=False)
                return
            elif ns.id == 'death':
                # save point
                if 'terminals' not in scene:
                    scene['terminals'] = Stack()
                scene['terminals'].push(MINUS_INF)
                if self.death_cnt < 50:
                    self.death_cnt += 1
                    print(f'You Died - {self.id}')
                    _save_scene_(scene, 'death', self.death_cnt)
                    save_log(logger=self.logs, id=self.id, goal_position=self.goal_position, state_id='D', cnt=self.death_cnt)
                    delogging(self.logs)
                    
                for K in scene.keys():
                    scene[K].pop()
                check_visit(agent.pos, check=False)
                return

            action_list = self.get_valid_action_list(ns.id, agent.stamina)
            np.random.shuffle(action_list)
            # PRINT_DEBUG
            if log_printing == True:
                print(f'state: {state.id}->{ns.id}')
                print(f'action: {action.input_key}')
                print(f'agent: {self.agent.pos}->{agent.pos}')
                print(f'valid key list: {action_list}')

            for next_action_key_input in action_list:
                passing_agent = Agent.from_agent(agent)
                if ns.id == 'air' and 'j' in next_action_key_input:
                    if passing_agent.stamina <= 0 or self.canParachute(passing_agent.pos) == False:
                        continue
                elif ns.id == 'wall' and state.id != 'wall':
                    passing_agent.update_direction(action.velocity)
                
                velocity, stamina_consume, acting_time, given = get_next_action(ns.id, next_action_key_input, 
                                            self.action_ids[next_action_key_input],
                                            prev_velocity=action.velocity)
                
                next_action = Action.from_action(action)
                next_action.action_update(self.action_ids[next_action_key_input], next_action_key_input,
                                            stamina_consume, acting_time, passing_agent.dir, velocity, given)
                self.agent.Update(passing_agent)
                self.agent.update_action(next_action)
                self.state.Update(ns)
                    
                stepDFS(timestep+1, state=ns, action=next_action)
                
                self.agent.Update(agent)
                self.state.Update(state)
                if self.goal_cnt >= n:
                    break
            
            for K in scene.keys():
                scene[K].pop()
            delogging(self.logs)
            check_visit(self.agent.pos, check=False)
            return    
        
        stepDFS(timestep=1, state=state, action=action)
        
        """
            for t in range(self.MAX_timestep):
                # PRINT_DEBUG
                if log_printing == True:
                    print(f'before: s_id={self.state.id}, pos={self.agent.pos}')

                # step                
                action = action.get_action_vector()
                ns, r, done, next_agent = self.step(action)
                action = cnv_action_vec2obj(action)
                next_pos = next_agent.get_current_pos()
                logging(self.logs, self.agent.pos, self.state, action, timestep=t+1, reward=r, next_pos=next_pos)
                
                # PRINT_DEBUG
                if log_printing == True:
                    print(f'after : s_id={ns.id}, pos={next_pos}, action={action.input_key}')
                    print('='*50)
                scene['rewards'].push(r)
                scene['timesteps'].push(ns.spend_time)
                if done == True:
                    if 'dones' not in scene:
                        scene['dones'] = Stack()
                    scene['dones'].push(r)

                elif t == self.MAX_timestep - 1:
                    tle_cnt += 1
                    time_out = True
                    print(f'Time over. - {task_no}')
                    #print('failed:agent({}) / goal({})'.format(self.agent.get_current_position(), self.goal_position))
                    '''if 'terminals' not in scene:
                        scene['terminals'] = []
                    scene['terminals'].append(1)'''
                    break

                # calculate next situation
                state = ns  # ok
                if ns.id == 'death' or ns.id == 'goal':
                    #scenario.append(scene)
                    if ns.id == 'death':
                        death_cnt += 1
                        #print(f'You Died. - {task_no}')
                        scene['terminals'] = [1]
                        scene['rewards'][-1] = r = -999999
                    break

                #scenario.append(scene)

                # 다음 action을 randomly generate하고, 기초적인 parameter를 초기화한다.
                next_key_input, next_action_id = self.get_softmax_action(before_key_input=next_key_input)
                stamina_consume = base_stamina_consume # 회복수치, -4.8
                acting_time = base_acting_time # 1.3sec

                # 경우에 따라 parameter 값을 조정한다.
                velocity = None
                given = 'None'
                if ns.id == 'air':
                    stamina_consume = 0         # no recover, no consume
                    if self.canParachute(next_pos) == True:
                        next_key_input, next_action_id = self.get_softmax_action(before_key_input=next_key_input, only=['Wait', 'j'])
                    else:
                        next_key_input, next_action_id = 'Wait', self.action_ids['Wait']
                        self.update_softmax_prob(idx=next_action_id)
                elif ns.id == 'field':
                    if 's' in next_key_input:   # sprint
                        stamina_consume = 20
                        acting_time = 1
                    if 'j' in next_key_input:
                        stamina_consume = 1 if stamina_consume == base_stamina_consume else stamina_consume + 1
                elif ns.id == 'wall':
                    stamina_consume = 10
                    if self.state.id != 'wall':
                        self.agent.update_direction(action.velocity)      # x-z 방향 전환
                    # Only can be W, S, and Wj
                    next_key_input, next_action_id = self.get_softmax_action_vWall()
                    given = 'wall'
                    if 'W' in next_key_input:
                        velocity = np.array([0., 1., 0.])
                    else:   # 'S'
                        velocity = np.array([0., -1., 0.])
                    if 'j' in next_key_input:
                        stamina_consume = 25
                        velocity *= 2
                elif ns.id == 'parachute':
                    next_key_input, next_action_id = self.get_softmax_action(next_key_input, only=['W', 'A', 'S', 'D', 'WA', 'WD', 'SA', 'SD', 'j'])
                    stamina_consume = 2
                    given = 'parachute'
                    
                # Note: 각 구체적인 값은 parameter table 참조
                
                
                self.state.Update(ns)
                self.agent.update_position(next_pos)
                # return value of action_update is newly constructed.
                # So, it is okay.
                action.action_update(next_action_id, next_key_input, stamina_consume, acting_time, self.agent.dir, velocity=velocity, given=given)
                self.agent.action.Update(action)

                scene['observations'].append(self.state.get_state_vector())
                scene['actions'].append(action.get_action_vector())
            # steps ended.
            
            if log_printing == True:
                print_log()
            
            for key in scene.keys():
                if key != 'observations' and key != 'actions':
                    scene[key] = np.array(scene[key])   # make {key:np.array(), ...}
            
            #scenario.append(scene)
            # save scene at each file instead of memorizeing scenes in scenario array
            if not time_out and (ns.id == 'goal' or death_cnt <= 95):
                time_t = time.strftime('%Y%m%d_%H-%M-%S', time.localtime(time.time()))
                path = f'pkl/scenario/{ns.id}/env_{self.id}/'
                if not os.path.exists(path):
                    os.makedirs(path)
                scene_filename = path + f'{time_t}.scn'
                for scene_key in scene:
                    scene[scene_key] = np.array(scene[scene_key])
                with open(scene_filename, 'wb') as f:
                    pickle.dump(scene, f)

            if ns.id == 'goal':
                complete += 1
                print(f'complete - {complete} / {n}')
                save_log(self.logs, self.id, self.goal_position, task_no)
                
                if log_printing == True:
                    print_log()
            """
        # self.dataset.append(scenario)   # Probably unused
        print(f'env{self.id} succeeded with {self.goal_cnt}.')
        self.logs.clear()
        for K in scene.keys():
            scene[K].clear()
        return self.goal_cnt
    # function make_scenario end.
    
    def get_dataset(self):
        return self.dataset
    
    def reset(self, dataset_initialize=False):
        # print('action_id["Wait"] =', self.action_ids['Wait'])
        self.action_probs = softmax(np.ones(len(self.action_ids)))
        self.action_probs_vWall = softmax(np.ones(3))
        self.agent.Update(self.initial_agent)
        self.state.Update(self.initial_state)
        self.logs.clear()
        self.goal_cnt = self.death_cnt = self.TL_cnt = 0
        if dataset_initialize == True:
            self.dataset = []
        return self.state.get_state_vector()
    
    
    
    