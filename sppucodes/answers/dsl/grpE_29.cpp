#include <iostream>
#include <string>

using namespace std;

struct Job {
    int jobId;
    string jobName;
    Job* next;
};

class JobQueue {
private:
    Job* front;
    Job* rear;

public:
    JobQueue() {
        front = nullptr; 
        rear = nullptr; 
    }

    void addJob(int id, const string& name) {
        Job* newJob = new Job{ id, name, nullptr };
        if (rear == nullptr) {
            front = rear = newJob;
        } else {
            rear->next = newJob;
            rear = newJob;
        }
        cout << "Job added: " << newJob->jobName << " (ID: " << newJob->jobId << ")" << endl;
    }

    void deleteJob() {
        if (front == nullptr) {
            cout << "No jobs to delete!" << endl;
            return;
        }
        Job* temp = front;
        front = front->next;
        if (front == nullptr) {
            rear = nullptr;
        }
        cout << "Job deleted: " << temp->jobName << " (ID: " << temp->jobId << ")" << endl;
        delete temp;
    }

    void displayJobs() const {
        if (front == nullptr) {
            cout << "No jobs in the queue." << endl;
            return;
        }
        Job* current = front;
        cout << "Jobs in queue:" << endl;
        while (current != nullptr) {
            cout << "Job ID: " << current->jobId << ", Job Name: " << current->jobName << endl;
            current = current->next;
        }
    }

    ~JobQueue() {
        while (front != nullptr) {
            deleteJob();
        }
    }
};

int main() {
    JobQueue queue;

    int choice, jobId;
    string jobName;

    do {
        cout << "\n1. Add Job\n2. Delete Job\n3. Display Jobs\n4. Exit\n";
        cout << "Enter your choice: ";
        cin >> choice;

        switch (choice) {
            case 1:
                cout << "Enter Job ID: ";
                cin >> jobId;
                cout << "Enter Job Name: ";
                cin.ignore();
                getline(cin, jobName);
                queue.addJob(jobId, jobName);
                break;
            case 2:
                queue.deleteJob();
                break;
            case 3:
                queue.displayJobs();
                break;
            case 4:
                cout << "Exiting program." << endl;
                break;
            default:
                cout << "Invalid choice. Please try again." << endl;
        }
    } while (choice != 4);

    return 0;
}
