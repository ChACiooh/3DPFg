class Stack:
    def __init__(self):
        self.stock_ = []
        self.amount_ = 0
        
    def push(self, item):
        if len(self.stock_) == self.amount_:
            self.stock_.append(item)
        else:
            self.stock_[self.amount_] = item
        self.amount_ += 1
        
    def pop(self):
        if self.amount_ <= 0:
            return
        self.amount_ -= 1
        
    def top(self):
        if self.amount_ <= 0:
            return None
        return self.stock_[-1]
        
    def size(self):
        return self.amount_
    
    def clear(self):
        self.stock_ = []
        self.amount_ = 0
    
    def getTotal(self):
        return self.stock_[:self.amount_]   # auto copy