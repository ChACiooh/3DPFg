namespace _3DPFg
{
    public class Q_function
    {
        /* TODO */
    }
    public class RL
    {
        private State state;
        private Agent agent;
        private Action action;
        private Environment env;

        /* TODO : 지형 정보는 float */

        /* constants */
        private static const double d = 10.0;
        private static const double p = 0.005;
        private static const int __k__ = 5;
        public RL()
        {
            state = new State();
            agent = new Agent();
            action = new Action();
            env = new Environment();
        }
        public RL(State s, Agent a, Action ac, Environment _env_)
        {
            state = new State(s);
            agent = new Agent(a);
            action = new Action(ac);
            env = new Environment(_env_);
        } 

        private double accurate_action(in Action a)
        {
            int stamina = agent.getStamina();
            int kind = a.kind();
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
    }
}