#include <iostream>
#include <vector>
using namespace std;

// Function to insert into Min Heap
void minInsert(vector<int>& heap, int i) {
    int current = i;
    int parent = (current - 1) / 2;

    while (parent >= 0 && heap[parent] > heap[current]) {
        swap(heap[parent], heap[current]);
        current = parent;
        parent = (current - 1) / 2;
    }
}

// Function to insert into Max Heap
void maxInsert(vector<int>& heap, int i) {
    int current = i;
    int parent = (current - 1) / 2;

    while (parent >= 0 && heap[parent] < heap[current]) {
        swap(heap[parent], heap[current]);
        current = parent;
        parent = (current - 1) / 2;
    }
}

int main() {
    int n;
    cout << "Enter the number of students: ";
    cin >> n;

    vector<int> marks(n);
    cout << "Enter the marks obtained by the students:\n";
    for (int i = 0; i < n; i++) {
        cin >> marks[i];
    }

    // Build Min Heap
    vector<int> minHeap = marks;
    for (int i = 1; i < n; i++) {
        minInsert(minHeap, i);
    }

    // Build Max Heap
    vector<int> maxHeap = marks;
    for (int i = 1; i < n; i++) {
        maxInsert(maxHeap, i);
    }

    cout << "Minimum marks obtained: " << minHeap[0] << endl;
    cout << "Maximum marks obtained: " << maxHeap[0] << endl;

    return 0;
}
