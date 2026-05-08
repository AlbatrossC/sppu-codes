// This code has been updated. Check github if you want the previous code at:https://github.com/AlbatrossC/sppu-codes/commits/main/answers/dsal/19_dictionary_avl.cpp

#include <iostream>
#include <string>
using namespace std;

// Node structure for AVL Tree
struct Node {
    string keyword;
    string meaning;
    Node* left;
    Node* right;
    int height;

    Node(string k, string m) {
        keyword = k;
        meaning = m;
        left = nullptr;
        right = nullptr;
        height = 1;
    }
};

// Utility functions
int height(Node* node) {
    if (node != nullptr)
        return node->height;
    else
        return 0;
}

int max(int a, int b) {
    if (a > b)
        return a;
    else
        return b;
}

void updateHeight(Node* node) {
    node->height = 1 + max(height(node->left), height(node->right));
}

int getBalance(Node* node) {
    if (node != nullptr)
        return height(node->left) - height(node->right);
    else
        return 0;
}

// Rotations
Node* rightRotate(Node* y) {
    Node* x = y->left;
    Node* T2 = x->right;
    x->right = y;
    y->left = T2;
    updateHeight(y);
    updateHeight(x);
    return x;
}

Node* leftRotate(Node* x) {
    Node* y = x->right;
    Node* T2 = y->left;
    y->left = x;
    x->right = T2;
    updateHeight(x);
    updateHeight(y);
    return y;
}

Node* leftRightRotate(Node* z) {
    z->left = leftRotate(z->left);
    return rightRotate(z);
}

Node* rightLeftRotate(Node* z) {
    z->right = rightRotate(z->right);
    return leftRotate(z);
}

// Insertion
Node* insert(Node* root, string key, string meaning) {
    if (root == nullptr)
        return new Node(key, meaning);

    if (key < root->keyword)
        root->left = insert(root->left, key, meaning);
    else if (key > root->keyword)
        root->right = insert(root->right, key, meaning);
    else {
        cout << "Keyword already exists.\n";
        return root;
    }

    updateHeight(root);
    int balance = getBalance(root);

    // Rebalancing
    if (balance > 1) {
        if (key < root->left->keyword)
            return rightRotate(root);  // LL
        else
            return leftRightRotate(root);  // LR
    }

    if (balance < -1) {
        if (key > root->right->keyword)
            return leftRotate(root);  // RR
        else
            return rightLeftRotate(root);  // RL
    }

    return root;
}

// Find minimum node
Node* findMin(Node* node) {
    while (node->left != nullptr)
        node = node->left;
    return node;
}

// Deletion
Node* deleteNode(Node* root, string key) {
    if (root == nullptr)
        return root;

    if (key < root->keyword)
        root->left = deleteNode(root->left, key);
    else if (key > root->keyword)
        root->right = deleteNode(root->right, key);
    else {
        Node* temp;
        if (root->left == nullptr && root->right == nullptr) {
            delete root;
            return nullptr;
        } else if (root->left == nullptr) {
            temp = root->right;
            delete root;
            return temp;
        } else if (root->right == nullptr) {
            temp = root->left;
            delete root;
            return temp;
        } else {
            temp = findMin(root->right);
            root->keyword = temp->keyword;
            root->meaning = temp->meaning;
            root->right = deleteNode(root->right, temp->keyword);
        }
    }

    updateHeight(root);
    int balance = getBalance(root);

    // Rebalancing
    if (balance > 1) {
        if (getBalance(root->left) >= 0)
            return rightRotate(root);  // LL
        else
            return leftRightRotate(root);  // LR
    }

    if (balance < -1) {
        if (getBalance(root->right) <= 0)
            return leftRotate(root);  // RR
        else
            return rightLeftRotate(root);  // RL
    }

    return root;
}

// Update
bool update(Node* root, string key, string newMeaning) {
    while (root != nullptr) {
        if (key == root->keyword) {
            root->meaning = newMeaning;
            return true;
        } else if (key < root->keyword) {
            root = root->left;
        } else {
            root = root->right;
        }
    }
    return false;
}

// Search with comparisons
bool search(Node* root, string key, int& comparisons) {
    while (root != nullptr) {
        comparisons++;
        if (key == root->keyword) {
            cout << "Found: " << root->meaning << "\n";
            return true;
        } else if (key < root->keyword) {
            root = root->left;
        } else {
            root = root->right;
        }
    }
    cout << "Keyword not found.\n";
    return false;
}

// Inorder traversal
void inorderTraversal(Node* root) {
    if (root == nullptr) return;
    inorderTraversal(root->left);
    cout << root->keyword << ": " << root->meaning << "\n";
    inorderTraversal(root->right);
}

// Main menu
int main() {
    Node* root = nullptr;
    int choice;
    string key, meaning;

    do {
        cout << "\n1. Insert\n2. Delete\n3. Update\n4. Search\n5. Display Dictionary\n6. Max Comparisons\n0. Exit\nChoice: ";
        cin >> choice;

        if (choice == 1) {
            cout << "Enter keyword: ";
            cin >> key;
            cout << "Enter meaning: ";
            cin.ignore();
            getline(cin, meaning);
            root = insert(root, key, meaning);
        }
        else if (choice == 2) {
            cout << "Enter keyword to delete: ";
            cin >> key;
            root = deleteNode(root, key);
        }
        else if (choice == 3) {
            cout << "Enter keyword to update: ";
            cin >> key;
            cout << "Enter new meaning: ";
            cin.ignore();
            getline(cin, meaning);
            if (update(root, key, meaning)) {
                cout << "Updated successfully.\n";
            } else {
                cout << "Keyword not found.\n";
            }
        }
        else if (choice == 4) {
            cout << "Enter keyword to search: ";
            cin >> key;
            int comparisons = 0;
            search(root, key, comparisons);
            cout << "Comparisons made: " << comparisons << "\n";
        }
        else if (choice == 5) {
            cout << "Dictionary contents:\n";
            inorderTraversal(root);
        }
        else if (choice == 6) {
            cout << "Maximum comparisons (tree height): " << height(root) << "\n";
        }
        else if (choice == 0) {
            cout << "Exiting...\n";
        }
        else {
            cout << "Invalid choice.\n";
        }
    } while (choice != 0);

    return 0;
}
