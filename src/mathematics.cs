namespace _3DPFg
{
    using System;
    using System.Collections.Generic;
    using System.Linq;
    public class AIMath
    {
        public AIMath() {}

        public static double exp(double x) {
            return Math.Pow(Math.E, x);
        }
        public static double sigmoid(double x) {
            return 1.0 / (1 + exp(x));
        }

        public static double Relu(double x) {
            if(x < 0)   return 0.0;
            return x;
        }

        public static double[] softmax(double[] x, int n)
        {
            double sum = elems => {
                double res = 0.0;
                foreach(double elem in elems) {
                    res += elem;
                }
                return res;
            };
            return x.Select(x => Math.Pow(Math.E, x) / sum(x));
        }
    }
}