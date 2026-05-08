/* 3(b) Write C++ program to draw the following pattern.
   Use DDA line and Bresenham’s circle drawing algorithm.
   Apply the concept of encapsulation. */

#include <graphics.h>
#include <conio.h>
#include <math.h>

class Draw
{
public:
    void lineDDA(int x1, int y1, int x2, int y2)
    {
        int dx = x2 - x1;
        int dy = y2 - y1;
        int steps = abs(dx) > abs(dy) ? abs(dx) : abs(dy);

        float x = x1;
        float y = y1;
        float xi = dx / (float)steps;
        float yi = dy / (float)steps;

        for (int i = 0; i <= steps; i++)
        {
            putpixel((int)x, (int)y, WHITE);
            x += xi;
            y += yi;
        }
    }

    void circleBres(int xc, int yc, int r)
    {
        int x = 0, y = r;
        int d = 3 - 2 * r;

        while (x <= y)
        {
            drawPoints(xc, yc, x, y);

            if (d < 0)
                d += 4 * x + 6;
            else
            {
                d += 4 * (x - y) + 10;
                y--;
            }
            x++;
        }
    }

private:
    void drawPoints(int xc, int yc, int x, int y)
    {
        putpixel(xc + x, yc + y, WHITE);
        putpixel(xc - x, yc + y, WHITE);
        putpixel(xc + x, yc - y, WHITE);
        putpixel(xc - x, yc - y, WHITE);
        putpixel(xc + y, yc + x, WHITE);
        putpixel(xc - y, yc + x, WHITE);
        putpixel(xc + y, yc - x, WHITE);
        putpixel(xc - y, yc - x, WHITE);
    }
};

int main()
{
    int gd = DETECT, gm;
    initgraph(&gd, &gm, "");

    Draw d;
    int xc = 320, yc = 240;

    d.lineDDA(160, 120, 480, 120);
    d.lineDDA(480, 120, 480, 360);
    d.lineDDA(480, 360, 160, 360);
    d.lineDDA(160, 360, 160, 120);

    d.lineDDA(xc, 120, 480, yc);
    d.lineDDA(480, yc, xc, 360);
    d.lineDDA(xc, 360, 160, yc);
    d.lineDDA(160, yc, xc, 120);

    d.circleBres(xc, yc, 90);

    getch();
    closegraph();
    return 0;
}
