#include <iostream>
#include <string>
using namespace std;

struct Node {
    char bit;
    Node* next;
    Node* prev;

    Node(char b) {
        bit = b;
        next = nullptr;
        prev = nullptr;
    }
};

class BinaryNumber {
private:
    Node* head;
    Node* tail;

public:
    BinaryNumber() {
        head = nullptr;
        tail = nullptr;
    }

    void append(char bit) {
        Node* newNode = new Node(bit);
        if (!head) {
            head = newNode;
            tail = newNode;
        } else {
            tail->next = newNode;
            newNode->prev = tail;
            tail = newNode;
        }
    }

    void display() const {
        Node* current = head;
        while (current) {
            cout << current->bit;
            current = current->next;
        }
        cout << endl;
    }

    BinaryNumber onesComplement() const {
        BinaryNumber result;
        Node* current = head;
        while (current) {
            result.append(current->bit == '0' ? '1' : '0');
            current = current->next;
        }
        return result;
    }

    BinaryNumber twosComplement() const {
        BinaryNumber onesComp = onesComplement();
        BinaryNumber result;
        Node* current = onesComp.tail;
        int carry = 1;

        while (current) {
            char sum = (current->bit - '0') + carry;
            result.append((sum % 2) + '0');
            carry = sum / 2;
            current = current->prev;
        }

        if (carry) {
            result.append('1');
        }

        return reverse(result);
    }

    BinaryNumber reverse(const BinaryNumber& bin) const {
        BinaryNumber result;
        Node* current = bin.tail;
        while (current) {
            result.append(current->bit);
            current = current->prev;
        }
        return result;
    }

    BinaryNumber add(const BinaryNumber& other) const {
        BinaryNumber result;
        Node* thisCurrent = tail;
        Node* otherCurrent = other.tail;
        int carry = 0;

        while (thisCurrent || otherCurrent || carry) {
            int sum = carry;
            if (thisCurrent) {
                sum += (thisCurrent->bit - '0');
                thisCurrent = thisCurrent->prev;
            }
            if (otherCurrent) {
                sum += (otherCurrent->bit - '0');
                otherCurrent = otherCurrent->prev;
            }

            result.append((sum % 2) + '0');
            carry = sum / 2;
        }

        return reverse(result);
    }

    ~BinaryNumber() {
        Node* current = head;
        while (current) {
            Node* nextNode = current->next;
            delete current;
            current = nextNode;
        }
    }
};

int main() {
    BinaryNumber bin1, bin2;
    cout << "Enter first binary number (e.g., 1011): ";
    string input;
    cin >> input;
    for (char bit : input) {
        bin1.append(bit);
    }

    cout << "Enter second binary number (e.g., 1101): ";
    cin >> input;
    for (char bit : input) {
        bin2.append(bit);
    }

    cout << "First Binary Number: ";
    bin1.display();

    cout << "Second Binary Number: ";
    bin2.display();

    cout << "1's Complement of First Binary Number: ";
    BinaryNumber onesComp1 = bin1.onesComplement();
    onesComp1.display();

    cout << "2's Complement of First Binary Number: ";
    BinaryNumber twosComp1 = bin1.twosComplement();
    twosComp1.display();

    cout << "Sum of Both Binary Numbers: ";
    BinaryNumber sum = bin1.add(bin2);
    sum.display();

    return 0;
}
