#include <iostream>
#include <graphics.h>
#include <cmath>

using namespace std;

int main() {
    cout << "Select option:\n1) Scaling\n2) Rotation\n3) Translation\n";
    int option;
    cout << "Enter the number: ";
    cin >> option;

    int gd = DETECT, gm;
    initgraph(&gd, &gm, "");

    switch (option) {
        case 1: {
            int t1 = 3, t2 = 3;
            cout << "Rectangle before scaling\n";
            rectangle(200, 200, 300, 300);
            setcolor(4);
            setcolor(1);
            cout << "Rectangle after scaling\n";
            rectangle(100 * t1, 100 * t2, 150 * t1, 150 * t2);
            break;
        }
        case 2: {
            int angle = (6 * 3.14) / 180;
            cout << "Rectangle before rotation\n";
            rectangle(200, 200, 300, 300);
            setcolor(4);
            cout << "Rectangle after rotation\n";
            long xr = 200 + ((300 - 200) * cos(angle) - (300 - 200) * sin(angle));
            long yr = 300 + ((300 - 200) * sin(angle) + (300 - 200) * cos(angle));
            rectangle(200, 300, xr, yr);
            break;
        }
        case 3: {
            int t1 = 50, t2 = 50;
            cout << "Rectangle before translation\n";
            rectangle(200, 200, 300, 300);
            setcolor(4);
            setcolor(1);
            cout << "Rectangle after translation\n";
            rectangle(200 + t1, 200 + t2, 300 + t1, 300 + t2);
            break;
        }
        default:
            cout << "Invalid option selected.\n";
            break;
    }

    getch();
    closegraph();
    return 0;
}
