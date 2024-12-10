#include <iostream>
#include <map>
#include <string>
using namespace std;

int main() {
    map<string, long long> statePopulations = {
        {"California", 39538223},
        {"Texas", 29145505},
        {"Florida", 21538187},
        {"New York", 20201249},
        {"Illinois", 12812508}
    };

    string stateName;
    cout << "Enter the state name to find its population: ";
    getline(cin, stateName);

    auto it = statePopulations.find(stateName);
    if (it != statePopulations.end()) {
        cout << "The population of " << stateName << " is " << it->second << ".\n";
    } else {
        cout << "State not found. Please check the name and try again.\n";
    }

    return 0;
}
