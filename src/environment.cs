namespace _3DPFg
{
    using System;
    public class Environment
    {
        private float[,] map_info;
        private Agent agent;
        private Q_table q_Table;
        private float tau = 1.0;
        private double[] prob_actions;
        public static Random rand;
        public Environment() 
        {
            agent = new Agent();
            q_Table = new Q_table();
            tau = 1.0;
            rand = new Random();
            prob_actions = new double[Action.ACTION_NUM];
            for(int i = 0; i < Action.ACTION_NUM; ++i) {
                prob_actions[i] = rand.Sample();
            }
            prob_actions = AIMath.softmax(prob_actions, Action.ACTION_NUM);
        }

        public int run() {
            State now_state = q_Table.get_state();
            if(now_state.getStateNum() == State.DEATH_STATE)  return 0;
            // do something (TODO)
            Action next_action = /*env로부터 가장 높은 확률을 가진 action 고르기 */
            q_table.update(now_state, next_action);
            q_table.update_state(Environment.state_transition(now_state, next_action));
            now_action_doing = /*TODO*/
            before_action = next_action;
            return 1;
        }

        //@Env_determine_action
        /*
         * 최댓값이 되는 a를 골라야 함
         * Boltzman approach - https://data-newbie.tistory.com/534
        */
        public int determine_action(float _tau_)
        {
            tau = _tau_;
            float sum = 0.0f;
            for(int i = 0; i < Action.ACTION_NUM; ++i) {
                prob_actions[i] = q_Table.getQvalue(i) / tau;
            }
            prob_actions = AIMath.softmax(prob_actions);
            float ticket = rand.Sample();
            for(int i = 0, sum = 0.0f; i < Action.ACTION_NUM; ++i) {
                sum += prob_actions[i];
                if(ticket < sum) {
                    return i;
                }
            }
            return Action.ACTION_NUM - 1;
        }
        public static State state_transition(State state, Action action)
        {
            State next_state = new State(state);
            // TODO 
            // after interact between action and state,
            // make corresponding next state and return it.
            // How to define state table:
            // There are variables that affects state condition e.g. stamina, map_info in front of an agent.
            // 
            return next_state;
        }

        public void set_map_info(in float[,] heigts_at_position)
        {
            map_info = new float[,](heigts_at_position);
        }
    }
}