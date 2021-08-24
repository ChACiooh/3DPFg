using System.Collections;
using UnityEditor;
using UnityEngine;
using UnityEngine.Events;
using System.Collections.Generic;
using System;

namespace Invector.vCharacterController
{
    public class Environment
    {
        private float[,] map_info;
        private Agent agent;
        private float tau = 1.0f;
        private double learning_rate_tau = 0.1f;
        private double[] prob_actions;
        private double[,] _table_;
        private State now_state;
        private Action before_action;
        private Action next_action;
        private bool now_action_doing = false;
        private double gamma = 0.01;    // need to fine-tune
        private int d = 10000;
        private int lr_exp = 0;
        private float t_u;
        private vThirdPersonController cc;
        private vCamera.vThirdPersonCamera tpCamera;
        private Terrain t;
        /* TODO : Recording 하기 위한 자료구조 선언 */

        public Environment(float waitingTime, float _tau_) 
        {
            agent = new Agent();
            _table_  = new double[RL_Constants.STATE_ID_MAX, RL_Constants.ACTION_NUM];
            map_info = new float[RL_Constants.xSize, RL_Constants.zSize];
            prob_actions = new double[RL_Constants.ACTION_NUM];
            initialize();
            tau = _tau_;
            t_u = waitingTime;
            lr_exp = 0;
            now_action_doing = false;
            now_state = new State(); // 초기 state initialize에서 정보가 부족한 상태
        }

        
        public double getQvalue(in int action_id)
        {
            return _table_[now_state.getStateNum(), action_id];
        }

        public void initialize() {
            for(int i = 0; i < RL_Constants.ACTION_NUM; ++i) {
                prob_actions[i] = UnityEngine.Random.Range(0.0f, 1.0f);
            }
            prob_actions = AIMath.softmax(prob_actions);
            for(int state_id = 0; state_id < RL_Constants.STATE_ID_MAX; ++state_id)
            {
                for(int action_id = 0; action_id < RL_Constants.ACTION_NUM; ++action_id)
                {
                    _table_[state_id, action_id] = 0.0;
                }
            }
        }

        public void updateEnvrionment(vThirdPersonController _cc_, vCamera.vThirdPersonCamera _tpCamera_, Terrain _t_)
        {
            cc = _cc_;
            tpCamera = _tpCamera_;
            t = _t_;
        }

        public void act()
        {
            // TODO
            if(now_action_doing)    return;
            investigateMapInfo();
            //update_state();
            State next_state = state_transition(now_state, before_action);
            QTableUpdate(now_state, before_action);
            now_state = next_state;
            before_action = next_action;
        }

        public State get_state() { return now_state; }

        public double accurate_action(in Action a)
        {
            int stamina = now_state.getStamina();
            Activities kind = a.getAction();
            if(stamina >= 0.7 * RL_Constants.MAX_STAMINA)
            {
                if(kind == Activities.Climb || kind == Activities.Para)   return 1.25;
                return 1.2;
            }
            else if(stamina >= 0.3 * RL_Constants.MAX_STAMINA)
            {
                if(kind == Activities.Climb || kind == Activities.Para)   return 1.05;
                return 1.0;
            }
            if(kind == Activities.Climb || kind == Activities.Para)   return 0.65;
            else if(kind == Activities.Dash) return 0.5;
            return 0.7;
        }

        private float variance(Agent agent)
        {
            float ax = agent.getX(), az = agent.getZ(), ay = agent.getY();
            int cnt = 0;
            float sum = 0.0f;
            foreach(float y in map_info) {
                sum += (y - ay) * (y - ay); // 현재는 높이만, 나중에는 거리에 따라서도 시도 /* TODO */
                ++cnt;
            }
            return sum / (float)cnt;
        }
        private double Reward(Agent agent, State s, Action a)
        {
            return 1.0f / (d * s.getRmndDist()) 
                        - 0.9f * s.getSpendTime() 
                        + 0.7f * accurate_action(a)
                        + 1.0f / AIMath.exp(variance(agent));
        }

        public double Q_value(State state, Action action)
        {
            int s = state.getStateNum();
            int a = (int)action.getAction();
            return _table_[s, a];
        }

        public void QTableUpdate(State state, Action action)
        {
            int s = state.getStateNum();
            int a = (int)action.getAction();
            double max_qtbl = double.MinValue;
            State next_state = state_transition(state, action);
            for(int tmp_action = 0; tmp_action < RL_Constants.ACTION_NUM; ++tmp_action)
            {
                double qa = _table_[next_state.getStateNum(), tmp_action];
                if(qa > max_qtbl)   max_qtbl = qa;
            }
            _table_[s, a] = Reward(agent, state, action) + gamma * max_qtbl;
            now_state = next_state;
        }

        private void Record()
        {
            //Q값, action, state, tau TODO
        }

        private void initialize_state_table()
        {
            // TODO
            int state_id = 1;
            Vector3 dir_vec = cc.transform.position - tpCamera.transform.position;
            dir_vec = dir_vec.normalized;

            var worldPos = cc.transform.position;
            int mapX = (int)(((worldPos.x - t.transform.position.x) / t.terrainData.size.x) * t.terrainData.alphamapWidth);
            int mapZ = (int)(((worldPos.z - t.transform.position.z) / t.terrainData.size.z) * t.terrainData.alphamapHeight);

            float dx = dir_vec.x;
            float dz = dir_vec.z;


        }

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

        private void update_state()
        {
            /* TODO */
            // 이곳에서 주어진 조건 아래 state를 갱신
            // 남은 거리, 지나간 시간, agent의 위치, 맵 정보 등등 활용
        }

        public void investigateMapInfo(){
            Vector3 dir_vec = cc.transform.position - tpCamera.transform.position;
            dir_vec = dir_vec.normalized;
            Vector3 dir_vec_x = AIMath.rotate(1, -45, dir_vec);
            Vector3 dir_vec_z = AIMath.rotate(1, 45, dir_vec);

            var worldPos = cc.transform.position;
            int mapX = (int)(((worldPos.x - t.transform.position.x) / t.terrainData.size.x) * t.terrainData.alphamapWidth);
            int mapZ = (int)(((worldPos.z - t.transform.position.z) / t.terrainData.size.z) * t.terrainData.alphamapHeight);
            float kx = 5f / RL_Constants.xSize;
            float kz = 5f / RL_Constants.zSize;
            //string str_debug = "";

            for(int i = 0; i < RL_Constants.xSize; ++i) {
                for(int j = 0; j < RL_Constants.zSize; ++j) {
                    float dx = mapX + kx * i * dir_vec_x.x + kz * j * dir_vec_z.x;
                    float dz = mapZ + kx * i * dir_vec_x.z + kz * j * dir_vec_z.z;

                    map_info[i,j] = t.terrainData.GetHeight((int)(dx), (int)(dz));
                    //str_debug += heights_at_position[i, j].ToString() + " ";
                }
                //str_debug += "\n";
            }
            //Debug.Log(str_debug);
        }

        //@Env_determine_action
        /*
         * 최댓값이 되는 a를 골라야 함
         * Boltzman approach - https://data-newbie.tistory.com/534
        */
        public Activities determine_action()
        {
            tau *= (float)Math.Pow(learning_rate_tau, lr_exp++);
            for(int i = 0; i < RL_Constants.ACTION_NUM; ++i) {
                prob_actions[i] = getQvalue(i) / tau;
            }
            prob_actions = AIMath.softmax(prob_actions);
            float ticket = UnityEngine.Random.Range(0.0f, 1.0f);
            double sum = 0.0;
            for(int i = 0; i < RL_Constants.ACTION_NUM; ++i) {
                sum += prob_actions[i];
                if(ticket < sum) {
                    return (Activities)(i % RL_Constants.ACTION_NUM);
                }
            }
            return Activities.FF;
        }
        

        public void set_map_info(in float[,] heights_at_position)
        {
            int rows = heights_at_position.GetLength(0);
            int cols = heights_at_position.GetLength(1);
            map_info = new float[rows,cols];
            for(int i = 0; i < rows; ++i) {
                for(int j = 0; j < cols; ++j) {
                    map_info[i,j] = heights_at_position[i,j];
                }
            }
        }

        public float[,] getMapInfo()
        {
            return map_info;
        }

        
    }
}