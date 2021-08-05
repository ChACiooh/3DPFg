namespace _3DPFg
{
    public class Q_table
    {
        private double[][] _table_ = new double[State.STATE_ID_MAX][Action.ACTION_NUM];
        private State now_state;
        private Action before_action;
        private bool now_action_doing = false;
        private double gamma = 0.01;

        public Q_table() {
            //
        }

        private double accurate_action(in Action a)
        {
            int stamina = agent.getStamina();
            int kind = a.getAction();
            if(stamina >= 0.7 * Agent.MAX_STAMINA)
            {
                if(kind == Activities.Climb || kind == Activities.Para)   return 1.25;
                return 1.2;
            }
            else if(stamina >= 0.3 * Agent.MAX_STAMINA)
            {
                if(kind == Activities.Climb || kind == Activities.Para)   return 1.05;
                return 1.0;
            }
            if(kind == Activities.Climb || kind == Activities.Para)   return 0.65;
            else if(kind == Dash) return 0.5;
            return 0.7;
        }

        private double variance(in MapInfo mi)
        {
            double ax = agent.X, az = agent.Z, ay = agent.Y;
            double v = 0.0;
            for(int angle = 0; angle <= 180; ++angle)
            {
                float[] info = mi.getGeometry(ax, az, angle, __k__);   // y값들
                int cnt = 0;
                double sum = 0.0;
                foreach(float y in info) {
                    sum += (y - ay) * (y - ay);
                    ++cnt;
                }
                v += sum / (double)cnt;
            }
            return v;
        }
        public double Reward(State s, Action a)
        {
            return r = 1.0 / (d * s.getRmndDist()) 
                        - p * s.getSpendTime() 
                        + 0.7*accurate_action(a)
                        + variance(env.getMapInfo());
        }

        public double Q_value(State state, Action action)
        {
            int s = state.getStateNum();
            int a = action.getAction();
            return _table_[s][a];
        }

        public void update(State state, Action action)
        {
            int s = state.getStateNum();
            int a = action.getAction();
            double update_value = 1.0;
            double max_qtbl = double.MinValue;
            State next_state = Environment.state_transition(state, action);
            for(int tmp_action = 0; tmp_action < Action.ACTION_NUM; ++tmp_action)
            {
                double qa = _table_[next_state.getStateNum()][tmp_action];
                if(qa > max_qtbl)   max_qtbl = qa;
            }
            _table_[s][a] = Reward(state, action) + gamma * max_qtbl;
        }
    }
}