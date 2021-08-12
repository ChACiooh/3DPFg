namespace _3DPFg
{
    public class MapInfo
    {
        public MapInfo() {}

        float[][] getHeights()
        {
            /* TODO */
        }
    }
    
    public class Environment
    {
        private double[][] map_info;
        private Agent agent;
        private Q_table q_Table;
        private double epsilon = 1.0;
        public Environment() 
        {
            agent = new Agent();
            tau = 1.0;
        }

        //@Env_determine_action
        /*
         * 최댓값이 되는 a를 골라야 함
         *
        */
        public int determine_action()
        {
            double max_qtbl = double.MinValue;
            int argmax_a = Wait;
            for(int a = Wait; a <= FF; ++a)
            {
                double q_val = q_Table.getQvalue(a);
                if(max_qtbl < q_val) {
                    max_qtbl = q_val;
                    argmax_a = a;
                }
            }
            int I_val = q_Table.accurate_action(argmax_a) > 0.7 ? 1 : 0;
            // TODO 확률을 어떻게 해야
        }
        public static State state_transition(State state, Action action)
        {
            State next_state = new State(state);
            // TODO 
            // after interact between action and state,
            // make corresponding next state and return it.

            return next_state;
        }
    }
}