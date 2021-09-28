import numpy as np

class Action:
    def __init__(self, acting_time, action_id, veclocity, stamina_consume=-4.8, input_key=None):
        self.acting_time = acting_time
        self.base_acting_time = 1.3
        self.id = action_id
        self.input_key = input_key
        self.velocity = veclocity # numpy array vector
        self.stamina_consume = stamina_consume
        
        
    def action_update(self, action_id, input_key, agent_dir):
        self.id = action_id
        self.input_key = input_key
        if self.id == 'Wait':
            self.velocity = np.array([0., 0., 0.])
            self.acting_time = self.base_acting_time
        elif self.id == 'W':
            self.velocity = 4 * agent_dir
            self.acting_time = self.base_acting_time
        elif self.id == 'A':
            self.acting_time = self.base_acting_time
            agent_dir = np.array([[0., -1.],
                                  [1., 0.]]) * agent_dir
            self.velocity = 4 * agent_dir
        elif self.id == 'S':
            self.acting_time = self.base_acting_time
            agent_dir = -1 * agent_dir
            self.velocity = 4 * agent_dir
        elif self.id == 'D':
            self.acting_time = self.base_acting_time
            agent_dir = np.array([[0., 1.],
                                  [-1., 0.]]) * agent_dir
            self.velocity = 4 * agent_dir
        elif self.id == 'WA':
            self.acting_time = self.base_acting_time
            rotate_angle = np.pi/4
            agent_dir = np.array([[np.cos(rotate_angle), -np.sin(rotate_angle)],
                                  [np.sin(rotate_angle), np.cos(rotate_angle)]]) * agent_dir
            self.velocity = 4 * agent_dir
        elif self.id == 'WD':
            self.acting_time = self.base_acting_time
            rotate_angle = -np.pi/4
            agent_dir = np.array([[np.cos(rotate_angle), -np.sin(rotate_angle)],
                                  [np.sin(rotate_angle), np.cos(rotate_angle)]]) * agent_dir
            self.velocity = 4 * agent_dir
        elif self.id == 'SD':
            self.acting_time = self.base_acting_time
            rotate_angle = -3*np.pi/4
            agent_dir = np.array([[np.cos(rotate_angle), -np.sin(rotate_angle)],
                                  [np.sin(rotate_angle), np.cos(rotate_angle)]]) * agent_dir
            self.velocity = 4 * agent_dir
        elif self.id == 'SA':
            self.acting_time = self.base_acting_time
            rotate_angle = 3*np.pi/4
            agent_dir = np.array([[np.cos(rotate_angle), -np.sin(rotate_angle)],
                                  [np.sin(rotate_angle), np.cos(rotate_angle)]]) * agent_dir
            self.velocity = 4 * agent_dir
        elif self.id == 'Ws':
            self.velocity = 6 * agent_dir
            self.acting_time = self.base_acting_time
            self.stamina_consume = 20
        elif self.id == 'As':
        elif self.id == 'Ss':
        elif self.id == 'Ds':
        elif self.id == 'WAs':
        elif self.id == 'WDs':
        elif self.id == 'SDs':
        elif self.id == 'SAs':
        elif self.id == 'Wj':
        elif self.id == 'Aj':
        elif self.id == 'Sj':
        elif self.id == 'Dj':
        elif self.id == 'WAj':
        elif self.id == 'WDj':
        elif self.id == 'SDj':
        elif self.id == 'SAj':
        elif self.id == 'Wsj':
        elif self.id == 'Asj':
        elif self.id == 'Ssj':
        elif self.id == 'Dsj':
        elif self.id == 'WAsj':
        elif self.id == 'WDsj':
        elif self.id == 'SDsj':
        elif self.id == 'SAsj':
            
        return agent_dir
        