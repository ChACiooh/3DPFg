import numpy as np
import math

def rotate_matrix(angle):
    R_matrix = np.array([[np.cos(angle), 0., np.sin(angle)],
                         [0., 1., 0.],
                         [-np.sin(angle), 0., np.cos(angle)]])

    return R_matrix

def vector_size(vec):
    return math.sqrt(np.dot(vec, vec))

def norm(vec):
    _size_ = vector_size(vec)
    return vec / _size_ if _size_ != 0 else np.array([0., 0., 0.])

def EuclideanDistance(pos1, pos2):
    pos3 = pos2 - pos1
    return math.sqrt(np.dot(pos3, pos3))

def convert_vector(dir_vec, siz_vec):
    return dir_vec * vector_size(siz_vec)

def sigmoid(x):
    return 1 / (1 + math.exp(-x))

def softmax(p):
    # given vector p into normalized with softmax
    sum = np.sum([math.exp(i) for i in p])
    return np.array([ math.exp(j) / sum for j in p ])

def round(n, maximum=70) -> int:
    for i in range(1, maximum):
        if n-i >= -0.5 and n-i < 0.5:
            return i
    return 0

def interpolate(pos1:np.ndarray, pos2:np.ndarray, a, b):
    if a + b == 0:
        return pos1
    return (a*pos2 + b*pos1) / (a+b)