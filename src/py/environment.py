from state import State
from action import Action
from agent import Agent

class OurEnv:
    def __init__(self, agent, action_time=4):
        self.action_time = action_time

    def state_transition(state, action):
        speed = action.get_speed()
        shift = speed * action_time
        delta_height = @get_height
    

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