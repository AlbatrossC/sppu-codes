#include <iostream>
using namespace std;

// Node definition for threaded binary tree
struct Node {
    int data;
    Node* left;
    Node* right;
    bool isThreaded;  // True if the right pointer points to the in-order successor

    Node(int val) : data(val), left(nullptr), right(nullptr), isThreaded(false) {}
};

// Function to insert a new node in a binary tree
Node* insert(Node* root, int val) {
    if (!root) 
        return new Node(val);
    if (val < root->data)
        root->left = insert(root->left, val);
    else
        root->right = insert(root->right, val);
    return root;
}

// Function to convert a binary tree to a threaded binary tree
void createThreaded(Node* root, Node*& prev) {
    if (!root) 
        return;

    // Recursively process the left subtree
    createThreaded(root->left, prev);

    // If the left child is NULL, link it to the in-order predecessor
    if (!root->left && prev) {
        root->left = prev;
        root->isThreaded = true;
    }

    // If the previous node has no right child, link it to the current node (successor)
    if (prev && !prev->right) {
        prev->right = root;
        prev->isThreaded = true;
    }

    // Update the previous node to the current node
    prev = root;

    // Recursively process the right subtree
    createThreaded(root->right, prev);
}

// Function to traverse a threaded binary tree in in-order
void inorderThreaded(Node* root) {
    if (!root) 
        return;

    // Go to the leftmost node
    Node* current = root;
    while (current->left && !current->isThreaded)
        current = current->left;

    // Traverse the tree using threading
    while (current) {
        cout << current->data << " ";

        // If the node is threaded, move to the in-order successor
        if (current->isThreaded)
            current = current->right;
        else {
            // Otherwise, move to the leftmost node of the right subtree
            current = current->right;
            while (current && current->left && !current->isThreaded)
                current = current->left;
        }
    }
}

int main() {
    Node* root = nullptr;

    // Insert nodes into the binary tree
    int values[] = {50, 30, 70, 20, 40, 60, 80};
    for (int val : values)
        root = insert(root, val);

    // Convert the binary tree to a threaded binary tree
    Node* prev = nullptr;
    createThreaded(root, prev);

    cout << "In-order traversal of the threaded binary tree: ";
    inorderThreaded(root);
    cout << endl;

    return 0;
}
