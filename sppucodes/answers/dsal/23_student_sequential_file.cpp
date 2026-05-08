#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
using namespace std;

struct Student {
    int roll;
    string name;
    string division;
    string address;
};

void addStudent() {
    ofstream file("students.txt", ios::app);
    Student s;

    cout << "Enter roll number: ";
    cin >> s.roll;
    cin.ignore();

    cout << "Enter name: ";
    getline(cin, s.name);

    cout << "Enter division: ";
    getline(cin, s.division);

    cout << "Enter address: ";
    getline(cin, s.address);

    file << s.roll << "," << s.name << "," << s.division << "," << s.address << "\n";
    file.close();
    cout << "Student added successfully.\n";
}

void displayStudent() {
    ifstream file("students.txt");
    int searchRoll;
    bool found = false;

    cout << "Enter roll number to search: ";
    cin >> searchRoll;

    string line, rollStr, name, division, address;

    while (getline(file, line)) {
        stringstream ss(line);
        getline(ss, rollStr, ',');
        getline(ss, name, ',');
        getline(ss, division, ',');
        getline(ss, address);

        if (stoi(rollStr) == searchRoll) {
            found = true;
            cout << "Student Found:\n";
            cout << "Roll Number: " << rollStr << "\n";
            cout << "Name: " << name << "\n";
            cout << "Division: " << division << "\n";
            cout << "Address: " << address << "\n";
            break;
        }
    }

    file.close();

    if (!found)
        cout << "Student with roll number " << searchRoll << " not found.\n";
}

void deleteStudent() {
    ifstream file("students.txt");
    ofstream temp("temp.txt");

    int deleteRoll;
    bool deleted = false;
    string line;

    cout << "Enter roll number to delete: ";
    cin >> deleteRoll;

    while (getline(file, line)) {
        stringstream ss(line);
        string rollStr;
        getline(ss, rollStr, ',');

        if (stoi(rollStr) != deleteRoll) {
            temp << line << "\n";
        } else {
            deleted = true;
        }
    }

    file.close();
    temp.close();

    remove("students.txt");
    rename("temp.txt", "students.txt");

    if (deleted)
        cout << "Student deleted successfully.\n";
    else
        cout << "Student with roll number " << deleteRoll << " not found.\n";
}

int main() {
    int choice;
    do {
        cout << "\n--- Student Record System ---\n";
        cout << "1. Add Student\n";
        cout << "2. Display Student\n";
        cout << "3. Delete Student\n";
        cout << "4. Exit\n";
        cout << "Enter your choice: ";
        cin >> choice;

        switch (choice) {
            case 1:
                addStudent();
                break;
            case 2:
                displayStudent();
                break;
            case 3:
                deleteStudent();
                break;
            case 4:
                cout << "Exiting program.\n";
                break;
            default:
                cout << "Invalid choice. Please try again.\n";
        }
    } while (choice != 4);

    return 0;
}
