#include <graphics.h>
#include <iostream>
#include <vector>
#include <algorithm>

using namespace std;

struct Point {
    int x, y;
};

void drawPolygon(const vector<Point>& points) {
    int n = points.size();
    for (int i = 0; i < n; i++) {
        line(
            points[i].x, points[i].y, 
            points[(i + 1) % n].x, points[(i + 1) % n].y
        );
    }
}

void scanlineFill(const vector<Point>& points, int fillColor) {
    int n = points.size();
    int yMin = INT_MAX, yMax = INT_MIN;

    for (int i = 0; i < n; i++) {
        yMin = min(yMin, points[i].y);
        yMax = max(yMax, points[i].y);
    }

    for (int y = yMin; y <= yMax; y++) {
        vector<int> intersections;

        for (int i = 0; i < n; i++) {
            int x1 = points[i].x, y1 = points[i].y;
            int x2 = points[(i + 1) % n].x, y2 = points[(i + 1) % n].y;

            if (y1 > y2) {
                swap(x1, x2);
                swap(y1, y2);
            }

            if (y >= y1 && y < y2 && y2 != y1) {
                int xIntersect = x1 + (y - y1) * (x2 - x1) / (y2 - y1);
                intersections.push_back(xIntersect);
            }
        }

        sort(intersections.begin(), intersections.end());

        for (size_t i = 0; i < intersections.size(); i += 2) {
            if (i + 1 < intersections.size()) {
                line(
                    intersections[i], y, 
                    intersections[i + 1], y
                );
                setcolor(fillColor);
            }
        }
    }
}

int main() {
    int gd = DETECT, gm;
    initgraph(&gd, &gm, "");

    int n;
    cout << "Enter the number of vertices of the polygon: ";
    cin >> n;

    vector<Point> points(n);
    for (int i = 0; i < n; i++) {
        cout << "Enter x and y for point " << i + 1 << ": ";
        cin >> points[i].x >> points[i].y;
    }

    setcolor(WHITE);
    drawPolygon(points);

    scanlineFill(points, RED);

    getch();
    closegraph();
    return 0;
}
