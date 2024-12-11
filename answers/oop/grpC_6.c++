#include <iostream>
#include <algorithm>
#include <vector>
using namespace std;

class Person {
public:
    string name;
    string DOB;
    string number;

    void input() {
        cout << "Enter Name: ";
        getline(cin, name);

        cout << "Enter Date of Birth (DD/MM/YYYY): ";
        getline(cin, DOB);

        cout << "Enter Telephone Number: ";
        getline(cin, number);
    }

    void display() const {
        cout << "Name: " << name << " | Date of Birth: " << DOB << " | Number: " << number << endl;
    }
};

bool sortByName(const Person& a, const Person& b) {
    return a.name < b.name;
}

void searchByName(const vector<Person>& people, const string& searchName) {
    bool found = false;
    for (const auto& person : people) {
        if (person.name == searchName) {
            person.display();
            found = true;
            break;
        }
    }

    if (!found) {
        cout << "No person found with the name " << searchName << "." << endl;
    }
}

int main() {
    vector<Person> people;

    int n;
    cout << "Enter the number of people: ";
    cin >> n;
    cin.ignore();

    for (int i = 0; i < n; i++) {
        Person person;
        person.input();
        people.push_back(person);
    }

    sort(people.begin(), people.end(), sortByName);

    cout << "\nSorted Records:\n";
    for (const auto& person : people) {
        person.display();
    }

    string search;
    cout << "Enter the name to search: ";
    getline(cin, search);

    searchByName(people, search);

    return 0;
}
