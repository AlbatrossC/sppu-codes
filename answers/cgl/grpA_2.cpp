#include <iostream>
#include <graphics.h>
#include <conio.h>

using namespace std;

class Point {
public:
    int x, y;
    char code[4];
};

class LineClipping {
public:
    void drawWindow();
    void drawLine(Point p1, Point p2);
    Point computeCode(Point p);
    int checkVisibility(Point p1, Point p2);
    Point calculateIntersection(Point p1, Point p2);
};

int main() {
    LineClipping lc;
    int gd = DETECT, gm;
    Point p1, p2;

    cout << "Enter x1 and y1: ";
    cin >> p1.x >> p1.y;
    cout << "Enter x2 and y2: ";
    cin >> p2.x >> p2.y;

    initgraph(&gd, &gm, "");
    lc.drawWindow();
    delay(2000);
    
    lc.drawLine(p1, p2);
    delay(2000);
    cleardevice();

    p1 = lc.computeCode(p1);
    p2 = lc.computeCode(p2);
    
    int visibilityStatus = lc.checkVisibility(p1, p2);
    delay(2000);

    switch (visibilityStatus) {
        case 0:
            lc.drawWindow();
            lc.drawLine(p1, p2);
            break;
        case 1:
            lc.drawWindow();
            break;
        case 2:
            lc.drawWindow();
            lc.drawLine(lc.calculateIntersection(p1, p2), lc.calculateIntersection(p2, p1));
            break;
    }

    delay(2000);
    closegraph();
    return 0;
}

void LineClipping::drawWindow() {
    rectangle(150, 100, 450, 350);
}

void LineClipping::drawLine(Point p1, Point p2) {
    line(p1.x, p1.y, p2.x, p2.y);
}

Point LineClipping::computeCode(Point p) {
    Point codedPoint;
    codedPoint.code[0] = (p.y < 100) ? '1' : '0';
    codedPoint.code[1] = (p.y > 350) ? '1' : '0';
    codedPoint.code[2] = (p.x > 450) ? '1' : '0';
    codedPoint.code[3] = (p.x < 150) ? '1' : '0';
    codedPoint.x = p.x;
    codedPoint.y = p.y;
    return codedPoint;
}

int LineClipping::checkVisibility(Point p1, Point p2) {
    for (int i = 0; i < 4; i++) {
        if (p1.code[i] == '1' && p2.code[i] == '1') return 1;
        if (p1.code[i] == '0' && p2.code[i] == '0') return 0;
    }
    return 2;
}

Point LineClipping::calculateIntersection(Point p1, Point p2) {
    Point intersectedPoint;
    float slope;

    if (p1.code[3] == '1' || p1.code[2] == '1') {
        intersectedPoint.x = (p1.code[3] == '1') ? 150 : 450;
        slope = static_cast<float>(p2.y - p1.y) / (p2.x - p1.x);
        intersectedPoint.y = p1.y + slope * (intersectedPoint.x - p1.x);
    } else if (p1.code[0] == '1' || p1.code[1] == '1') {
        intersectedPoint.y = (p1.code[0] == '1') ? 100 : 350;
        slope = static_cast<float>(p2.y - p1.y) / (p2.x - p1.x);
        intersectedPoint.x = p1.x + (intersectedPoint.y - p1.y) / slope;
    }

    for (int i = 0; i < 4; i++)
        intersectedPoint.code[i] = p1.code[i];

    return intersectedPoint;
}
    