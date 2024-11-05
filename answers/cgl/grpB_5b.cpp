#include <GL/glut.h>
#include <cmath>

void drawLine(float x1, float y1, float x2, float y2) {
    glBegin(GL_LINES);
    glVertex2f(x1, y1);
    glVertex2f(x2, y2);
    glEnd();
}

void hilbertCurve(int order, float x, float y, float size, int angle) {
    if (order == 0) return;

    float newSize = size / 2;

    hilbertCurve(order - 1, x, y, newSize, 0);
    drawLine(x + newSize, y, x + newSize, y + newSize);
    hilbertCurve(order - 1, x + newSize, y + newSize, newSize, 0);
    drawLine(x + newSize, y + newSize, x + newSize, y + 2 * newSize);
    hilbertCurve(order - 1, x + newSize, y + 2 * newSize, newSize, 0);
    drawLine(x + newSize, y + 2 * newSize, x, y + 2 * newSize);
    hilbertCurve(order - 1, x, y + 2 * newSize, newSize, 0);
    drawLine(x, y + 2 * newSize, x, y);
}

void display() {
    glClear(GL_COLOR_BUFFER_BIT);
    glColor3f(1.0f, 1.0f, 1.0f);
    float size = 1.0f;
    float x = -size / 2;
    float y = -size / 2;
    hilbertCurve(5, x, y, size, 0);
    glFlush();
}

void init() {
    glClearColor(0.0f, 0.0f, 0.0f, 1.0f);
    glColor3f(1.0f, 1.0f, 1.0f);
    glPointSize(1.0);
    glLineWidth(1.0);
    glMatrixMode(GL_PROJECTION);
    gluOrtho2D(-1.0, 1.0, -1.0, 1.0);
}

int main(int argc, char** argv) {
    glutInit(&argc, argv);
    glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB);
    glutInitWindowSize(500, 500);
    glutCreateWindow("Hilbert Curve");
    init();
    glutDisplayFunc(display);
    glutMainLoop();
    return 0;
}
