#include <iostream>
#include <fstream>
#include <cstring>
#include <vector>
using namespace std;

struct Employee {
    int id;
    char name[50];
    char designation[50];
    float salary;

    void input() {
        cout << "Enter Employee ID: "; cin >> id;
        cin.ignore();
        cout << "Enter Name: "; cin.getline(name, 50);
        cout << "Enter Designation: "; cin.getline(designation, 50);
        cout << "Enter Salary: "; cin >> salary;
    }

    void display() {
        cout << "\nID: " << id
             << "\nName: " << name
             << "\nDesignation: " << designation
             << "\nSalary: " << salary << "\n";
    }
};

struct IndexRecord {
    int id;
    int pos;
    bool active;
};

vector<IndexRecord> loadIndex() {
    vector<IndexRecord> index;
    ifstream idxFile("index.txt");
    IndexRecord rec;
    while (idxFile >> rec.id >> rec.pos >> rec.active) {
        index.push_back(rec);
    }
    return index;
}

void saveIndex(const vector<IndexRecord>& index) {
    ofstream idxFile("index.txt");
    for (const auto& rec : index) {
        idxFile << rec.id << " " << rec.pos << " " << rec.active << "\n";
    }
}

int searchIndex(const vector<IndexRecord>& index, int id) {
    for (size_t i = 0; i < index.size(); ++i) {
        if (index[i].id == id && index[i].active) return i;
    }
    return -1;
}

void addEmployee() {
    Employee emp;
    emp.input();

    ofstream out("employee.dat", ios::binary | ios::app);
    int pos = out.tellp();
    out.write((char*)&emp, sizeof(emp));
    out.close();

    vector<IndexRecord> index = loadIndex();
    index.push_back({emp.id, pos, true});
    saveIndex(index);

    cout << "Employee added successfully!\n";
}

void displayEmployee() {
    int id;
    cout << "Enter Employee ID to search: ";
    cin >> id;

    vector<IndexRecord> index = loadIndex();
    int idx = searchIndex(index, id);

    if (idx == -1) {
        cout << "Employee not found.\n";
        return;
    }

    ifstream in("employee.dat", ios::binary);
    Employee emp;
    in.seekg(index[idx].pos);
    in.read((char*)&emp, sizeof(emp));
    in.close();

    emp.display();
}

void deleteEmployee() {
    int id;
    cout << "Enter Employee ID to delete: ";
    cin >> id;

    vector<IndexRecord> index = loadIndex();
    int idx = searchIndex(index, id);

    if (idx == -1) {
        cout << "Employee not found.\n";
        return;
    }

    index[idx].active = false;
    saveIndex(index);
    cout << "Employee deleted successfully.\n";
}

int main() {
    int choice;
    do {
        cout << "\nEmployee Management System";
        cout << "\n1. Add Employee";
        cout << "\n2. Display Employee";
        cout << "\n3. Delete Employee";
        cout << "\n4. Exit";
        cout << "\nEnter your choice: ";
        cin >> choice;
        switch (choice) {
            case 1: addEmployee(); break;
            case 2: displayEmployee(); break;
            case 3: deleteEmployee(); break;
            case 4: cout << "Exiting...\n"; break;
            default: cout << "Invalid choice.\n";
        }
    } while (choice != 4);
    return 0;
}
