#include <iostream>
#include <string>

using namespace std;

template <typename T>
struct PQItem {
    T data;
    int priority;
    PQItem* next;

    bool operator<=(const PQItem& other) const {
        return priority <= other.priority; 
    }
};

template <typename T>
class PriorityQueue {
private:
    PQItem<T>* front;

public:
    PriorityQueue() {
        front = nullptr; 
    }

    void enqueue(const T& item, int priority) {
        PQItem<T>* newItem = new PQItem<T>{ item, priority, nullptr };
        if (front == nullptr || newItem <= *front) {
            newItem->next = front;
            front = newItem;
        } else {
            PQItem<T>* current = front;
            while (current->next != nullptr && *(current->next) <= *newItem) {
                current = current->next;
            }
            newItem->next = current->next;
            current->next = newItem;
        }
        cout << "Item enqueued: " << item << " with priority: " << priority << endl;
    }

    void dequeue() {
        if (front == nullptr) {
            cout << "Priority Queue is empty!" << endl;
            return;
        }
        PQItem<T>* temp = front;
        front = front->next;
        cout << "Item dequeued: " << temp->data << " with priority: " << temp->priority << endl;
        delete temp;
    }

    void display() const {
        if (front == nullptr) {
            cout << "Priority Queue is empty." << endl;
            return;
        }
        PQItem<T>* current = front;
        cout << "Items in Priority Queue:" << endl;
        while (current != nullptr) {
            cout << "Item: " << current->data << ", Priority: " << current->priority << endl;
            current = current->next;
        }
    }

    ~PriorityQueue() {
        while (front != nullptr) {
            dequeue();
        }
    }
};

int main() {
    PriorityQueue<string> pq;

    int choice, priority;
    string item;

    do {
        cout << "\n1. Enqueue Item\n2. Dequeue Item\n3. Display Items\n4. Exit\n";
        cout << "Enter your choice: ";
        cin >> choice;

        switch (choice) {
            case 1:
                cout << "Enter Item: ";
                cin >> item;
                cout << "Enter Priority: ";
                cin >> priority;
                pq.enqueue(item, priority);
                break;
            case 2:
                pq.dequeue();
                break;
            case 3:
                pq.display();
                break;
            case 4:
                cout << "Exiting program." << endl;
                break;
            default:
                cout << "Invalid choice. Please try again." << endl;
        }
    } while (choice != 4);

    return 0;
}
