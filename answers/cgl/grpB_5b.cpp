/* 5b) Write C++ program to generate Hilbert curve using concept of fractals */

#include <graphics.h>
#include <conio.h>
#include <stdio.h>

int x = 50, y = 50;
int step = 10;

void move(int dx, int dy)
{
    x += dx * step;
    y += dy * step;
    lineto(x, y);
}

void hilbert(int n, int dx, int dy)
{
    if (n == 0)
        return;

    hilbert(n - 1, dy, dx);
    move(dx, dy);

    hilbert(n - 1, dx, dy);
    move(dy, dx);

    hilbert(n - 1, dx, dy);
    move(-dx, -dy);

    hilbert(n - 1, -dy, -dx);
}

int main()
{
    int n;
    int gd = DETECT, gm;

    printf("Enter number of iterations: ");
    scanf("%d", &n);

    initgraph(&gd, &gm, "");

    moveto(x, y);
    hilbert(n, 1, 0);

    getch();
    closegraph();
    return 0;
}
