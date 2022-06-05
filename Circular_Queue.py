class Circular_Queue:
    def __init__(self, max_size) -> None:
        self.max_size = max_size
        self.queue = [None] * max_size
        self.front = max_size-1
        self.rear = max_size-1
    def isEmpty(self):
        return self.front == self.rear
    def isFull(self):
        return (self.rear + 1) % self.max_size == self.front
    def get_length(self):
        return (self.rear - self.front + self.max_size) % self.max_size
    def enQueue(self, data):
        if self.isFull():
            print("Queue is Full")
        else:
            self.rear = (self.rear + 1) % self.max_size
            self.queue[self.rear] = data
    def deQueue(self):
        if self.isEmpty():
            print("Queue is Empty")
        else:
            self.front = (self.front + 1) % self.max_size
            return self.queue[self.front]
    def display(self):
        print("Queue:", end='{ ')
        f = self.front
        r = self.rear
        while f != r:
            f = (f + 1) % self.max_size
            print(self.queue[f], end = ' ')
        print("}")