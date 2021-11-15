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
        self.stock_ = self.stock_[:self.amount_]
        
    def top(self):
        if self.amount_ <= 0:
            return None
        return self.stock_[-1]
        
    def size(self):
        return self.amount_
    
    def clear(self):
        self.stock_ = []
        self.amount_ = 0
    
    def getTotal(self, n=-1) -> list:
        if n != -1:
            return self.stock_[:n]
        return self.stock_[:self.amount_]   # auto copy