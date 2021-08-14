namespace _3DPFg
{
    public class Q_table
    {
        private double[][] _table_ = new double[State.STATE_ID_MAX][Action.ACTION_NUM];
        private State now_state;
        private Action before_action;
        private bool now_action_doing = false;
        private double gamma = 0.01;    // need to fine-tune

        public Q_table() {
            reset();
        }

        
        public double getQvalue(in int action_id)
        {
            return _table_[now_state.getStateNum][action_id];
        }

        public void reset() {
            for(int state_id = 0; state_id < State.STATE_ID_MAX; ++state_id)
            {
                for(int action_id = 0; action_id < Action.ACTION_NUM; ++action_id)
                {
                    _table_[state_id][action_id] = 0.0;
                }
            }
        }

        public State get_state() { return now_state; }

        public double accurate_action(in Action a)
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

        private float variance(in float[,] map_info)
        {
            float ax = agent.X, az = agent.Z, ay = agent.Y;
            float[,] info = mi.getGeometry(ax, az, angle, __k__);   // y값들
            int cnt = 0;
            float sum = 0.0;
            foreach(float[] ys in info) {
                foreach(float y in ys) {
                    sum += (y - ay) * (y - ay);
                    ++cnt;
                }
            }
            return sum / (float)cnt;
        }
        private double Reward(State s, Action a)
        {
            return r = 1.0 / (d * s.getRmndDist()) 
                        - p * s.getSpendTime() 
                        + 0.7 * accurate_action(a)
                        + variance(env.getMapInfo());
        }

        public double Q_value(State state, Action action)
        {
            int s = state.getStateNum();
            int a = action.getAction();
            return _table_[s][a];
        }

        public void update(int state, Action action)
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

        public void update_state(State next_state)
        {
            now_state.update(next_state);
        }
    }
}