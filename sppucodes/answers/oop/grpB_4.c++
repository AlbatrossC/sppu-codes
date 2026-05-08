#include <iostream>
#include <fstream>
#include <string>

using namespace std;

int main() {
    const char* filename = "try.txt";

    // Create and write to the file
    ofstream outFile(filename);
    outFile << "Trying out new ways to create a file.";
    outFile.close();

    // Read and display the content of the file
    ifstream inFile(filename);
    cout << "Content of the File:\n";
    cout << inFile.rdbuf();
    inFile.close();

    return 0;
}
