/* 3. Write C++ program to draw the following pattern. 
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

        float xInc = dx / (float)steps;
        float yInc = dy / (float)steps;

        float x = x1;
        float y = y1;

        for (int i = 0; i <= steps; i++)
        {
            putpixel((int)x, (int)y, WHITE);
            x += xInc;
            y += yInc;
        }
    }

    void circleBres(int xc, int yc, int r)
    {
        int x = 0, y = r;
        int d = 3 - 2 * r;

        while (x <= y)
        {
            plot(xc, yc, x, y);

            if (d < 0)
                d = d + 4 * x + 6;
            else
            {
                d = d + 4 * (x - y) + 10;
                y--;
            }
            x++;
        }
    }

private:
    void plot(int xc, int yc, int x, int y)
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

    d.circleBres(xc, yc, 120);
    d.circleBres(xc, yc, 60);

    d.lineDDA(xc, yc - 120, xc - 100, yc + 60);
    d.lineDDA(xc - 100, yc + 60, xc + 100, yc + 60);
    d.lineDDA(xc + 100, yc + 60, xc, yc - 120);

    getch();
    closegraph();
    return 0;
}
