#include <iostream>
using namespace std;

class Complex{
    public:
        double real;
        double img;

        Complex(){
            real = 0;
            img = 0;
        }

        Complex(double r , double i){
            real = r;
            img = i;
        }

        Complex operator+(const Complex& other){
            Complex result;
            result.real= real + other.real;
            result.img = img + other.img;
            return result;
        }
        
        Complex operator*(const Complex& other){
            Complex result;
            result.real = (real*other.real) - (img*other.img);
            result.img = (real*other.img) + (img*other.real); 
            return result;
        }

        friend ostream& operator<<(ostream& out, Complex& c){
            out << c.real << "+" << c.img <<"i"<<endl;
            return out;
        }

        friend istream& operator>>(istream& in,Complex& c){
            cout << "Enter Real Part:";
            in>>c.real;
            cout<<"Enter Imaginary Part:";
            in>>c.img;
            return in;
        }
};

int main(){
    Complex c1, c2 , sum , product;

    cout << "Enter 1st complex Number:" << endl;
    cin>>c1;

    cout<< "Entr 2nd Complex Number:" << endl;;
    cin>>c2;

    sum = c1+c2;
    product = c1 * c2;

    cout << "Sum:" <<sum<<endl;
    cout<< "Product:" << product<<endl;

    return 0;
}