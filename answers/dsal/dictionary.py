class Node:
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.next = None


class HashTable:
    def __init__(self, size):
        self.size = size
        self.table = [None] * self.size

    def hash(self, key):
        return hash(key) % self.size

    def insert(self, key, value):
        index = self.hash(key)
        new_node = Node(key, value)

        if self.table[index] is None:
            self.table[index] = new_node
        else:
            current = self.table[index]
            while current:
                if current.key == key:
                    current.value = value
                    return
                if current.next is None:
                    break
                current = current.next
            current.next = new_node

    def find(self, key):
        index = self.hash(key)
        current = self.table[index]

        while current:
            if current.key == key:
                return current.value
            current = current.next

        return None

    def delete(self, key):
        index = self.hash(key)
        current = self.table[index]
        prev = None

        while current:
            if current.key == key:
                if prev:
                    prev.next = current.next
                else:
                    self.table[index] = current.next
                return True
            prev = current
            current = current.next

        return False


size = int(input("Enter the size of the hash table: "))
ht = HashTable(size)

while True:
    print("\nChoose an operation:")
    print("1. Insert (key, value)")
    print("2. Find (key)")
    print("3. Delete (key)")
    print("4. Exit")

    choice = input("Enter your choice: ")

    if choice == "1":
        key = input("Enter key: ")
        value = input("Enter value: ")
        ht.insert(key, value)
        print(f"Inserted ({key}, {value})")

    elif choice == "2":
        key = input("Enter key to find: ")
        result = ht.find(key)
        if result:
            print("Value:", result)
        else:
            print("No key found")

    elif choice == "3":
        key = input("Enter key to delete: ")
        if ht.delete(key):
            print("Deleted")
        else:
            print("Key Not Found")

    elif choice == "4":
        print("Exiting...")
        break

    else:
        print("Invalid choice! Enter a number between 1 and 4.")
