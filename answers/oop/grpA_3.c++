#include <iostream>
#include <stdio.h>
using namespace std;

class publication {
private:
    string title;
    float price;

public:
    void add() {
        cout << "Enter Title: ";
        cin.ignore();
        getline(cin, title);
        cout << "Enter Price: ";
        cin >> price;
    }

    void display() {
        cout << "Title: " << title << endl;
        cout << "Price: " << price << endl;
    }
};

class book : public publication {
private:
    int page_count;

public:
    void add_book() {
        try {
            add();
            cout << "Enter Pages: ";
            cin >> page_count;
            if (page_count <= 0) {
                throw page_count;
            }
        }
        catch (...) {
            cout << "Invalid page count!" << endl;
            page_count = 0;
        }
    }

    void display_book() {
        display();
        cout << "Pages: " << page_count << endl;
    }
};

class tape : public publication {
private:
    float play_time;

public:
    void add_tape() {
        try {
            add();
            cout << "Enter Play Time (minutes): ";
            cin >> play_time;
            if (play_time <= 0)
                throw play_time;
        }
        catch (...) {
            cout << "Invalid play time!" << endl;
            play_time = 0;
        }
    }

    void display_tape() {
        display();
        cout << "Play Time: " << play_time << " min" << endl;
    }
};

int main() {
    book b1[10];
    tape t1[10];
    int ch, b_count = 0, t_count = 0;

    do {
        cout << "* PUBLICATION DATABASE *" << endl;
        cout << "1. Add Book" << endl;
        cout << "2. Add Tape" << endl;
        cout << "3. Show Books" << endl;
        cout << "4. Show Tapes" << endl;
        cout << "5. Exit" << endl;
        cout << "Enter choice: ";
        cin >> ch;

        switch (ch) {
        case 1:
            b1[b_count].add_book();
            b_count++;
            break;
        case 2:
            t1[t_count].add_tape();
            t_count++;
            break;
        case 3:
            cout << "* BOOKS *" << endl;
            for (int j = 0; j < b_count; j++) {
                b1[j].display_book();
            }
            break;
        case 4:
            cout << "* TAPES *" << endl;
            for (int j = 0; j < t_count; j++) {
                t1[j].display_tape();
            }
            break;
        case 5:
            exit(0);
        default:
            cout << "Invalid choice!" << endl;
        }
    } while (ch != 5);

    return 0;
}
