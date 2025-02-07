class PhoneEntry:
    def __init__(self, name, number):
        self.name = name
        self.number = number

class ChainedHashTable:
    def __init__(self, size):
        self.size = size
        self.table = [[] for _ in range(size)]
        self.comparisons = 0
    
    def hash_function(self, name):
        return sum(ord(c) for c in name) % self.size
    
    def insert(self, name, number):
        index = self.hash_function(name)
        self.table[index].append(PhoneEntry(name, number))
    
    def search(self, name):
        self.comparisons = 0
        index = self.hash_function(name)
        
        for entry in self.table[index]:
            self.comparisons += 1
            if entry.name == name:
                return entry.number
        return None

class LinearProbingHashTable:
    def __init__(self, size):
        self.size = size
        self.table = [None] * size
        self.comparisons = 0
    
    def hash_function(self, name):
        return sum(ord(c) for c in name) % self.size
    
    def insert(self, name, number):
        index = self.hash_function(name)
        
        while self.table[index] is not None:
            index = (index + 1) % self.size
            
        self.table[index] = PhoneEntry(name, number)
    
    def search(self, name):
        self.comparisons = 0
        index = self.hash_function(name)
        
        while self.table[index] is not None:
            self.comparisons += 1
            if self.table[index].name == name:
                return self.table[index].number
            index = (index + 1) % self.size

            if index == self.hash_function(name):
                break
                
        return None

size = int(input("Enter the size of table:"))
chained_table = ChainedHashTable(size)
linear_table = LinearProbingHashTable(size)

for _ in range(size):
    name = input("Enter name:")
    phone_no = input("Enter Phone Number:")
    chained_table.insert(name , phone_no)
    linear_table.insert(name , phone_no)

search = input("Enter name to search phone number:")
chained_result = chained_table.search(search)
linear_result = linear_table.search(search)

if chained_result:
    print("Chained Hash Table:", chained_result, "(Comparisons:", chained_table.comparisons, ")")
else:
    print("Chained Hash Table: Not Found")

if linear_result:
    print("Linear Probing:", linear_result, "(Comparisons:", linear_table.comparisons, ")")
else:
    print("Linear Probing: Not Found")