#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

class Person {
public:
    string name;
    string DOB;
    string number;

    void input() {
        cout << "Enter Name: ";
        cin >> ws; // Clear any leading whitespace
        getline(cin, name);
        cout << "Enter DOB (DD/MM/YYYY): ";
        getline(cin, DOB);
        cout << "Enter Phone Number: ";
        getline(cin, number);
    }

    void display() const {
        cout << "Name: " << name << "\nDOB: " << DOB << "\nPhone Number: " << number << "\n";
    }
};

bool Sortingbyname(const Person &a, const Person &b) {
    return a.name < b.name;
}

void Searchbyname(const vector<Person> &people, const string &searchname) {
    bool found = false;
    for (const auto &person : people) {
        if (person.name == searchname) {
            person.display();
            found = true;
        }
    }
    if (!found) {
        cout << "No record found for name: " << searchname << "\n";
    }
}

int main() {
    int n;
    cout << "Enter the number of people: ";
    cin >> n;

    vector<Person> people(n);
    for (auto &person : people) {
        person.input();
    }

    sort(people.begin(), people.end(), Sortingbyname);

    cout << "\nSorted Records:\n";
    for (const auto &person : people) {
        person.display();
    }

    string searchName;
    cout << "\nEnter a name to search: ";
    cin >> ws; // Clear any leading whitespace
    getline(cin, searchName);
    Searchbyname(people, searchName);

    return 0;
}
