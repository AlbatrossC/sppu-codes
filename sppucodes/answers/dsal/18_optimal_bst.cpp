#include <iostream>
#include <climits>

using namespace std;

int sum(int freq[], int low, int high) {
    int result = 0;
    for (int i = low; i <= high; i++) {
        result += freq[i];
    }
    return result;
}

int minCostBST(int keys[], int freq[], int n) {
    int cost[n][n];

    for (int i = 0; i < n; i++) {
        cost[i][i] = freq[i];
    }

    for (int length = 2; length <= n; length++) {
        for (int i = 0; i <= n - length; i++) {
            int j = i + length - 1;
            cost[i][j] = INT_MAX;

            for (int r = i; r <= j; r++) {
                int leftCost;
                if (r > i) {
                    leftCost = cost[i][r - 1];
                } else {
                    leftCost = 0;
                }

                int rightCost;
                if (r < j) {
                    rightCost = cost[r + 1][j];
                } else {
                    rightCost = 0;
                }

                int totalCost = leftCost + rightCost + sum(freq, i, j);

                if (totalCost < cost[i][j]) {
                    cost[i][j] = totalCost;
                }
            }
        }
    }

    return cost[0][n - 1];
}

int main() {
    int keys[] = {10, 20, 30};
    int freq[] = {34, 8, 50};
    int n = sizeof(keys) / sizeof(keys[0]);

    cout << "Cost of Optimal BST is: " << minCostBST(keys, freq, n) << endl;

    return 0;
}
