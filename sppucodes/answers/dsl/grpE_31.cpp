#include <iostream>
#include <stdexcept>

using namespace std;

class Deque {
private:
    int* arr;
    int capacity;
    int front;
    int rear;
    int size;

public:
    Deque(int cap) {
        capacity = cap;
        arr = new int[capacity];
        front = -1;
        rear = 0;
        size = 0;
    }

    ~Deque() {
        delete[] arr;
    }

    void addFront(int x) {
        if (size == capacity) {
            throw overflow_error("Deque is full");
        }
        front = (front + 1) % capacity;
        arr[front] = x;
        size++;
        if (size == 1) {
            rear = front;
        }
    }

    void addRear(int x) {
        if (size == capacity) {
            throw overflow_error("Deque is full");
        }
        rear = (rear - 1 + capacity) % capacity;
        arr[rear] = x;
        size++;
        if (size == 1) {
            front = rear;
        }
    }

    void deleteFront() {
        if (size == 0) {
            throw underflow_error("Deque is empty");
        }
        front = (front - 1 + capacity) % capacity;
        size--;
        if (size == 0) {
            front = -1;
            rear = 0;
        }
    }

    void deleteRear() {
        if (size == 0) {
            throw underflow_error("Deque is empty");
        }
        rear = (rear + 1) % capacity;
        size--;
        if (size == 0) {
            front = -1;
            rear = 0;
        }
    }

    void display() const {
        if (size == 0) {
            cout << "Deque is empty." << endl;
            return;
        }
        cout << "Elements in Deque: ";
        for (int i = 0; i < size; i++) {
            cout << arr[(rear + i) % capacity] << " ";
        }
        cout << endl;
    }
};

int main() {
    int capacity;
    cout << "Enter the capacity of the Deque: ";
    cin >> capacity;
    Deque deque(capacity);

    int choice, value;

    do {
        cout << "\n1. Add to Front\n2. Add to Rear\n3. Delete from Front\n4. Delete from Rear\n5. Display\n6. Exit\n";
        cout << "Enter your choice: ";
        cin >> choice;

        switch (choice) {
            case 1:
                cout << "Enter value to add to front: ";
                cin >> value;
                try {
                    deque.addFront(value);
                } catch (const overflow_error& e) {
                    cout << e.what() << endl;
                }
                break;
            case 2:
                cout << "Enter value to add to rear: ";
                cin >> value;
                try {
                    deque.addRear(value);
                } catch (const overflow_error& e) {
                    cout << e.what() << endl;
                }
                break;
            case 3:
                try {
                    deque.deleteFront();
                } catch (const underflow_error& e) {
                    cout << e.what() << endl;
                }
                break;
            case 4:
                try {
                    deque.deleteRear();
                } catch (const underflow_error& e) {
                    cout << e.what() << endl;
                }
                break;
            case 5:
                deque.display();
                break;
            case 6:
                cout << "Exiting program." << endl;
                break;
            default:
                cout << "Invalid choice. Please try again." << endl;
        }
    } while (choice != 6);

    return 0;
}
