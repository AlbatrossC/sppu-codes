#include <iostream>
#include <graphics.h> // graphics.h library is used to include graphical operations in a program.
#include <math.h>
using namespace std;

class scan {
public:
    int x[20], y[20], k;
    float slope[20], x_int[20];
    void polygon(int n);
};

void scan::polygon(int n) {
    int i;
    float dx, dy;

    x[n] = x[0];
    y[n] = y[0];

    for (int i = 0; i < n; i++) { // draw all lines (edges of polygon)
        line(x[i], y[i], x[i + 1], y[i + 1]); // line coordinates x1,y1,x2,y2
    }

    for (i = 0; i < n; i++) { // finding slope of all lines
        dy = y[i + 1] - y[i]; // dy = y2 - y1
        dx = x[i + 1] - x[i]; // dx = x2 - x1
        if (dy == 0)
            slope[i] = 1;
        else if (dx == 0)
            slope[i] = 0;
        else
            slope[i] = dx / dy;
    }

    // finding intersection points
    
    
    	
    	
    for (int p = 0; p < 480; p++) { 
        k = 0;
        for (i = 0; i < n; i++) {
            if (((y[i] <= p) && (y[i + 1] > p)) || ((y[i] > p) && (y[i + 1] <= p))) {
                x_int[k] = x[i] + slope[i] * (p - y[i]);
                k++;
            }
        }

        for (int j = 0; j < k - 1; j++) { 
            for (int i = 0; i < k - 1; i++) {
                if (x_int[i] > x_int[i + 1]) {
                    float temp = x_int[i];
                    x_int[i] = x_int[i + 1];
                    x_int[i + 1] = temp;
                }
            }
        }

        for (int i = 0; i < k; i = i + 2) { 
            setcolor(YELLOW);
            line(x_int[i], p, x_int[i + 1], p);
            delay(10);
        }
    }
}

int main() {
    int n, i;
    scan p;

    // Ask user for number of edges
    cout << "Enter number of edges: ";
    cin >> n;

    // Ask for coordinates for each edge
    cout << "\nEnter Coordinates:\n";
    for (i = 0; i < n; i++) {
        cout << "Edge " << (i + 1) << ":\n";
        cout << "x" << (i + 1) << ": ";
        cin >> p.x[i];
        cout << "y" << (i + 1) << ": ";
        cin >> p.y[i];
    }

    int gd, gm;
    gd = DETECT;
    initgraph(&gd, &gm, NULL);
    
    p.polygon(n);
    getch();
    closegraph();
    return 0;
}
