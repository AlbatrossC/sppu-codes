#include <iostream>
using namespace std;

const int max_size = 10;
int int_arr[max_size];
float float_arr[max_size];

template<class T>
void SelectionSort(T a[], int &n){
    for (int i = 0 ; i<n; i++){
        int min_index =i;
        for(int j = i+1; j<n; j++){
            if (a[j] < a[min_index]){
                min_index =j;
            }
        }

        T temp = a[min_index];
        a[min_index] = a[i];
        a[i] = temp;
    }
}

template<class T>
void in_out(T a[], int n){
    cout << "Enter the no of elements:";
    cin>>n;

    for(int i = 0 ; i<n ; i++){
        cout << "Element no."<<(i+1)<<":";
        cin>>a[i];
    }
    cout << endl;

    SelectionSort(a , n);

    //Display
    cout << "Sorted Array:" << endl;
    for(int i = 0; i<n ; i++){
        cout << a[i] << " ";
    }

    cout << endl;
}

int main(){
    int int_arr[max_size];
    float float_arr[max_size];
    int n;

    cout << "Integar array Sorting:" << endl;
    in_out(int_arr , n);

    cout << "Floating array Sorting:" << endl;
    in_out(float_arr , n);
    
    
}

