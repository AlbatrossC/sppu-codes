/* 2. Write C++ program to implement Cohen Southerland line clipping algorithm. */

#include <graphics.h>
#include <conio.h>
#include <math.h>

#define xmin 150
#define ymin 100
#define xmax 450
#define ymax 350

int regionCode(int x, int y)
{
    int code = 0;
    if (y < ymin) code |= 1;
    if (y > ymax) code |= 2;
    if (x > xmax) code |= 4;
    if (x < xmin) code |= 8;
    return code;
}

void cohenSutherlandClip(int *x1, int *y1, int *x2, int *y2)
{
    int c1 = regionCode(*x1, *y1);
    int c2 = regionCode(*x2, *y2);

    while (c1 != 0 || c2 != 0)
    {
        if ((c1 & c2) != 0)
            return;

        int c, x, y;
        float m = (float)(*y2 - *y1) / (*x2 - *x1);

        c = (c1 != 0) ? c1 : c2;

        if (c & 1)
        {
            y = ymin;
            x = *x1 + (y - *y1) / m;
        }
        else if (c & 2)
        {
            y = ymax;
            x = *x1 + (y - *y1) / m;
        }
        else if (c & 4)
        {
            x = xmax;
            y = *y1 + m * (x - *x1);
        }
        else
        {
            x = xmin;
            y = *y1 + m * (x - *x1);
        }

        if (c == c1)
        {
            *x1 = x;
            *y1 = y;
            c1 = regionCode(*x1, *y1);
        }
        else
        {
            *x2 = x;
            *y2 = y;
            c2 = regionCode(*x2, *y2);
        }
    }
}

int main()
{
    int gd = DETECT, gm;
    int x1 = 100, y1 = 200;
    int x2 = 500, y2 = 100;

    initgraph(&gd, &gm, "");

    rectangle(xmin, ymin, xmax, ymax);
    line(x1, y1, x2, y2);
    outtextxy(140, 370, "PRESS ENTER TO CLIP THE LINE");

    while (getch() != 13);
    cleardevice();

    cohenSutherlandClip(&x1, &y1, &x2, &y2);

    rectangle(xmin, ymin, xmax, ymax);
    line(x1, y1, x2, y2);
    outtextxy(180, 370, "CLIPPED LINE DISPLAYED");

    getch();
    closegraph();
    return 0;
}
