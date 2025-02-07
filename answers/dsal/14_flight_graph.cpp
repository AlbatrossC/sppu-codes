#include <iostream>
#include <vector>
using namespace std;

class Graph {
private:
    vector<vector<int>> adjMatrix;
    int numVertices;

public:
    Graph(int vertices) {
        numVertices = vertices;
        adjMatrix.resize(vertices, vector<int>(vertices, 0));
    }

    void addEdge(int u, int v) {
        if (u >= 0 && u < numVertices && v >= 0 && v < numVertices) {
            adjMatrix[u][v] = 1;
            adjMatrix[v][u] = 1;
            cout << "Edge added between " << u << " and " << v << ".\n";
        } else {
            cout << "Invalid vertices.\n";
        }
    }

    void removeEdge(int u, int v) {
        if (u >= 0 && u < numVertices && v >= 0 && v < numVertices) {
            adjMatrix[u][v] = 0;
            adjMatrix[v][u] = 0;
            cout << "Edge removed between " << u << " and " << v << ".\n";
        } else {
            cout << "Invalid vertices.\n";
        }
    }

    void display() const {
        cout << "Adjacency Matrix:\n";
        for (int i = 0; i < numVertices; ++i) {
            for (int j = 0; j < numVertices; ++j) {
                cout << adjMatrix[i][j] << " ";
            }
            cout << endl;
        }
    }

    void DFS(int start) {
        vector<bool> visited(numVertices, false);
        cout << "DFS Traversal: ";
        dfsHelper(start, visited);
        cout << endl;
    }

    void BFS(int start) {
        vector<bool> visited(numVertices, false);
        vector<int> queue;

        visited[start] = true;
        queue.push_back(start);

        cout << "BFS Traversal: ";
        while (!queue.empty()) {
            int current = queue.front();
            queue.erase(queue.begin());
            cout << current << " ";

            for (int i = 0; i < numVertices; ++i) {
                if (adjMatrix[current][i] == 1 && !visited[i]) {
                    visited[i] = true;
                    queue.push_back(i);
                }
            }
        }
        cout << endl;
    }

private:
    void dfsHelper(int vertex, vector<bool>& visited) {
        visited[vertex] = true;
        cout << vertex << " ";

        for (int i = 0; i < numVertices; ++i) {
            if (adjMatrix[vertex][i] == 1 && !visited[i]) {
                dfsHelper(i, visited);
            }
        }
    }
};

int main() {
    int vertices = 5;
    Graph g(vertices);

    g.addEdge(0, 1);
    g.addEdge(0, 2);
    g.addEdge(1, 3);
    g.addEdge(1, 4);
    g.addEdge(3, 4);

    g.display();

    g.DFS(0);
    g.BFS(0);

    g.removeEdge(1, 4);
    g.display();

    return 0;
}
