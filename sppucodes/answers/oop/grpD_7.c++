#include <iostream>
#include <map>
using namespace std;

int main() {
    map<string, long long> statePopulation = {
        {"Uttar Pradesh", 231502578},
        {"Maharashtra", 123144223},
        {"Bihar", 127104093},
        {"West Bengal", 100671234},
        {"Madhya Pradesh", 84935639}
    };

    string stateName;
    cout << "Enter the name of the state to find its population: ";
    getline(cin, stateName);

    if (statePopulation.find(stateName) != statePopulation.end()) {
        cout << "The population of " << stateName << " is " << statePopulation[stateName] << "." << endl;
    } else {
        cout << "State not found." << endl;
    }

    return 0;
}
