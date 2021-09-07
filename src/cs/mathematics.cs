using System;
using System.Collections.Generic;
using UnityEditor;
using UnityEngine;
using UnityEngine.Events;
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

        public static Vector3 rotate(int axis, double angle, Vector3 vec)
        {
            angle = angle / 180 * Math.PI;
            float x,y,z;
            float[,] rotate_matrix = new float[3,3];
            float cosa = (float)Math.Cos(angle), sina = (float)Math.Sin(angle);
            if(axis == 0) // x-axis
            {
                rotate_matrix[0,0] = 1.0f;
                rotate_matrix[1,1] = rotate_matrix[2,2] = cosa;
                rotate_matrix[1,2] = sina;
                rotate_matrix[2,1] = -sina;
            }
            else if(axis == 1) // y-axis
            {
                rotate_matrix[1, 1] = 1.0f;
                rotate_matrix[0,0] = rotate_matrix[2,2] = cosa;
                rotate_matrix[0,2] = -sina;
                rotate_matrix[2,0] = sina;
            }
            else if(axis == 2) // z-axis
            {
                rotate_matrix[2, 2] = 1.0f;
                rotate_matrix[1,1] = rotate_matrix[0,0] = cosa;
                rotate_matrix[0,1] = sina;
                rotate_matrix[1,0] = -sina;
            }
            Vector3[] vectors = new Vector3[3];
            for(int i = 0; i < 3; ++i) {
                for(int j = 0; j < 3; ++j) {
                    vectors[i][j] = rotate_matrix[i, j];
                }
                // vectors[i].x = rotate_matrix[i, 0];
                // vectors[i].y = rotate_matrix[i, 1];
                // vectors[i].z = rotate_matrix[i, 2];
            }
            x = Vector3.Dot(vectors[0], vec);
            y = Vector3.Dot(vectors[1], vec);
            z = Vector3.Dot(vectors[2], vec);
            vec[0] = x;
            vec[1] = y;
            vec[2] = z;
            return vec; 
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