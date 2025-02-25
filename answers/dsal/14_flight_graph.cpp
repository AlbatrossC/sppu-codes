#include <iostream>
#include <unordered_map>
#include <vector>
#include <queue>

using namespace std;

class Graph {
private:
    unordered_map<string, vector<pair<string, int>>> adjList;

public:
    void addEdge(string u, string v, int weight) {
        adjList[u].push_back({v, weight});
        adjList[v].push_back({u, weight}); // Since it's an undirected graph
    }

    void display() {
        cout << "Adjacency List Representation of Graph:\n";
        for (auto &pair : adjList) {
            cout << pair.first << " -> ";
            for (auto &neighbor : pair.second) {
                cout << "(" << neighbor.first << ", " << neighbor.second << " min) ";
            }
            cout << endl;
        }
    }

    void DFSHelper(string node, unordered_map<string, bool> &visited) {
        visited[node] = true;
        for (auto &neighbor : adjList[node]) {
            if (!visited[neighbor.first]) {
                DFSHelper(neighbor.first, visited);
            }
        }
    }

    bool isConnected() {
        if (adjList.empty()) return false;

        unordered_map<string, bool> visited;
        for (auto &pair : adjList) visited[pair.first] = false;

        auto startNode = adjList.begin()->first;
        DFSHelper(startNode, visited);

        for (auto &pair : visited) {
            if (!pair.second) return false;
        }
        return true;
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
