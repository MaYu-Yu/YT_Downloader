class Circular_Queue:
    def __init__(self, max_size):
        self.max_size = max_size
        self.queue = [None] * max_size
        self.front = 0
        self.rear = 0

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
            self.queue[self.rear] = data
            self.rear = (self.rear + 1) % self.max_size

    def deQueue(self):
        if self.isEmpty():
            print("Queue is Empty")
        else:
            data = self.queue[self.front]
            self.front = (self.front + 1) % self.max_size
            return data

    def display(self):
        if self.isEmpty():
            print("Queue is Empty")
        else:
            print("Queue:", end='{ ')
            current_index = self.front
            while current_index != self.rear:
                print(self.queue[current_index], end=' ')
                current_index = (current_index + 1) % self.max_size
            print("}")
