namespace _3DPFg
{
    public enum Activities
    {
        Wait,
        Run,
        Jump,
        Dash,
        Para,
        Climb,
        FF
    }
    public class Action
    {
        private int action_id = -1; // follows Activities

        public Action() {}
        
        /* components */
        public int kind()
        {
            return action_id;
        }
        public int wait();         // 0
        public int running();      // 1
        public int jump();         // 2
        public int dash();         // 3
        public int paragliding();  // 4
        public int climbing();     // 5
        public int freefall();     // 6
    }
}
