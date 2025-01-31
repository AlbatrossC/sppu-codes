#include <iostream>
#include <algorithm>

using namespace std;

struct Node {
    int data;
    Node* left;
    Node* right;

    Node(int val) {
        data = val;
        left = nullptr;
        right = nullptr;
    }
};

// Insert a new node in the Binary Search Tree (BST)
Node* insert(Node* root, int val) {
    if (!root)
        return new Node(val);

    // If value is less than root, move to the left subtree
    if (val < root->data)
        root->left = insert(root->left, val);
    // If value is greater, move to the right subtree
    else
        root->right = insert(root->right, val);
    
    return root;
}

// Inorder Traversal (Left, Root, Right)
void inorder(Node* root) {
    if (!root)
        return;

    inorder(root->left);
    cout << root->data << " ";
    inorder(root->right);
}

// Find the height of the binary tree
int findHeight(Node* root) {
    if (!root)
        return 0;

    int leftHeight = findHeight(root->left);
    int rightHeight = findHeight(root->right);

    return 1 + max(leftHeight, rightHeight);
}

// Find the minimum value in the binary tree
int findMin(Node* root) {
    if (!root)
        return -1;

    while (root->left)
        root = root->left;

    return root->data;
}

// Mirror the binary tree (swap left and right subtrees)
void mirror(Node* root) {
    if (!root)
        return;

    swap(root->left, root->right);
    mirror(root->left);
    mirror(root->right);
}

// Search for a value in the binary search tree
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
    int total, val;

    // Input total number of elements to be inserted
    cout << "Enter total number of elements: ";
    cin >> total;

    // Insert elements into the BST
    for (int i = 0; i < total; i++) {
        cout << "Enter value " << i + 1 << ": ";
        cin >> val;
        root = insert(root, val);
    }

    // Inorder traversal of the BST
    cout << "Inorder traversal of the BST: ";
    inorder(root);
    cout << endl;

    // Insert a new node and print the inorder traversal
    int newNode;
    cout << "Enter a value to insert: ";
    cin >> newNode;
    root = insert(root, newNode);

    cout << "Inorder traversal after inserting " << newNode << ": ";
    inorder(root);
    cout << endl;

    // Find and print the height of the tree
    int height = findHeight(root);
    cout << "Height (Number of nodes in the longest path): " << height << endl;

    // Find and print the minimum value in the BST
    int minValue = findMin(root);
    cout << "Minimum value in the BST: " << minValue << endl;

    // Search for a value in the BST
    int searchValue;
    cout << "Enter a value to search: ";
    cin >> searchValue;
    bool isFound = search(root, searchValue);
    cout << "Search for " << searchValue << ": " << (isFound ? "Found" : "Not Found") << endl;

    // Mirror the tree and print the inorder traversal
    mirror(root);
    cout << "Inorder traversal after mirroring the tree: ";
    inorder(root);
    cout << endl;

    return 0;
}
