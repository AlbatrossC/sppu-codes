#include <iostream>
#include <string>

using namespace std;

struct Member {
    string prn;
    string name;
    Member* next;

    Member(const string& prn, const string& name) {
        this->prn = prn;
        this->name = name;
        this->next = nullptr;
    }
};

class PinnacleClub {
private:
    Member* president;
    Member* secretary;
    Member* head;
    int memberCount;

public:
    PinnacleClub() {
        president = new Member("PRESIDENT_PRN", "President");
        secretary = new Member("SECRETARY_PRN", "Secretary");
        head = nullptr;
        memberCount = 0;
        president->next = secretary;
    }

    ~PinnacleClub() {
        clearList();
        delete president;
        delete secretary;
    }

    void clearList() {
        Member* current = head;
        while (current) {
            Member* temp = current;
            current = current->next;
            delete temp;
        }
        head = nullptr;
        memberCount = 0;
    }

    void addMember(const string& prn, const string& name) {
        Member* newMember = new Member(prn, name);
        if (!head) {
            head = newMember;
        } else {
            Member* current = head;
            while (current->next != secretary) {
                current = current->next;
            }
            current->next = newMember;
        }
        newMember->next = secretary;
        memberCount++;
    }

    void deleteMember(const string& prn) {
        if (!head) return;

        Member* current = head;
        Member* previous = nullptr;

        while (current != secretary) {
            if (current->prn == prn) {
                if (previous) {
                    previous->next = current->next;
                } else {
                    head = current->next; // Deleting head member
                }
                delete current;
                memberCount--;
                return;
            }
            previous = current;
            current = current->next;
        }
    }

    int totalMembers() const {
        return memberCount;
    }

    void displayMembers() const {
        if (!head) {
            cout << "No members in the club." << endl;
            return;
        }

        Member* current = head;
        while (current != secretary) {
            cout << "PRN: " << current->prn << ", Name: " << current->name << endl;
            current = current->next;
        }
    }

    void concatenate(PinnacleClub& other) {
        if (head == nullptr) {
            head = other.head;
        } else {
            Member* current = head;
            while (current->next != secretary) {
                current = current->next;
            }
            current->next = other.head;
        }
        other.head = nullptr; 
        memberCount += other.memberCount; 
        other.memberCount = 0; 
    }
};

int main() {
    PinnacleClub divisionA;
    PinnacleClub divisionB;

    int choice;
    string prn, name;

    do {
        cout << "\n1. Add Member (Division A)\n2. Delete Member (Division A)\n3. Display Members (Division A)\n";
        cout << "4. Add Member (Division B)\n5. Delete Member (Division B)\n6. Display Members (Division B)\n";
        cout << "7. Concatenate Divisions\n8. Total Members in Division A\n9. Total Members in Division B\n";
        cout << "10. Exit\n";
        cout << "Enter your choice: ";
        cin >> choice;

        switch (choice) {
            case 1:
                cout << "Enter PRN: ";
                cin >> prn;
                cout << "Enter Name: ";
                cin >> name;
                divisionA.addMember(prn, name);
                break;
            case 2:
                cout << "Enter PRN to delete: ";
                cin >> prn;
                divisionA.deleteMember(prn);
                break;
            case 3:
                divisionA.displayMembers();
                break;
            case 4:
                cout << "Enter PRN: ";
                cin >> prn;
                cout << "Enter Name: ";
                cin >> name;
                divisionB.addMember(prn, name);
                break;
            case 5:
                cout << "Enter PRN to delete: ";
                cin >> prn;
                divisionB.deleteMember(prn);
                break;
            case 6:
                divisionB.displayMembers();
                break;
            case 7:
                divisionA.concatenate(divisionB);
                break;
            case 8:
                cout << "Total Members in Division A: " 
                     << divisionA.totalMembers() 
                     << endl;
                break;
            case 9:
                cout << "Total Members in Division B: " 
                     << divisionB.totalMembers() 
                     << endl;
                break;
            case 10:
                cout << "Exiting program." << endl;
                break;
            default:
                cout << "Invalid choice." << endl;
        }
    } while (choice != 10);

    return 0;
}
