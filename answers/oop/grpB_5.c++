#include <iostream>
using namespace std;

template <typename T>
void SelectionSort(T arr[], int size) {
    for (int i = 0; i < size - 1; i++) {
        int minIndex = i;
        for (int j = i + 1; j < size; j++) {
            if (arr[minIndex] > arr[j]) {
                minIndex = j;
            }
        }
        // temp -> minIndex -> i -> temp
        T temp = arr[minIndex];
        arr[minIndex] = arr[i];
        arr[i] = temp;
    }
}

int main() {
    int intArr[] = {64, 90, 25, 12, 22, 11};
    int intSize = sizeof(intArr) / sizeof(intArr[0]);

    cout << "Original Integer Array: ";
    for (int i = 0; i < intSize; i++) {
        cout << intArr[i] << " ";
    }
    cout << endl;

    SelectionSort(intArr, intSize);

    cout << "Sorted Integer Array: ";
    for (int i = 0; i < intSize; ++i) {
        cout << intArr[i] << " ";
    }
    cout << endl;

    float floatArr[] = {64.1, 25.5, 12.2, 22.8, 11.3};
    int floatSize = sizeof(floatArr) / sizeof(floatArr[0]);

    cout << "Original Floating-Point Array: ";
    for (int i = 0; i < floatSize; i++) {
        cout << floatArr[i] << " ";
    }
    cout << endl;

    SelectionSort(floatArr, floatSize);

    cout << "Sorted Floating-Point Array: ";
    for (int i = 0; i < floatSize; i++) {
        cout << floatArr[i] << " ";
    }
    cout << endl;

    return 0;
}
