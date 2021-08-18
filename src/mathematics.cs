using System;
using System.Collections.Generic;
using System.Linq;

namespace Invector.vCharacterController
{
    public static class RL_Constants {
        public const int MAX_STAMINA = 100;
        public const int STATE_ID_MAX = 5601;   // MAX_STAMINA * 7 * 8 + 1(Death state1)
        public const int DEATH_STATE = 0;
        public const int ACTION_NUM = 7;
        public const int xSize = 10, zSize = 10;
    }

    public static class AIMath
    {
        public static double exp(double x) {
            return Math.Pow(Math.E, x);
        }
        public static double sigmoid(double x) {
            return 1.0 / (1 + exp(x));
        }

        public static double Relu(double x) {
            return x < 0.0 ? 0.0 : x;
        }

        public static double[] softmax(double[] x)
        {
            double fraction = 0.0;
            int n = x.GetLength(0);
            foreach(double x_Unit in x) {
                fraction += exp(x_Unit);
            }
            for(int i = 0; i < n; ++i) {
                x[i] = exp(x[i]) / fraction;
            }
            return x;
        }
    }
}