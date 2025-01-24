#include <iostream>
#include <algorithm> // For std::max
using namespace std;

struct Node {
    int data;
    Node* left;
    Node* right;

    Node(int val) : data(val), left(nullptr), right(nullptr) {}
};

Node* insert(Node* root, int val) {
    if (!root) 
        return new Node(val);
    if (val < root->data)
        root->left = insert(root->left, val);
    else
        root->right = insert(root->right, val);
    return root;
}

void inorder(Node* root) {
    if (!root) 
        return;
    inorder(root->left);
    cout << root->data << " ";
    inorder(root->right);
}

int findHeight(Node* root) {
    if (!root) 
        return 0;
    int leftHeight = findHeight(root->left);
    int rightHeight = findHeight(root->right);
    return 1 + max(leftHeight, rightHeight);
}

int findMin(Node* root) {
    if (!root) 
        return -1;
    while (root->left)
        root = root->left;
    return root->data;
}

void mirror(Node* root) {
    if (!root) 
        return;
    swap(root->left, root->right);
    mirror(root->left);
    mirror(root->right);
}

bool search(Node* root, int val) {
    if (!root) 
        return false;
    if (root->data == val) 
        return true;
    if (val < root->data)
        return search(root->left, val);
    return search(root->right, val);
}

int main() {
    Node* root = nullptr;

    int values[] = {50, 30, 70, 20, 40, 60, 80};
    for (int val : values)
        root = insert(root, val);

    cout << "Inorder traversal of the BST: ";
    inorder(root);
    cout << endl;

    int newNode = 25;
    root = insert(root, newNode);
    cout << "Inorder traversal after inserting " << newNode << ": ";
    inorder(root);
    cout << endl;

    int height = findHeight(root);
    cout << "Number of nodes in the longest path (height): " << height << endl;

    int minValue = findMin(root);
    cout << "Minimum data value in the BST: " << minValue << endl;

    mirror(root);
    cout << "Inorder traversal after mirroring the tree: ";
    inorder(root);
    cout << endl;

    int searchValue = 40;
    bool isFound = search(root, searchValue);
    cout << "Search for " << searchValue << ": " << (isFound ? "Found" : "Not Found") << endl;

    return 0;
}
