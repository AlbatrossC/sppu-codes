/* 4(b) Write C++ program to implement translation, rotation and scaling transformations
   on equilateral triangle and rhombus. Apply the concept of operator overloading. */

#include <graphics.h>
#include <conio.h>
#include <math.h>
#include <stdio.h>

class Shape
{
public:
    float x[4], y[4];
    int n;

    Shape(int p) { n = p; }

    void draw()
    {
        for (int i = 0; i < n - 1; i++)
            line(x[i], y[i], x[i + 1], y[i + 1]);
        line(x[n - 1], y[n - 1], x[0], y[0]);
    }

    void getCenter(float &cx, float &cy)
    {
        cx = cy = 0;
        for (int i = 0; i < n; i++)
        {
            cx += x[i];
            cy += y[i];
        }
        cx /= n;
        cy /= n;
    }

    Shape operator+(int dx)
    {
        Shape r(n);
        for (int i = 0; i < n; i++)
        {
            r.x[i] = x[i] + dx;
            r.y[i] = y[i];
        }
        return r;
    }

    Shape operator*(float s)
    {
        Shape r(n);
        float cx, cy;
        getCenter(cx, cy);

        for (int i = 0; i < n; i++)
        {
            r.x[i] = cx + (x[i] - cx) * s;
            r.y[i] = cy + (y[i] - cy) * s;
        }
        return r;
    }

    Shape rotate(float a)
    {
        Shape r(n);
        float cx, cy;
        float rad = a * 3.14 / 180;
        getCenter(cx, cy);

        for (int i = 0; i < n; i++)
        {
            float dx = x[i] - cx;
            float dy = y[i] - cy;
            r.x[i] = cx + dx * cos(rad) - dy * sin(rad);
            r.y[i] = cy + dx * sin(rad) + dy * cos(rad);
        }
        return r;
    }
};

int main()
{
    int gd = DETECT, gm, ch;
    initgraph(&gd, &gm, "");

    printf("1. Scaling\n2. Translation\n3. Rotation\n");
    printf("Enter choice: ");
    scanf("%d", &ch);

    Shape tri(3);
    tri.x[0] = 120; tri.y[0] = 200;
    tri.x[1] = 170; tri.y[1] = 120;
    tri.x[2] = 220; tri.y[2] = 200;

    Shape rho(4);
    rho.x[0] = 120; rho.y[0] = 320;
    rho.x[1] = 160; rho.y[1] = 280;
    rho.x[2] = 200; rho.y[2] = 320;
    rho.x[3] = 160; rho.y[3] = 360;

    setcolor(WHITE);
    tri.draw();
    rho.draw();

    if (ch == 1)
    {
        (tri * 1.5 + 200).draw();
        (rho * 1.5 + 200).draw();
    }
    else if (ch == 2)
    {
        (tri + 200).draw();
        (rho + 200).draw();
    }
    else if (ch == 3)
    {
        (tri.rotate(45) + 200).draw();
        (rho.rotate(45) + 200).draw();
    }

    getch();
    closegraph();
    return 0;
}
