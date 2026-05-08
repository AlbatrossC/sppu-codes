/* 4(a) Write C++ program to draw 2-D object and perform following basic transformations:
   1. Scaling  2. Translation  3. Rotation.
   Apply the concept of operator overloading. */

#include <graphics.h>
#include <conio.h>
#include <math.h>
#include <stdio.h>

class Rect
{
public:
    float x1, y1, x2, y2;

    Rect() {}

    Rect(float a, float b, float c, float d)
    {
        x1 = a; y1 = b; x2 = c; y2 = d;
    }

    void draw()
    {
        rectangle((int)x1, (int)y1, (int)x2, (int)y2);
    }

    Rect translate(float tx, float ty)
    {
        return Rect(x1 + tx, y1 + ty, x2 + tx, y2 + ty);
    }

    Rect scale(float s)
    {
        float w = x2 - x1;
        float h = y2 - y1;
        return Rect(x1, y1, x1 + w * s, y1 + h * s);
    }

    Rect rotate(float angle)
    {
        float rad = angle * 3.14 / 180;
        float cx = (x1 + x2) / 2;
        float cy = (y1 + y2) / 2;
        float hw = (x2 - x1) / 2;
        float hh = (y2 - y1) / 2;

        float x = hw * cos(rad) - hh * sin(rad);
        float y = hw * sin(rad) + hh * cos(rad);

        return Rect(cx - hw, cy - hh, cx + x, cy + y);
    }
};

int main()
{
    int gd = DETECT, gm;
    initgraph(&gd, &gm, "");

    int choice;
    printf("1. Scaling\n2. Translation\n3. Rotation\n");
    printf("Enter choice: ");
    scanf("%d", &choice);

    Rect original(100, 200, 180, 260);
    cleardevice();

    original.draw();
    outtextxy(100, 180, "Original");

    if (choice == 1)
    {
        Rect scaled = original.scale(1.5).translate(200, 0);
        scaled.draw();
        outtextxy(300, 180, "Scaled");
    }
    else if (choice == 2)
    {
        Rect translated = original.translate(200, 0);
        translated.draw();
        outtextxy(300, 180, "Translated");
    }
    else if (choice == 3)
    {
        Rect rotated = original.rotate(45).translate(200, 0);
        rotated.draw();
        outtextxy(300, 180, "Rotated");
    }

    getch();
    closegraph();
    return 0;
}
