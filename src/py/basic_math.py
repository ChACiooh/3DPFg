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
