namespace _3DPFg
{
    public class State
    {
        public static int STATE_ID_MAX = 3000;
        public static const int MAX_STAMINA = 100;
        private int stamina;
        private double remained_distance;
        private double spend_time;
        private int state_num;  // 7 * 8 * MAX_STAMINA의 종류만큼 있다. 

        /* 주변 지형 정보를 저장할 구조체 또는 class 필요
         * 이 부분은 협업으로 정의할 필요가 있음
         */

        public State() 
        {
            stamina = MAX_STAMINA;
        }
        public State(State s)
        {
            this.stamina = s.stamina;
            this.remained_distance = s.remained_distance;
            this.spend_time = s.spend_time;
        }
        public void updateSurround(/* . . .*/)
        {
            // TODO
        }
        public int getStateNum() {
            return state_num;
        }
        public void update();

        public double getSpendTime() { return spend_time; }
        public double getRmndDist() { return remained_distance; }
    }
}
