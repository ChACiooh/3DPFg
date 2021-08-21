namespace Invector.vCharacterController
{
    public class State
    {
        private int stamina; 
        private double remained_distance;
        private double spend_time;
        private int state_num;  // 7 * 8 * MAX_STAMINA의 종류만큼 있다. 

        public State() 
        {
            stamina = RL_Constants.MAX_STAMINA;
            spend_time = 0;
            state_num = 0;  // generated
        }
        public State(State s)
        {
            this.stamina = s.stamina;
            this.remained_distance = s.remained_distance;
            this.spend_time = s.spend_time;
        }
        public int getStateNum() {
            return state_num;
        } 
        public void update(in State next_state) 
        {
            stamina = next_state.stamina;
            remained_distance = next_state.remained_distance;
            spend_time = next_state.spend_time;
            state_num = next_state.state_num;
        }

        public int getStamina() { return stamina; }
        public double getSpendTime() { return spend_time; }
        public double getRmndDist() { return remained_distance; }
    }
}
