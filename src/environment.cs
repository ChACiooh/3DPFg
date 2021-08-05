namespace _3DPFg
{
    public struct MapInfo
    {
        //
    }
    
    public class Environment
    {
        private double[][] map_info;
        private Agent agent;
        private Q_table q_Table;
        private double tau = 1.0;
        public Environment() 
        {
            agent = new Agent();
            tau = 1.0;
        }

        //@Env_determine_action
        public void determine_action(State state, Action action)
        {
            double p = AIMath.exp(q_Table.Q_value(state, action) / tau);
            double q = 0.0;
            for(int a = 0; a < Action.ACTION_NUM; ++a) {
                q += AIMath.exp(q_Table.Q_value(state, a) / tau);
            }
            return p / q;
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