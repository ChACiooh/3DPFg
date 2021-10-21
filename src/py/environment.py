from state import State
from action import Action
from action import *
from agent import Agent
from basic_math import *

stamina_area = [19, 39, 59, 79, 100]
len_stamina_area = len(stamina_area)
# starting point of state_ids
state_maps = {'field':0, 'wall':len_stamina_area, 
              'highair':len_stamina_area*2, 
              'lowair':len_stamina_area*3, 
              'goal':len_stamina_area*4, 'death':len_stamina_area*4+1}



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
                 fall_damage,
                 fall_min_height,
                 MAX_timestep=500,
                 MAX_stamina=200, 
                 unit_time=1.3, 
                 parachute_height=3,
                 gravitial_acc=9.8,
                 climb_angle=60,
                 gliding_down=10.0):
        self.initial_agent = agent
        self.agent = Agent.from_agent(agent)
        #State(remained_distance, state_id, state_no, spend_time=0)
        self.initial_state = State(EuclideanDistance(self.initial_agent.get_current_position(), goal_position), state_id='field',
                                    state_no=len_stamina_area-1)
        self.state = self.initial_state
        self.map_info = map_info
        self.goal_position = goal_position
        self.num_states = num_states
        self.num_actions = num_actions
        self.state_ids = state_ids
        self.action_ids = action_ids
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
        self.log = []


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

        return angle >= self.climb_angle * np.pi / 180

    def calc_fall_damage(self, y, ny):
        fall_height = y - ny - self.fall_min_height
        return 0 if fall_height <= 0 else fall_height * self.fall_damage

    def cal_next_pos(self, state, action):
        next_pos = self.agent.get_current_position()
        next_state_id = state.id
        y_err = 0.5
        if state.id == 'death' or state.id == 'goal':
            return next_pos, state.id
        elif state.id == 'air' and 'j' in action.action_id:
            # 현재 air 상태인데 입력된 action에 점프 키가 있다
            next_state_id = 'parachute'
            action.velocity[1] = -3
            # parachute mode on
            
        """
            현재 action에 모든 velocity 정보가 담겨 있다고 가정된 상태.
            그러나 현재 state에 따라서 그 velocity도 당연히 달라져야 한다
            이를테면 air상태와 parachute의 상태는 달라지기 때문에 parachute 모드일 때 velocity 조정 필요
            또한, 이 method에 들어온 시점에서 field가 아닌 state일 때에 대한 물리 옵션 확인 필요
        """
        # 60 frame으로 나눠서 충돌 테스트
        t = action.acting_time / 60
        st = action.stamina_consume / 60
        stamina_flag = False
        next_stamina = self.agent.stamina
        prev_pos = self.agent.get_current_position()                    # copy
        v_xz = np.array([action.velocity[0], 0., action.velocity[2]])   # distribute by x,z
        v_y = np.array([0., action.velocity[1], 0.])                    # distribute by y

        if next_state_id == 'wall':
            v_y /= 4    # 1 m/s, 기존은 4 m/s
            # agent의 기저 벡터 space의 y-z평면을 기반으로 하지 않고,
            # 기존처럼 하되, 방향만 y-axis 방향으로 돌려둔 상태라고 가정.
            # 옆으로는 움직일 수 없다고 가정.
            for _ in range(60):
                next_pos = next_pos + v_y * t
                next_stamina -= st

                if next_stamina <= 0:   # stamina가 다하고 미끄러짐/떨어짐
                    next_stamina = 0
                    stamina_flag = True
                    prev_pos = np.copy(next_pos)
                    prev_height = prev_pos[1]
                    while self.isWall(prev_pos[0], prev_pos[2], next_pos[0], next_pos[2]) == True:
                        checking_t = 1/60
                        prev_pos = np.copy(next_pos)
                        # 뒤로 가기 파트
                        while True:
                            next_pos = prev_pos - self.agent.dir * checking_t
                            if self.inBound(next_pos[0], next_pos[2]) == False:
                                next_state_id = 'death'
                                break
                            if self.map_info[int(next_pos[0]), int(next_pos[2])] != self.map_info[int(prev_pos[0]), int(prev_pos[2])]:
                                break
                            checking_t += 1/60

                        # 낙하 파트
                        while next_pos[1] > self.map_info[int(next_pos[0]), int(next_pos[2])]:
                            next_pos += 0.5*self.g*(1/3600)
                            if self.inBound(next_pos[0], next_pos[2]) == False:
                                next_state_id = 'death'
                                break
                            if next_pos[1] <= 0:
                                next_pos[1] = 0
                                break
                    self.agent.HP -= self.calc_fall_damage(prev_height, next_pos[1])
                    if self.agent.HP <= 0:
                        next_state_id = 'death'
                    if next_state_id != 'death':
                        next_state_id = 'field'
                    break

                px, pz = prev_pos[0], prev_pos[2]
                nx, nz = next_pos[0], next_pos[2]

                while self.inBound(nx, nz) == True and next_pos[1] != self.map_info[int(nx), int(nz)]: # 곡선 벽일 경우
                    if 'W' in action.input_key:
                        next_pos += self.agent.dir / 60
                    elif 'S' in action.input_key:
                        next_pos -= self.agent.dir / 60
                    nx, nz = next_pos[0], next_pos[2]
                if self.inBound(nx, nz) == False:
                    next_state_id = 'death'
                    break
                elif self.isWall(px, pz, nx, nz) == False:
                    next_state_id = 'field'
                    break

                prev_pos = np.copy(next_pos)

        else:
            for _ in range(60):
                next_pos = next_pos + (v_xz + v_y)*t 
                if next_state_id == 'air':
                    next_pos += 0.5*self.g*t*t

                next_stamina -= st
                if next_stamina <= 0:
                    next_stamina = 0
                    stamina_flag = True

                
                x, y, z = next_pos[0], next_pos[1], next_pos[2]
                if not self.inBound(x, z):
                    return next_pos, 'death'

                if next_state_id == 'air' or next_state_id == 'parachute':
                    if y - self.map_info[int(x), int(z)] <= y_err:
                        next_pos[1] = self.map_info[int(x), int(z)]
                        next_state_id = 'field'
                        if 'j' in action.input_key:
                            # jump action end.
                            break
                        
                if self.isWall(prev_pos[0], prev_pos[2], next_pos[0], next_pos[2]) == True:
                    next_state_id = 'wall'
                    break

                if stamina_flag == True:
                    break
                prev_pos = np.copy(next_pos)
        self.agent.stamina = next_stamina
        return next_pos, next_state_id
    
    def state_transition(self, state, action):
        if state.id == 'death' or state.id == 'goal':
            return state, self.agent.get_current_pos()
        y = self.agent.pos[1]
        next_pos, next_state_id = self.cal_next_pos(state, action)
        nx, ny, nz = next_pos[0], next_pos[1], next_pos[2]
        
        # acting_time만큼 지날 동안 action.stamina_consume을 소모
        stamina = self.agent.stamina - action.stamina_consume * (base_acting_time / action.acting_time)
        stamina = int(stamina)
        if stamina <= 0:
            stamina = 0
        elif stamina > self.MAX_stamina:
            stamina = self.MAX_stamina

        remained_distance = EuclideanDistance(next_pos, self.goal_position)
        
        #next_state = State(remained_distance, state_id, spend_time=state.spend_time+self.unit_time)
        if self.inBound(nx, nz) == True and (y == ny or ny == self.map_info[int(nx), int(nz)]):
            next_state_id  = state.id
            self.agent.HP -= self.calc_fall_damage(y, ny)
            if self.agent.HP <= 0:
                next_state_id = 'death'
        
        next_state_no = state.no
        if next_state_id != 'death' and next_state_id != 'goal':
            for i in range(len_stamina_area):
                if stamina / self.MAX_stamina * 100.0 <= stamina_area[i]:
                    next_state_no = state_maps[next_state_id] + i
                    break
                
        #self.agent.action = action
        #self.agent.update_position(nx, ny, nz)
        next_state = State(remained_distance, next_state_id, next_state_no, spend_time=state.spend_time+self.unit_time)
        
        return next_state, next_pos
    
    
    def reward(self, state, action):
        next_state, next_pos = self.state_transition(state, action)
        deltaDistance = next_state.remained_distance - state.remained_distance
        
        return -deltaDistance, next_state, next_pos
    
    def get_random_action(self, seed):
        np.random.seed(seed)
        _keys_ = list(self.action_ids.keys())
        key = int(np.random.randint(len(_keys_), size=1))
        return _keys_[key], self.action_ids[_keys_[key]]
    
    def step(self, action):
        reward, state, next_pos = self.reward(self.state, action)
        done = (state.id == 'goal')
        return state, reward, done, next_pos

    def logging(self, state, action, timestep, reward):
        self.log.append([state.id, action.input_key, timestep, reward])
        return

    def print_log(self, n=10):
        cnt = 0
        for l in self.log:
            cnt += 1
            print(f'state:"{l[0]}", action:"{l[1]}", timestep:"{l[2]}", reward:"{l[3]}"')
            if cnt == n:
                break
        return

    def make_scenarios(self, n=10):
        complete = 0
        tle_cnt = 0
        scenario = []
        task_no = 1
        while complete < n:
            # initialize
            if task_no == n:
                break
            print(task_no)
            task_no += 1
            print('='*20)
            scene = dict()
            self.agent.Update(self.initial_agent)
            #state.Update(self.initial_state)
            self.reset()
            action = self.agent.action = Action(action_id=self.action_ids['Wait'], velocity=np.array([0.,0.,0.]))
            scene['observations'] = [self.state.get_state_vector()]
            scene['actions'] = [action.get_action_vector(self.action_ids)]
            scene['rewards'] = []
            scene['timesteps'] = []
            self.logging(self.state, action, 0, 0)
            for t in range(self.MAX_timestep):
                ns, r, done, next_pos = self.step(action)
                scene['rewards'].append(r)
                scene['timesteps'].append(action.acting_time)
                if done == True:
                    if 'dones' not in scene:
                        scene['dones'] = []
                    scene['dones'].append(r)

                elif t == self.MAX_timestep - 1:
                    tle_cnt += 1
                    print('Time over.')
                    print('failed:agent({}) / goal({})'.format(self.agent.get_current_position(), self.goal_position))
                    if 'terminals' not in scene:
                        scene['terminals'] = []
                    scene['terminals'].append(1)
                    break

                # calculate next situation
                state = ns  # ok
                if state.id == 'death' or state.id == 'goal':
                    #scenario.append(scene)
                    break

                #scenario.append(scene)

                # 다음 action을 randomly generate하고, 기초적인 parameter를 초기화한다.
                # TODO : seed 값을 reward나 여러 다른 변수를 이용해 만들어보자.
                next_key_input, next_action_id = self.get_random_action(seed=t)
                stamina_consume = base_stamina_consume # 회복수치, -4.8
                acting_time = base_acting_time # 1.3sec

                # 경우에 따라 parameter 값을 조정한다.
                if state.id == 'air':
                    stamina_consume = 0         # no recover, no consume
                elif state.id == 'field':
                    if 's' in next_key_input:   # sprint
                        stamina_consume = 20
                        acting_time = 1
                    if 'j' in next_key_input:
                        stamina_consume = 1 if stamina_consume == base_stamina_consume else stamina_consume + 1
                elif state.id == 'wall':
                    self.agent.update_direction(action.velocity)      # 방향 전환
                    seed = t + 1
                    while 's' in next_key_input or 'A' in next_key_input or 'D' in next_key_input:                      # spinning
                        next_key_input, next_action_id = self.get_random_action(seed)
                        seed += 1
                    if 'j' in next_key_input:
                        stamina_consume = 25
                elif state.id == 'parachute':
                    stamina_consume = 2
                    acting_time = 1
                elif state.id == 'goal' or state.id == 'death':
                    tle_cnt += 1
                    if state.id == 'death':
                        print('You died.')
                    break
                # Note: 각 구체적인 값은 parameter table 참조
                
                self.state = state
                self.agent.update_position(next_pos)
                # return value of action_update is newly constructed.
                # So, it is okay.
                action.action_update(next_action_id, next_key_input, stamina_consume, acting_time, self.agent.dir)
                self.agent.action.Update(action)
                self.logging(state, action, timestep=t, reward=r)

                scene['observations'].append(self.state.get_state_vector())
                scene['actions'].append(action.get_action_vector(self.action_ids))
                scene['rewards'].append(r)
            # steps ended.

            self.print_log()
            for key in scene.keys():
                if key != 'observations' and key != 'actions':
                    scene[key] = np.array(scene[key])   # make {key:np.array(), ...}
            scenario.append(scene)
            if state.id == 'goal':
                '''r_t = 0
                len_scenario = len(scenario)
                for t in range(1, len_scenario):
                    r_t += scenario[len_scenario - t][0]
                    scenario[len_scenario - t][0] = r_t # calculate return to go'''
                complete += 1
                print(f'complete - {complete} / {n}')

            if complete == 0 and tle_cnt >= n * n:
                print('Failed.\nIt needs to add Time-steps.')
                break
        
        self.dataset.append(scenario)
        return scenario
    
    def get_dataset(self):
        return self.dataset
    
    def reset(self, dataset_initialize=False):
        # print('action_id["Wait"] =', self.action_ids['Wait'])
        self.agent = Agent.from_agent(self.initial_agent)
        self.state = State.from_state(self.initial_state)
        if dataset_initialize == True:
            self.dataset = []
        return self.state.get_state_vector()
    
    
    
    