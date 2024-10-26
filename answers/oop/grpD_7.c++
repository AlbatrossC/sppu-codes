#include <iostream>
#include <map>
#include <string>
using namespace std;

int main()
{

    map<string, long long> statePopulations;

    statePopulations["California"] = 39538223;
    statePopulations["Texas"] = 29145505;
    statePopulations["Florida"] = 21538187;
    statePopulations["New York"] = 20201249;
    statePopulations["Illinois"] = 12812508;

    string statename;
    cout << "Enter the State name to find its population:";
    getline(cin, statename);

    auto it = statePopulations.find(statename);

    if (it != statePopulations.end())
    {
        cout << "The Population of that state is:" << it->second;
    }
    else
    {
        cout << "Not found";
    }

    return 0;
}
