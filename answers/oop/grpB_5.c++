#include <iostream>
using namespace std;

template <class T>
void SelectionSort(T a[], int n) {
    for (int i = 0; i < n; i++) {
        int min_index = i;
        for (int j = i + 1; j < n; j++) {
            if (a[j] < a[min_index]) {
                min_index = j;
            }
        }
        T temp = a[min_index];
        a[min_index] = a[i];
        a[i] = temp;
    }
}

template <class T>
void in_out(T a[], int max_size) {
    int n;
    cout << "Enter the number of elements (max " << max_size << "): ";
    cin >> n;

    if (n > max_size || n <= 0) {
        cout << "Invalid size! Must be between 1 and " << max_size << ".\n";
        return;
    }

    for (int i = 0; i < n; i++) {
        cout << "Element no." << (i + 1) << ": ";
        cin >> a[i];
    }

    SelectionSort(a, n);

    cout << "Sorted Array: ";
    for (int i = 0; i < n; i++) {
        cout << a[i] << " ";
    }
    cout << endl;
}

int main() {
    const int max_size = 10;
    int int_arr[max_size];
    float float_arr[max_size];

    cout << "Integer Array Sorting:\n";
    in_out(int_arr, max_size);

    cout << "Floating Array Sorting:\n";
    in_out(float_arr, max_size);

    return 0;
}
