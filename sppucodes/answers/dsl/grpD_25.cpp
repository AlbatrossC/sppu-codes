#include <iostream>
#include <stack>
#include <string>
#include <cctype>
using namespace std;

void printRev(const string &s) {
    stack<char> stk;
    
    for (char ch : s) {
        if (isalnum(ch)) {
            stk.push(tolower(ch));
        }
    }

    cout << "Original: " << s << endl;
    cout << "Reversed: ";
    
    while (!stk.empty()) {
        cout << stk.top();
        stk.pop();
    }
    cout << endl;
}

bool isPal(const string &s) {
    stack<char> stk;
    string filtered;

    for (char ch : s) {
        if (isalnum(ch)) {
            filtered += tolower(ch);
            stk.push(tolower(ch));
        }
    }

    string rev;
    while (!stk.empty()) {
        rev += stk.top();
        stk.pop();
    }

    return filtered == rev;
}

int main() {
    string input;

    cout << "Enter a string: ";
    getline(cin, input);

    printRev(input);

    if (isPal(input)) {
        cout << "The string is a palindrome." << endl;
    } else {
        cout << "The string is not a palindrome." << endl;
    }

    return 0;
}
