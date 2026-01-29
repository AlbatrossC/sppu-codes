/* 1. Write C++ program to draw a concave polygon and fill it with desired color using scan fill algorithm. */

#include <graphics.h>
#include <conio.h>

struct Point
{
    int x, y;
};

Point poly[6] = {
    {200, 100},
    {300, 150},
    {250, 200},
    {300, 250},
    {200, 300},
    {150, 200}
};

int n = 6;

void drawPolygon()
{
    int i;
    for (i = 0; i < n; i++)
    {
        line(poly[i].x, poly[i].y,
             poly[(i + 1) % n].x, poly[(i + 1) % n].y);
    }
}

void scanlineFill(int color)
{
    int i, j, y;
    int yMin = poly[0].y, yMax = poly[0].y;

    for (i = 1; i < n; i++)
    {
        if (poly[i].y < yMin) yMin = poly[i].y;
        if (poly[i].y > yMax) yMax = poly[i].y;
    }

    setcolor(color);

    for (y = yMin; y <= yMax; y++)
    {
        int interX[10];
        int count = 0;

        for (i = 0; i < n; i++)
        {
            int x1 = poly[i].x;
            int y1 = poly[i].y;
            int x2 = poly[(i + 1) % n].x;
            int y2 = poly[(i + 1) % n].y;

            if (y1 > y2)
            {
                int tx = x1; x1 = x2; x2 = tx;
                int ty = y1; y1 = y2; y2 = ty;
            }

            if (y >= y1 && y < y2)
            {
                int x = x1 + (y - y1) * (x2 - x1) / (y2 - y1);
                interX[count++] = x;
            }
        }

        for (i = 0; i < count - 1; i++)
        {
            for (j = i + 1; j < count; j++)
            {
                if (interX[i] > interX[j])
                {
                    int temp = interX[i];
                    interX[i] = interX[j];
                    interX[j] = temp;
                }
            }
        }

        for (i = 0; i < count; i += 2)
        {
            line(interX[i], y, interX[i + 1], y);
        }
    }
}

int main()
{
    int gd = DETECT, gm;
    initgraph(&gd, &gm, "");

    setcolor(WHITE);
    drawPolygon();
    scanlineFill(RED);

    getch();
    closegraph();
    return 0;
}
