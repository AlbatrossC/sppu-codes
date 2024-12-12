#include <iostream>
using namespace std;

class Complex {
public:
    double real;
    double imag;

    Complex() {
        real = 0;
        imag = 0;
    }

    Complex(double r, double i) {
        real = r;
        imag = i;
    }

    Complex operator+(const Complex& other) {
        Complex result;
        result.real = real + other.real;
        result.imag = imag + other.imag;
        return result;
    }

    Complex operator*(const Complex& other) {
        Complex result;
        result.real = (real * other.real) - (imag * other.imag);
        result.imag = (real * other.imag) + (imag * other.real);
        return result;
    }

    friend istream& operator>>(istream& in, Complex& c) {
        cout << "Enter the real part: ";
        in >> c.real;
        cout << "Enter the imaginary part: ";
        in >> c.imag;
        return in;
    }

    friend ostream& operator<<(ostream& out, const Complex& c) {
        out << c.real << " + " << c.imag << "i" << endl;
        return out;
    }
};

int main() {
    Complex c1, c2, sum, product;

    cout << "Enter the first complex number:" << endl;
    cin >> c1;

    cout << "Enter the second complex number:" << endl;
    cin >> c2;

    sum = c1 + c2;
    product = c1 * c2;

    cout << "Sum: " << sum << endl;
    cout << "Product: " << product << endl;

    return 0;
}
