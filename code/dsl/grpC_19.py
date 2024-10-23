#include <iostream>
#include <string>
using namespace std;

struct Node{
    string name;
    string PRN;
    Node* next;

    Node(string n , string p):name(n), PRN(p) , next(nullptr){};
};

class PinnacleClub{
    private:
        Node* head;
        Node* tail;

    public:
        PinnacleClub():head(nullptr) , tail(nullptr) {};
    
        void add_member(string prn , string name){
            Node* newnode = new Node(name , prn);
            if(head == nullptr){
                head = newnode;
                tail = newnode;
            } else{
                tail->next = newnode;
                tail = newnode;
            }
        }

        void add_president(string prn, string name){
            Node* newnode = new Node(name ,prn);
            {
                newnode->next = head  ;
                head = newnode;
            }   
        }

        void add_sec(string name , string prn){
            Node* newNode = new Node(name , prn);
            {
                if (head = nullptr){
                    head = newNode;
                    tail = newNode;
                }
                else{
                    tail->next = newNode;
                    tail=newNode;
                }
            }
        }

        int total(){
            int count = 0;
            Node* current = head;
            while(current != nullptr){
                count ++;
                current   = current-> next;  
            }
            return count;
        }

        void display(){
            Node* current = head;
            while(current!= nullptr){
                cout << "Name:" <<current->name<<endl;
                cout<< "PRN:"<<current->PRN<<endl;
                current = current->next;
            }
        }
        

};


int main() {
    PinnacleClub club;

    string name, prn;
    int n1, n2;

    // Input for first club
    cout << "Enter total number of members for Club 1: ";
    cin >> n1;
    for (int i = 0; i < n1; i++) {
        cout << "Name: ";
        cin >> name;
        cout << "PRN: ";
        cin >> prn;
        club.add_member(prn, name);
    }

    // Input for second club
    cout << "Enter total number of members for Club 2: ";
    cin >> n2;
    for (int i = 0; i < n2; i++) {
        cout << "Name: ";
        cin >> name;
        cout << "PRN: ";
        cin >> prn;
        club.add_member(prn, name);
    }

    // Display all members of the combined club
    cout << "\nMembers of the Combined Club:" << endl;
    club.display();

    cout << "Total Members in the Combined Club: " << club.total() << endl;

    return 0;
}