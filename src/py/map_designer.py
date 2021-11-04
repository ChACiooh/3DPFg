from mpl_toolkits.mplot3d import axes3d
import numpy as np
import matplotlib.pyplot as plt
import math
import pickle
import json
import os

# a : tangent of gaussian distribution
# mu : mean, np.array([x, y])
# radius_x : radius of x position of mean point
# radius_y : radius of y position of mean point
# s_2 : variance
def gaussian(map_info, scale, mu, radius_x, radius_y, s_2, bound_x, bound_y):
    centre_x, centre_y = mu[0], mu[1]
    for x in range(centre_x - radius_x, centre_x + radius_x):
        for y in range(centre_y - radius_y, centre_y + radius_y):
            if x < 0 or y < 0 or x >= bound_x or y >= bound_y:
                continue
            X = np.array([x, y])
            g = scale * math.pow(math.e, -np.dot(X - mu, X - mu)/pow(s_2, 2))
            g = g if g <= 20.0 else 20.0
            map_info[x,y] = g
    return map_info

def plt_map_info(map_list, X, Z):
    n = len(map_list)
    for i in range(n):
        print('{}/{}'.format(i+1, n))
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.plot_surface(X, Z, map_list[i])
        ax.set_zlim(-10, 50)

        plt.tight_layout()
        plt.show()
        
        
class MapDesigner:
    def __init__(self, map_path, width=100, height=100):
        self.width = width
        self.height = height
        self.X = np.array([i for i in range(self.width)])
        self.X = np.tile(self.X, (self.height,1))
        self.Z = np.transpose(self.X)
        if map_path[-1] != '\\' and map_path[-1] != '/':
            map_path += '\\'
        
        self.map_path = map_path
        directory = os.listdir(map_path)
        self.map_list = []
        for fname in directory:
            file_name = map_path + fname
            with open(file_name, 'rb') as f:
                map_info = pickle.load(f)
            self.map_list.append(map_info)
        self.loaded = len(self.map_list)
    
    
    def gen_gaussian_map_info(self, n=10, auto_save=True):
        map_info = np.zeros((self.height, self.width),dtype=np.float64)
        x = np.random.randint(1, self.width, n)
        z = np.random.randint(1, self.height, n)
        for mu in zip(x, z):
            radius_x = np.random.randint(10, 30) # 구릉의 반경 x방향
            radius_z = np.random.randint(10, 30) # 구릉의 반경 y방향
            s_2 = np.random.rand() + np.random.randint(8, 13) # variance. 크기가 클수록 넓은 범위가 됨
            # print(s_2)
            map_info = gaussian(map_info, 30, np.array(mu), radius_x, radius_z, s_2, self.width, self.height) # 20 : 최대 높이
            
        if auto_save == True:
            self.map_list.append(map_info)
        return map_info

    
    def plot(self, n=1):
        plt_map_info(self.map_list[:n], self.X, self.Z)
        
    def save(self, type='pickle'):
        if type == 'pickle':
            for i in range(self.loaded, len(self.map_list)):
                file_name = self.map_path + f'map_info_{i+1}.pkl'
                with open(file_name, 'wb') as f:
                    pickle.dump(self.map_list[i], f)
        elif type == 'json':
            map_path = 'json/maps/'
            for i in range(0, len(self.map_list)):
                file_name = map_path + f'map_info_{i+1}.json'
                with open(file_name, 'w', encoding='utf-8') as f:
                    sub_map = []
                    for row in self.map_list[i]:
                        row = list(row)
                        sub_map.append(row)
                    json.dump(sub_map, f, ensure_ascii=False, indent='\t')
        else:
            print('Error: type parameter was wrong.')
