/* 5c) Write C++ program to generate fractal patterns by using Koch curves */

#include <graphics.h>
#include <math.h>
#include <stdio.h>
#include <conio.h>

class kochCurve
{
public:
    void koch(int it, int x1, int y1, int x5, int y5)
    {
        int x2, y2, x3, y3, x4, y4;
        int dx, dy;

        if (it == 0)
        {
            line(x1, y1, x5, y5);
        }
        else
        {
            dx = (x5 - x1) / 3;
            dy = (y5 - y1) / 3;

            x2 = x1 + dx;
            y2 = y1 + dy;

            x3 = (int)(0.5 * (x1 + x5) + sqrt(3) * (y1 - y5) / 6);
            y3 = (int)(0.5 * (y1 + y5) + sqrt(3) * (x5 - x1) / 6);

            x4 = x1 + 2 * dx;
            y4 = y1 + 2 * dy;

            koch(it - 1, x1, y1, x2, y2);
            koch(it - 1, x2, y2, x3, y3);
            koch(it - 1, x3, y3, x4, y4);
            koch(it - 1, x4, y4, x5, y5);
        }
    }
};

int main()
{
    kochCurve k;
    int it;
    int gd = DETECT, gm;

    printf("Enter Number Of Iterations: ");
    scanf("%d", &it);

    initgraph(&gd, &gm, "");

    k.koch(it, 150, 20, 20, 280);
    k.koch(it, 20, 280, 280, 280);
    k.koch(it, 280, 280, 150, 20);

    getch();
    closegraph();
    return 0;
}
