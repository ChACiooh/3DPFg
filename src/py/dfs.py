
"""
Parameters
id : expected next state id
next_pos : expected next position of the agent

Return
action_keys : enabled input action keys
"""
def next_args(id, next_pos):
    action_keys = []]
    if id == 'air':
        if self.canParachute(next_pos) == True:
            action_keys = ['Wait', 'j']
        else:
            action_keys = ['Wait']
    elif id == 'field':
        action_keys = self._keys_
    elif id == 'wall':
        if state.id != 'wall':  # need information before state
            self.agent.update_direction(action.velocity)      # x-z 방향 전환
        # Only can be W, S, and Wj
        action_keys = ['W', 'S', 'Wj']
    elif id == 'parachute':
        action_keys = ['W', 'A', 'S', 'D', 'WA', 'WD', 'SA', 'SD', 'j']

    return action_keys

def dfs(self, state, action, timestep, scene):
    if timestep >= 500:
        return
    timestep += 1
    ns, r, done, next_pos = self.step(action)
    
    scene['rewards'].append(r)
    scene['timesteps'].append(ns.spend_time)
    if done == True:
        if 'dones' not in scene:
            scene['dones'] = []
        scene['dones'].append(r)

    elif timestep == self.MAX_timestep - 1:
        self.tle_cnt += 1
        if 'terminals' not in scene:
            scene['terminals'] = []
        scene['terminals'].append(1)
        self.logging(self.state, action, timestep=timestep+1, reward=r, next_pos=next_pos)
        return

    # calculate next situation
    #state = ns  # ok
    if ns.id == 'death' or ns.id == 'goal':
        if state.id == 'death':
            scene['terminals'] = [1]
            scene['rewards'][-1] = r = -999999
        self.logging(self.state, action, timestep=timestep+1, reward=r, next_pos=next_pos)
        return

    #scenario.append(scene)

    # 다음 action을 randomly generate하고, 기초적인 parameter를 초기화한다.
    stamina_consume = base_stamina_consume # 회복수치, -4.8
    acting_time = base_acting_time # 1.3sec

    # 경우에 따라 parameter 값을 조정한다.
    velocity = None
    given = 'None'
    next_arguments = next_args(ns.id, )
    
    # TODO : 다시 environment.py 참고하면서 짜기
        
    # Note: 각 구체적인 값은 parameter table 참조
    self.state.Update(state)
    self.agent.update_position(next_pos)
    # return value of action_update is newly constructed.
    # So, it is okay.
    next_action = Action(next_action_id, velocity, acting_time=acting_time, stamina_consume=stamina_consume, input_key=next_key_input)
    next_action.action_update(next_action_id, next_key_input, stamina_consume, acting_time, self.agent.dir, velocity, given=given)
    self.agent.action.Update(next_action)

    dfs(self, ns, next_action, timestep+1, next_action_list, scene)

    #scene['observations'].append(self.state.get_state_vector())
    #scene['actions'].append(action.get_action_vector(self.action_ids))