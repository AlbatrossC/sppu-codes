// Code is Updated and simplified.
// Previous code: github.com/AlbatrossC/sppu-codes/commits/main/answers/dsal/14_flight_graph.cpp

#include <iostream>
#include <unordered_map>
#include <vector>
using namespace std;

class Graph {
private:
    unordered_map<string, vector<pair<string, int>>> adjList;

public:
    void addEdge(string u, string v, int weight) {
        adjList[u].push_back({v, weight});
        adjList[v].push_back({u, weight});
    }

    void display() {
        cout << "Adjacency list:\n";
        for (auto &pair : adjList) {
            cout << pair.first << " -> ";
            for (auto &nb : pair.second) {
                cout << "(" << nb.first << ", " << nb.second << ") ";
            }
            cout << endl;
        }
    }

    void DFSHelper(const string &node, unordered_map<string, bool> &visited) {
        visited[node] = true;
        for (auto &nb : adjList[node]) {
            if (!visited[nb.first]) {
                DFSHelper(nb.first, visited);
            }
        }
    }

    bool isConnected() {
        if (adjList.empty()) {
            return false;
        }

        unordered_map<string, bool> visited;
        DFSHelper(adjList.begin()->first, visited);

        return visited.size() == adjList.size();
    }
};

int main() {
    Graph g;

    g.addEdge("Pune", "Mumbai", 180);
    g.addEdge("Pune", "Nashik", 210);
    g.addEdge("Mumbai", "Nagpur", 480);
    g.addEdge("Nashik", "Nagpur", 450);

    g.display();

    if (g.isConnected()) {
        cout << "The graph is connected.\n";
    } else {
        cout << "The graph is not connected.\n";
    }

    return 0;
}
