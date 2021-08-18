namespace Invector.vCharacterController
{
    public class Agent
    {
        private Action a_action;
        private State state;
        private float x, y, z;

        public Agent() 
        {
            state = new State();
        }
        public void updateAction(Action na)
        {
            a_action = na;
        }

        public void updateLoc(float _x_, float _y_, float _z_)
        {
            x = _x_;
            y = _y_;
            z = _z_;
        }

        public float getX() { return x; }
        public float getY() { return y; }
        public float getZ() { return z; }
    }
}
