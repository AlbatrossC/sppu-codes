/* 5(a) Write C++ program to generate snowflake using concept of fractals */

#include <graphics.h>
#include <conio.h>
#include <math.h>

void koch(int x1, int y1, int x2, int y2, int n)
{
    if (n == 0)
    {
        line(x1, y1, x2, y2);
        return;
    }

    int x3 = (2 * x1 + x2) / 3;
    int y3 = (2 * y1 + y2) / 3;
    int x4 = (x1 + 2 * x2) / 3;
    int y4 = (y1 + 2 * y2) / 3;

    int x = x3 + (x4 - x3) / 2 - (y4 - y3) * sqrt(3) / 2;
    int y = y3 + (y4 - y3) / 2 + (x4 - x3) * sqrt(3) / 2;

    koch(x1, y1, x3, y3, n - 1);
    koch(x3, y3, x, y, n - 1);
    koch(x, y, x4, y4, n - 1);
    koch(x4, y4, x2, y2, n - 1);
}

int main()
{
    int gd = DETECT, gm;
    initgraph(&gd, &gm, "");

    int x1 = 200, y1 = 200;
    int x2 = 400, y2 = 200;
    int x3 = 300, y3 = 373;

    koch(x1, y1, x2, y2, 4);
    koch(x2, y2, x3, y3, 4);
    koch(x3, y3, x1, y1, 4);

    getch();
    closegraph();
    return 0;
}
