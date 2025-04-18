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

// Function to get the height of a node
int height(Node* root) {
    if (root == nullptr)
        return 0;
    else
        return root->height;
}

// Function to get balance factor of a node
int getBalance(Node* root) {
    if (root == nullptr)
        return 0;
    else
        return height(root->left) - height(root->right);
}

// Function to get the maximum of two integers
int max(int a, int b) {
    if (a > b)
        return a;
    else
        return b;
}

// Function to perform right rotation
Node* rightRotate(Node* y) {
    Node* x = y->left;
    Node* T2 = x->right;

    x->right = y;
    y->left = T2;

    y->height = max(height(y->left), height(y->right)) + 1;
    x->height = max(height(x->left), height(x->right)) + 1;

    return x;
}

// Function to perform left rotation
Node* leftRotate(Node* x) {
    Node* y = x->right;
    Node* T2 = y->left;

    y->left = x;
    x->right = T2;

    x->height = max(height(x->left), height(x->right)) + 1;
    y->height = max(height(y->left), height(y->right)) + 1;

    return y;
}

// Function to insert a node in AVL tree
Node* insert(Node* root, string key, string meaning) {
    if (root == nullptr) {
        return new Node(key, meaning);
    }

    if (key < root->keyword) {
        root->left = insert(root->left, key, meaning);
    }
    else if (key > root->keyword) {
        root->right = insert(root->right, key, meaning);
    }
    else {
        cout << "Keyword already exists.\n";
        return root;
    }

    root->height = max(height(root->left), height(root->right)) + 1;

    int balance = getBalance(root);

    if (balance > 1 && key < root->left->keyword) {
        return rightRotate(root);
    }

    if (balance < -1 && key > root->right->keyword) {
        return leftRotate(root);
    }

    if (balance > 1 && key > root->left->keyword) {
        root->left = leftRotate(root->left);
        return rightRotate(root);
    }

    if (balance < -1 && key < root->right->keyword) {
        root->right = rightRotate(root->right);
        return leftRotate(root);
    }

    return root;
}

// Function to search for a keyword in AVL tree
bool search(Node* root, string key, int& comparisons) {
    while (root != nullptr) {
        comparisons++;

        if (key == root->keyword) {
            cout << "Found: " << root->meaning << "\n";
            return true;
        }

        if (key < root->keyword) {
            root = root->left;
        }
        else {
            root = root->right;
        }
    }

    cout << "Keyword not found.\n";
    return false;
}

// Function to update the meaning of a keyword
bool update(Node* root, string key, string newMeaning) {
    while (root != nullptr) {
        if (key == root->keyword) {
            root->meaning = newMeaning;
            return true;
        }

        if (key < root->keyword) {
            root = root->left;
        }
        else {
            root = root->right;
        }
    }

    return false;
}

// Function to find the node with minimum value
Node* findMin(Node* root) {
    while (root->left != nullptr) {
        root = root->left;
    }

    return root;
}

// Function to delete a node from AVL tree
Node* deleteNode(Node* root, string key) {
    if (root == nullptr) {
        return root;
    }

    if (key < root->keyword) {
        root->left = deleteNode(root->left, key);
    }
    else if (key > root->keyword) {
        root->right = deleteNode(root->right, key);
    }
    else {
        if (root->left == nullptr || root->right == nullptr) {
            Node* temp;

            if (root->left != nullptr) {
                temp = root->left;
            }
            else {
                temp = root->right;
            }

            delete root;
            return temp;
        }
        else {
            Node* temp = findMin(root->right);
            root->keyword = temp->keyword;
            root->meaning = temp->meaning;
            root->right = deleteNode(root->right, temp->keyword);
        }
    }

    root->height = max(height(root->left), height(root->right)) + 1;

    int balance = getBalance(root);

    if (balance > 1 && getBalance(root->left) >= 0) {
        return rightRotate(root);
    }

    if (balance > 1 && getBalance(root->left) < 0) {
        root->left = leftRotate(root->left);
        return rightRotate(root);
    }

    if (balance < -1 && getBalance(root->right) <= 0) {
        return leftRotate(root);
    }

    if (balance < -1 && getBalance(root->right) > 0) {
        root->right = rightRotate(root->right);
        return leftRotate(root);
    }

    return root;
}

// Function for inorder traversal (ascending order)
void inorderTraversal(Node* root) {
    if (root == nullptr) {
        return;
    }

    inorderTraversal(root->left);
    cout << root->keyword << ": " << root->meaning << "\n";
    inorderTraversal(root->right);
}

// Main function to run the dictionary AVL tree operations
int main() {
    Node* root = nullptr;
    int choice;
    string key, meaning;

    do {
        cout << "\n1. Insert\n2. Delete\n3. Update\n4. Search\n5. Inorder Traversal\n6. Max Comparisons\n0. Exit\nChoice: ";
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
            bool updated = update(root, key, meaning);
            if (updated) {
                cout << "Updated successfully.\n";
            }
            else {
                cout << "Keyword not found.\n";
            }
        }
        else if (choice == 4) {
            int cmp = 0;
            cout << "Enter keyword to search: ";
            cin >> key;
            search(root, key, cmp);
            cout << "Comparisons: " << cmp << "\n";
        }
        else if (choice == 5) {
            cout << "Dictionary (Inorder Traversal):\n";
            inorderTraversal(root);
        }
        else if (choice == 6) {
            int h = height(root);
            cout << "Maximum comparisons (tree height): " << h << "\n";
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
