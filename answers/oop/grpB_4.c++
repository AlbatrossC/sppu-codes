#include <iostream>
#include <fstream>
#include <string>

using namespace std;

int main(){
    const char* filename = "try.txt";

    ofstream outfile(filename);
    outfile << "Trying out new ways to create a file";
    outfile.close();

    ifstream inFile(filename);
    cout<<"Content of File:\n";
    cout <<inFile.rdbuf();
    inFile.close();

    return 0;
}