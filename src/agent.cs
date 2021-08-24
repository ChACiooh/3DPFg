using System.Collections;
using UnityEditor;
using UnityEngine;
using UnityEngine.Events;
using System.Collections.Generic;
using System;

namespace Invector.vCharacterController
{
    public class Agent
    {
        private Action a_action;
        private float x, y, z;
        private float speed;
        private Vector3 direction;

        public Agent() 
        {
            speed = 0.0f;
        }
        public void updateAction(Action na)
        {
            a_action = na;
        }

        public void updateSpeed(float _speed_) { speed = _speed_; }
        public float getSpeed() { return speed; }
        public Vector3 getDirection() { return direction; }
        public void setDirection(Vector3 new_vec)
        {
            direction = new_vec;
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
