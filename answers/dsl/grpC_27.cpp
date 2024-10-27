#include <iostream>
#include <stack>
#include <string>
#include <cctype>

using namespace std;

int precedence(char op) {
    if (op == '+' || op == '-') return 1;
    if (op == '*' || op == '/') return 2;
    return 0;
}

string infixToPostfix(const string& infix) {
    stack<char> operators;
    string postfix;

    for (char ch : infix) {
        if (isalnum(ch)) {
            postfix += ch; // Add operand to output
        } else if (ch == '(') {
            operators.push(ch); // Push '(' onto stack
        } else if (ch == ')') {
            while (!operators.empty() && operators.top() != '(') {
                postfix += operators.top();
                operators.pop();
            }
            operators.pop(); // Remove '(' from stack
        } else {
            while (!operators.empty() && precedence(operators.top()) >= precedence(ch)) {
                postfix += operators.top();
                operators.pop();
            }
            operators.push(ch); // Push current operator onto stack
        }
    }

    while (!operators.empty()) {
        postfix += operators.top();
        operators.pop();
    }

    return postfix;
}

int evaluatePostfix(const string& postfix) {
    stack<int> operands;

    for (char ch : postfix) {
        if (isdigit(ch)) {
            operands.push(ch - '0'); // Convert char to int
        } else {
            int right = operands.top(); operands.pop();
            int left = operands.top(); operands.pop();
            switch (ch) {
                case '+': operands.push(left + right); break;
                case '-': operands.push(left - right); break;
                case '*': operands.push(left * right); break;
                case '/': operands.push(left / right); break;
            }
        }
    }

    return operands.top();
}

int main() {
    string infix;
    
    cout << "Enter an infix expression (e.g., A+B*C-D): ";
    getline(cin, infix); // Read the entire line of input

    string postfix = infixToPostfix(infix);
    cout << "Postfix: " << postfix << endl;

    // Assuming operands are single digit for evaluation
    cout << "Enter the postfix expression to evaluate (e.g., ABC*D-): ";
    string postfixExpr;
    getline(cin, postfixExpr); // Read the postfix expression input

    int result = evaluatePostfix(postfixExpr);
    cout << "Result: " << result << endl;

    return 0;
}
