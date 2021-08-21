namespace Invector.vCharacterController
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
        private Activities action_id; // follows Activities
        public Action() { action_id = Activities.Wait; }
        public Action(int next_action_id)
        {
            action_id = (Activities)(next_action_id % RL_Constants.ACTION_NUM);
        }
        
        /* components */
        public Activities getAction()
        {
            return action_id;
        }
        public void set_action(Activities activity)
        {
            action_id = activity;
        }
        // public int wait();         // 0
        // public int running();      // 1
        // public int jump();         // 2
        // public int dash();         // 3
        // public int paragliding();  // 4
        // public int climbing();     // 5
        // public int freefall();     // 6
    }
}
