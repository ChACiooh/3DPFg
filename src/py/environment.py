from numpy.random.mtrand import f
from state import State
from action import Action
from action import *
from agent import Agent
from basic_math import *
import time

stamina_area = [19, 39, 59, 79, 100]
len_stamina_area = len(stamina_area)
# starting point of state_ids
state_maps = {'field':0, 'wall':len_stamina_area, 
              'parachute':len_stamina_area*2, 
              'air':len_stamina_area*3, 
              'death':len_stamina_area*4, 'goal':len_stamina_area*4+1}



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
                 parachute_height=5,
                 gravitial_acc=9.8,
                 climb_angle=60,
                 gliding_down=10.0):
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
        self.logs = []

    def isGoal(self, pos):
        d = EuclideanDistance(self.goal_position, pos)
        return d <= 0.5

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
        if state.id == 'death' or state.id == 'goal' or action.input_key == 'Wait':
            return next_pos, state.id
        elif state.id == 'air' and 'j' in action.input_key:
            # 현재 air 상태인데 입력된 action에 점프 키가 있다
            next_state_id = 'parachute'
            return next_pos, next_state_id
            # parachute mode on
        elif state.id == 'parachute' and 'j' in action.input_key:
            next_state_id = 'air'
            return next_pos, next_state_id
        elif state.id == 'field' and 'j' in action.input_key:
            next_state_id = 'air'
            
        # 60 frame으로 나눠서 충돌 테스트
        t = action.acting_time / 60
        st = action.stamina_consume / 60
        next_stamina = self.agent.stamina
        prev_pos = self.agent.get_current_position()                    # copy
        v_xz = np.array([action.velocity[0], 0., action.velocity[2]])   # distribute by x,z
        v_y = np.array([0., action.velocity[1], 0.])                    # distribute by y
            
        if next_state_id == 'wall':
            # agent의 기저 벡터 space의 y-z평면을 기반으로 하지 않고,
            # 기존처럼 하되, 방향만 y-axis 방향으로 돌려둔 상태라고 가정.
            # 옆으로는 움직일 수 없다고 가정.
            for _ in range(60):
                next_pos = next_pos + v_y * t
                if next_stamina > 0 and st >= 0: # 벽에서는 회복 불가
                    next_stamina -= st

                if next_stamina < 1:   # stamina가 다하고 미끄러짐/떨어짐
                    next_stamina = 0
                    next_state_id = 'death'
                    return next_pos, next_state_id
                
            next_xz = np.copy(next_pos)
            next_xz[1] = 0
            prev_xz = np.copy(next_xz)
            y1 = self.map_info[int(prev_pos[0]), int(prev_pos[2])]
            y_hat = self.map_info[int(next_pos[0]), int(next_pos[2])]

            if not self.inBound(next_pos[0], next_pos[2]):
                next_state_id = 'death'

            elif y_hat > y1:
                while self.inBound(next_xz[0], next_xz[2]):
                    if self.map_info[int(next_xz[0]), int(next_xz[2])] != y1:
                        break
                    if int(next_xz[0]) != int(prev_xz[0]) or int(next_xz[2]) != int(prev_xz[2]):
                        break
                    next_xz += self.agent.dir * 0.05
                    print(f'prev={prev_xz}')
                    print(f'next={next_xz}')

                y2 = self.map_info[int(next_xz[0]), int(next_xz[2])]
                a = y2 - y_hat
                b = y_hat - y1
                next_xz = prev_xz + (next_xz - prev_xz) * a / (a+b)
                next_pos[0] = next_xz[0]
                next_pos[2] = next_xz[2]
            
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

                if next_pos[1] < 0:
                    next_pos[1] = 0
                    if next_state_id == 'air':
                        damage = self.calc_fall_damage(y=prev_pos[1], ny=0)
                        self.agent.HP -= damage
                        if self.agent.HP < 1:
                            self.agent.HP = 0
                            next_state_id = 'death'
                        else:
                            next_state_id = 'field'
                        break
                    elif next_state_id == 'parachute':
                        next_state_id = 'field'
                        break
                        
                if self.isWall(prev_pos[0], prev_pos[2], x, z) == True:
                    next_state_id = 'wall'
                    break

                #prev_pos = np.copy(next_pos)
        self.agent.stamina = next_stamina
        return next_pos, next_state_id
    
    def state_transition(self, state, action):
        if state.id == 'death' or state.id == 'goal':
            return state, self.agent.get_current_pos()
        next_pos, next_state_id = self.cal_next_pos(state, action)

        remained_distance = EuclideanDistance(next_pos, self.goal_position)

        next_state_no = state.no
        if next_state_id != 'death' and next_state_id != 'goal':
            for i in range(len_stamina_area):
                if self.agent.stamina / self.MAX_stamina * 100.0 <= stamina_area[i]:
                    next_state_no = state_maps[next_state_id] + i
                    break
                
        if self.isGoal(next_pos) == True:
            next_state_id = 'goal'
        next_state = State(remained_distance, next_state_id, next_state_no, spend_time=state.spend_time+action.acting_time)
        return next_state, next_pos
    
    def get_random_action(self):
        _keys_ = list(self.action_ids.keys())
        key = np.random.randint(self.num_actions)
        return _keys_[key], self.action_ids[_keys_[key]]

    def reward(self, state, action):
        next_state, next_pos = self.state_transition(state, action)
        deltaDistance = next_state.remained_distance - state.remained_distance
        
        return -deltaDistance, next_state, next_pos
    
    def step(self, action):
        reward, state, next_pos = self.reward(self.state, action)
        done = (state.id == 'goal')
        return state, reward, done, next_pos

    def logging(self, state, action, timestep, reward, next_pos):
        pos = self.agent.pos
        x, y, z = pos[0], pos[1], pos[2]
        nx, ny, nz = next_pos[0], next_pos[1], next_pos[2]
        self.logs.append([state.id, action.input_key, timestep, reward, str((x, y, z))+'->'+str((nx, ny, nz))])
        return

    def save_log(self, task_no):
        t = time.strftime('%Y%m%d_%H-%M-%S', time.localtime(time.time()))
        task_no = str(task_no)
        gx = int(self.goal_position[0])
        gz = int(self.goal_position[2])
        g_pos = f'x{gx}z{gz}'
        filename = g_pos + '_' + t + '_' + str(task_no) + '.log'
        with open(f'logs/{filename}', 'w') as f:
            for log in self.logs:
                log_msg = f'coord:{log[4]}\n'
                log_msg += f'state:{log[0]}, action:{log[1]}, timestep:{log[2]}, reward:{log[3]}\n'
                log_msg += '=' * 50 + '\n'
                f.write(log_msg)
        return

    def print_log(self, n=20):
        print('')
        print('logs>')
        len_log = len(self.logs)
        if len_log < 2*n:
            for l in self.logs:
                print(f'coord:"{l[4]}"')
                print(f'state:"{l[0]}", action:"{l[1]}", timestep:"{l[2]}", reward:"{l[3]}"')
        elif len_log >= 2*n:
            for l in self.logs[:20]:
                print(f'coord:"{l[4]}"')
                print(f'state:"{l[0]}", action:"{l[1]}", timestep:"{l[2]}", reward:"{l[3]}"')
            for l in self.logs[len_log-20:]:
                print(f'coord:"{l[4]}"')
                print(f'state:"{l[0]}", action:"{l[1]}", timestep:"{l[2]}", reward:"{l[3]}"')
        return

    def make_scenarios(self, n=10):
        complete = 0
        tle_cnt = 0
        scenario = []
        task_no = 0
        print('initialized to make scenarios')
        print(f'Max time step={self.MAX_timestep}')
        while complete < n:
            # initialize
            task_no += 1
            # PRINT_DEBUG
            #print('')
            #print('='*20)
            #print(task_no)
            scene = dict()
            self.reset()
            action = self.agent.action = Action(action_id=self.action_ids['Wait'], velocity=np.array([0.,0.,0.]))
            scene['observations'] = [self.state.get_state_vector()]
            scene['actions'] = [action.get_action_vector(self.action_ids)]
            scene['rewards'] = []
            scene['timesteps'] = []
            #self.logging(self.state, action, 0, 0)
            for t in range(self.MAX_timestep):
                # PRINT_DEBUG
                #print(f'before: s_id={self.state.id}, pos={self.agent.pos}')
                ns, r, done, next_pos = self.step(action)
                # PRINT_DEBUG
                #print(f'after : s_id={ns.id}, pos={next_pos}, action={action.input_key}')
                #print('='*50)
                scene['rewards'].append(r)
                scene['timesteps'].append(ns.spend_time)
                if done == True:
                    if 'dones' not in scene:
                        scene['dones'] = []
                    scene['dones'].append(r)

                elif t == self.MAX_timestep - 1:
                    tle_cnt += 1
                    print(f'Time over. - {task_no}')
                    #print('failed:agent({}) / goal({})'.format(self.agent.get_current_position(), self.goal_position))
                    if 'terminals' not in scene:
                        scene['terminals'] = []
                    scene['terminals'].append(1)
                    self.logging(self.state, action, timestep=t+1, reward=r, next_pos=next_pos)
                    break

                # calculate next situation
                state = ns  # ok
                if state.id == 'death' or state.id == 'goal':
                    #scenario.append(scene)
                    if state.id == 'death':
                        print(f'You Died. - {task_no}')
                        tle_cnt += 1
                    self.logging(self.state, action, timestep=t+1, reward=r, next_pos=next_pos)
                    break

                #scenario.append(scene)

                # 다음 action을 randomly generate하고, 기초적인 parameter를 초기화한다.
                next_key_input, next_action_id = self.get_random_action()
                stamina_consume = base_stamina_consume # 회복수치, -4.8
                acting_time = base_acting_time # 1.3sec

                # 경우에 따라 parameter 값을 조정한다.
                velocity = None
                given = 'None'
                if state.id == 'air':
                    stamina_consume = 0         # no recover, no consume
                    if next_pos[1] >= self.parachute_height:
                        while next_key_input != 'j' and next_key_input != 'Wait':
                            next_key_input, next_action_id = self.get_random_action()
                    else:
                        next_key_input, next_action_id = 'Wait', self.action_ids['Wait']
                elif state.id == 'field':
                    if 's' in next_key_input:   # sprint
                        stamina_consume = 20
                        acting_time = 1
                    if 'j' in next_key_input:
                        stamina_consume = 1 if stamina_consume == base_stamina_consume else stamina_consume + 1
                elif state.id == 'wall':
                    stamina_consume = 10
                    if self.state.id != 'wall':
                        self.agent.update_direction(action.velocity)      # x-z 방향 전환
                    while next_key_input != 'W' and next_key_input != 'S' and next_key_input != 'Wj':             # spinning
                        # Only can be W, S, and Wj
                        next_key_input, next_action_id = self.get_random_action()
                    given = 'wall'
                    if 'W' in next_key_input:
                        velocity = np.array([0., 1., 0.])
                    else:   # 'S'
                        velocity = np.array([0., -1., 0.])
                    if 'j' in next_key_input:
                        stamina_consume = 25
                        velocity *= 2
                elif state.id == 'parachute':
                    while 's' in next_key_input:
                        next_key_input, next_action_id = self.get_random_action()
                    stamina_consume = 2
                    given = 'parachute'
                    
                # Note: 각 구체적인 값은 parameter table 참조
                
                self.logging(self.state, action, timestep=t+1, reward=r, next_pos=next_pos)
                self.state.Update(state)
                self.agent.update_position(next_pos)
                # return value of action_update is newly constructed.
                # So, it is okay.
                action.action_update(next_action_id, next_key_input, stamina_consume, acting_time, self.agent.dir, velocity=velocity, given=given)
                self.agent.action.Update(action)

                scene['observations'].append(self.state.get_state_vector())
                scene['actions'].append(action.get_action_vector(self.action_ids))
                scene['rewards'].append(r)
            # steps ended.
            #self.print_log()
            
            for key in scene.keys():
                if key != 'observations' and key != 'actions':
                    scene[key] = np.array(scene[key])   # make {key:np.array(), ...}
            scenario.append(scene)
            if state.id == 'goal':
                complete += 1
                print(f'complete - {complete} / {n}')
                self.save_log(task_no)
                #self.print_log()

            """if complete == 0 and tle_cnt >= n:
                print('Failed.\nIt needs to add Time-steps.')
                break"""
        
        self.dataset.append(scenario)
        return scenario
    
    def get_dataset(self):
        return self.dataset
    
    def reset(self, dataset_initialize=False):
        # print('action_id["Wait"] =', self.action_ids['Wait'])
        self.agent.Update(self.initial_agent)
        self.state.Update(self.initial_state)
        self.logs = []
        if dataset_initialize == True:
            self.dataset = []
        return self.state.get_state_vector()
    
    
    
    