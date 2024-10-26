#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

class Person
{
public:
    string name;
    string DOB;
    string number;

    void input()
    {
        cout << "Enter Name: ";
        cin >> name;
        cout << "Enter DOB: ";
        cin >> DOB;
        cout << "Enter Number: ";
        cin >> number;
    }

    void display() const
    {
        cout << "Name: " << name << endl;
        cout << "DOB: " << DOB << endl;
        cout << "Number: " << number << endl;
    }
};

bool Sortingbyname(const Person &a, const Person &b)
{
    return a.name < b.name;
}

void Searchbyname(const vector<Person> &people, const string &searchname)
{
    bool found = false; // Variable to track if a person was found
    for (const auto &person : people)
    {
        if (person.name == searchname)
        {
            person.display();
            found = true; // Set found to true if a match is found
            break;        // Exit loop after finding the first match
        }
    }
}

int main()
{
    int n;
    cout << "ENter no of People:";
    cin >> n;

    vector<Person> people(n);
    for (auto &person : people)
    {
        person.input();
    }

    cout << "\nSorted Records:\n";
    for (const auto &person : people)
    {
        person.display();
    }

    string searchName;
    cout << "\nEnter a name to search: ";
    cin >> searchName; // Input name to search
    Searchbyname(people, searchName);

    return 0;
}