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
        private float[,] map_info = null;
        private Agent agent;
        private float tau = 1.0f;
        private double[] prob_actions;
        private double[,] _table_;
        private State now_state;
        private Action before_action;
        private bool now_action_doing = false;
        private double gamma = 0.01;    // need to fine-tune
        private int d = 10000;
        private float p = 0.9f;


        public Environment() 
        {
            agent = new Agent();
            _table_  = new double[RL_Constants.STATE_ID_MAX, RL_Constants.ACTION_NUM];
            map_info = new float[RL_Constants.xSize, RL_Constants.zSize];
            reset();
            tau = 1.0f;
            prob_actions = new double[RL_Constants.ACTION_NUM];
            for(int i = 0; i < RL_Constants.ACTION_NUM; ++i) {
                prob_actions[i] = UnityEngine.Random.Range(0.0f, 1.0f);
            }
            prob_actions = AIMath.softmax(prob_actions);
        }

        
        public double getQvalue(in int action_id)
        {
            return _table_[now_state.getStateNum(), action_id];
        }

        public void reset() {
            for(int state_id = 0; state_id < RL_Constants.STATE_ID_MAX; ++state_id)
            {
                for(int action_id = 0; action_id < RL_Constants.ACTION_NUM; ++action_id)
                {
                    _table_[state_id, action_id] = 0.0;
                }
            }
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
                        - p * s.getSpendTime() 
                        + 0.7f * accurate_action(a)
                        + variance(agent);
        }

        public double Q_value(State state, Action action)
        {
            int s = state.getStateNum();
            int a = (int)action.getAction();
            return _table_[s, a];
        }

        public void update(State state, Action action)
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
        }

        private State state_transition(State state, Action action)
        {
            State next_state = new State();
            /* TODO */
            return next_state;
        }

        public void update_state(State next_state)
        {
            now_state.update(next_state);
        }

        public void setHeights(vThirdPersonController cc, vCamera.vThirdPersonCamera tpCamera, Terrain t){
            Vector3 dir_vec = cc.transform.position - tpCamera.transform.position;
            dir_vec = dir_vec.normalized;

            var worldPos = cc.transform.position;
            int mapX = (int)(((worldPos.x - t.transform.position.x) / t.terrainData.size.x) * t.terrainData.alphamapWidth);
            int mapZ = (int)(((worldPos.z - t.transform.position.z) / t.terrainData.size.z) * t.terrainData.alphamapHeight);
            float dx = 5f/10f/dir_vec.x, dz = 5f/10f/dir_vec.z;
            //string str_debug = "";

            for(int i = 0; i < RL_Constants.xSize; ++i) {
                for(int j = 0; j < RL_Constants.zSize; ++j) {
                    map_info[i,j] = t.terrainData.GetHeight((int)(mapX + i * dx), (int)(mapZ + j * dz));
                    //str_debug += heights_at_position[i, j].ToString() + " ";
                }
                //str_debug += "\n";
            }
            //Debug.Log(str_debug);
        }

        public int run() {
            State now_state = get_state();
            if(now_state.getStateNum() == RL_Constants.DEATH_STATE)  return 0;
            // do something (TODO)
            Action next_action = new Action();/*env로부터 가장 높은 확률을 가진 action 고르기 */
            update(now_state, next_action);
            update_state(state_transition(now_state, next_action));
            now_action_doing = false;
            before_action = next_action;
            return 1;
        }

        public ref Agent getAgent() { return ref agent; }

        //@Env_determine_action
        /*
         * 최댓값이 되는 a를 골라야 함
         * Boltzman approach - https://data-newbie.tistory.com/534
        */
        public int determine_action(float _tau_)
        {
            tau = _tau_;
            for(int i = 0; i < RL_Constants.ACTION_NUM; ++i) {
                prob_actions[i] = getQvalue(i) / tau;
            }
            prob_actions = AIMath.softmax(prob_actions);
            float ticket = UnityEngine.Random.Range(0.0f, 1.0f);
            double sum = 0.0;
            for(int i = 0; i < RL_Constants.ACTION_NUM; ++i) {
                sum += prob_actions[i];
                if(ticket < sum) {
                    return i;
                }
            }
            return RL_Constants.ACTION_NUM - 1;
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