#include <iostream>
#include <cstring>
#include <exception>

using namespace std;

// Forward declaration of friend class
class DisplayStudent;

// Class definition for Student
class Student {
private:
    string name;
    int roll_no;
    string class_name;
    char division;
    string dob;
    string blood_group;
    string contact_address;
    string telephone_no;
    string driving_license;

public:
    // Static variable to track student count
    static int count;

    // Default constructor
    Student() {
        name = "N/A";
        roll_no = 0;
        class_name = "N/A";
        division = 'N';
        dob = "N/A";
        blood_group = "N/A";
        contact_address = "N/A";
        telephone_no = "N/A";
        driving_license = "N/A";
        count++;
    }

    // Parameterized constructor
    Student(string name, int roll_no, string class_name, char division, string dob,
            string blood_group, string contact_address, string telephone_no, string driving_license) {
        this->name = name;
        this->roll_no = roll_no;
        this->class_name = class_name;
        this->division = division;
        this->dob = dob;
        this->blood_group = blood_group;
        this->contact_address = contact_address;
        this->telephone_no = telephone_no;
        this->driving_license = driving_license;
        count++;
    }

    // Copy constructor
    Student(const Student &obj) {
        name = obj.name;
        roll_no = obj.roll_no;
        class_name = obj.class_name;
        division = obj.division;
        dob = obj.dob;
        blood_group = obj.blood_group;
        contact_address = obj.contact_address;
        telephone_no = obj.telephone_no;
        driving_license = obj.driving_license;
        count++;
    }

    // Destructor
    ~Student() {
        cout << "Destructor called for student: " << name << endl;
        count--;
    }

    // Inline function to display student information
    inline void display() {
        cout << "Name: " << name << endl;
        cout << "Roll Number: " << roll_no << endl;
        cout << "Class: " << class_name << endl;
        cout << "Division: " << division << endl;
        cout << "Date of Birth: " << dob << endl;
        cout << "Blood Group: " << blood_group << endl;
        cout << "Contact Address: " << contact_address << endl;
        cout << "Telephone Number: " << telephone_no << endl;
        cout << "Driving License Number: " << driving_license << endl;
        cout << "------------------------------" << endl;
    }

    // Friend function to access private members
    friend class DisplayStudent;

    // Static function to display total count of students
    static void showCount() {
        cout << "Total number of students: " << count << endl;
    }

    // Function to input student details from user
    void inputDetails() {
        cout << "Enter student's name: ";
        getline(cin, name);
        cout << "Enter roll number: ";
        cin >> roll_no;
        cin.ignore(); // To consume the newline left by cin
        cout << "Enter class: ";
        getline(cin, class_name);
        cout << "Enter division (single character): ";
        cin >> division;
        cin.ignore();
        cout << "Enter date of birth (dd-mm-yyyy): ";
        getline(cin, dob);
        cout << "Enter blood group: ";
        getline(cin, blood_group);
        cout << "Enter contact address: ";
        getline(cin, contact_address);
        cout << "Enter telephone number: ";
        getline(cin, telephone_no);
        cout << "Enter driving license number: ";
        getline(cin, driving_license);
    }
};

// Initialize static member
int Student::count = 0;

// Friend class to display student data
class DisplayStudent {
public:
    void showDetails(Student &s) {
        cout << "Displaying details from friend class:" << endl;
        cout << "Name: " << s.name << endl;
        cout << "Roll No: " << s.roll_no << endl;
    }
};

int main() {
    int num_students;

    // Ask the user how many students they want to input
    cout << "Enter the number of students: ";
    cin >> num_students;
    cin.ignore(); // Ignore the newline after cin

    // Dynamically allocate an array of student objects
    Student **students = new Student*[num_students];

    // Loop to get details of each student
    try {
        for (int i = 0; i < num_students; ++i) {
            cout << "\nEnter details for Student " << i + 1 << ":\n";
            students[i] = new Student();  // Dynamic allocation for each student
            students[i]->inputDetails();  // Get user input
        }

        // Display details of each student
        for (int i = 0; i < num_students; ++i) {
            cout << "\nDetails for Student " << i + 1 << ":\n";
            students[i]->display();
        }

        // Display total student count using static function
        Student::showCount();

        // Delete dynamically allocated student objects
        for (int i = 0; i < num_students; ++i) {
            delete students[i];
        }

        // Delete the array itself
        delete[] students;

    } catch (bad_alloc &e) {
        cout << "Memory allocation failed: " << e.what() << endl;
    }

    return 0;
}
