from state import State
from action import Action
from agent import Agent

class Environment:
    def __init__(self, agent, map_info, 
                 num_states, num_actions, 
                 state_ids, action_ids, 
                 consume_stamina_info, 
                 fall_damage,
                 fall_min_height,
                 MAX_stamina=100, 
                 waiting_time=2, 
                 parachute_height=3):
        self.agent = agent
        self.map_info = map_info
        self.num_states = num_states
        self.num_actions = num_actions
        self.state_ids = state_ids
        self.action_ids = action_ids
        self.consume_stamina_info = consume_stamina_info
        self.fall_damage = fall_damage
        self.fall_min_height = fall_min_height
        self.MAX_stamina = MAX_stamina
        self.waiting_time = waiting_time
        self.parachute_height = parachute_height

    def state_transition(self, state, action):
        if state.id == 'death' or state.id == 'goal':
            return state
        
        speed = action.get_speed()
        shift = speed * self.action_time
        x, y, z = self.agent.get_current_position()
        direction = action.direction
        
        nx = x + direction['x']
        ny = y + direction['y']
        nz = z + direction['z']
        
        def calc_fall_damage():
            fall_height = y - ny - self.fall_min_height
            return 0 if fall_height <= 0 else fall_height * self.fall_damage
        
        stamina = self.agent.stamina - self.consume_stamina_info[action.id]
        if stamina < 0:
            stamina = 0
        elif stamina > self.MAX_stamina:
            stamina = self.MAX_stamina

        remained_distance = # TODO:calculate
        
        #next_state = State(remained_distance, state_id, spend_time=state.spend_time+self.waiting_time)
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
        
                
        self.agent.action = action
        self.agent.update_position(nx, ny, nz)
    

"""
private State state_transition(State state, Action action)
        {
            // get p value
            State next_state = new State();

            float shift = 4 * agent.getSpeed() * t_u; // action마다 speed 부여하는 게 나을 듯
            float p = 5.0f; // 5m 정의
            Vector3 dir_vec = cc.transform.position - tpCamera.transform.position;
            dir_vec = dir_vec.normalized;

            var worldPos = cc.transform.position;
            int mapX = (int)(((worldPos.x - t.transform.position.x) / t.terrainData.size.x) * t.terrainData.alphamapWidth);
            int mapZ = (int)(((worldPos.z - t.transform.position.z) / t.terrainData.size.z) * t.terrainData.alphamapHeight);

            float dx = dir_vec.x, dz = dir_vec.z, delta_height = 0f;
            int i, j = 0;

            for(i = 0; i < RL_Constants.xSize; ++i)
            {
                bool flag = false;
                for(j = 0; j < RL_Constants.zSize; ++j)
                {
                    delta_height = map_info[i, j] - map_info[0, 0];
                    if(Math.Abs(delta_height) >= 1.5f)
                    {
                        p = (float)Math.Sqrt((i * dx) * (i * dx) + (j * dz) * (j * dz));
                        flag = true;
                        break;
                    }
                }
                if(flag)    break;
            }

            //if(before_action.getAction())
            // TODO : action에 따른 스태미나 감소 등 처리
            // 사망 관련 진단도 해야 한다.
            if(shift < p)
            {
                // keep going
                next_state = now_state;
            }
            else
            {
                // determine action
                if(i < RL_Constants.xSize && j < RL_Constants.zSize)
                {
                    double angle = Math.Atan((double)delta_height);
                    Activities activity;
                    if(angle >= Math.PI / 4)
                    {
                        // 등반하는 state로 전이시키기
                        // TODO : next_state.뭐시기, stamina 참고하면서 state 다른 번호로 분류
                        activity = Activities.Climb;
                    }
                    else
                    {
                        // 낙하하는 state로 전이시키기
                        // TODO : next_state.뭐시기
                        activity = Activities.FF;
                    }
                }
                else
                {
                    // keep going
                    next_state = now_state;
                }
            }
            
            return next_state;
        }
"""