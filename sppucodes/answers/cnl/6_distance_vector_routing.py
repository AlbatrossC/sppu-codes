# Distance Vector Routing

INF = 999

# Input the routing table for all nodes
def input_routing_table(num_nodes):
    table = []
    for i in range(num_nodes):
        row = []
        for j in range(num_nodes):
            row.append(INF)
        table.append(row) 

    print(f"\nEnter the routing table (use {INF} for no connection):")

    # Print header
    print("\t|", end="")
    for i in range(num_nodes):
        print(f" Node{i+1}", end="\t")
    print()

    print("-------" * (num_nodes + 1))

    # Fill the table
    for i in range(num_nodes):
        print(f"Node{i+1} |\t", end="")
        for j in range(num_nodes):
            table[i][j] = int(input())
    return table


# Compute shortest paths using Bellman-Ford algorithm
def bellman_ford(num_nodes, edge_list, source):
    distances = [INF] * num_nodes
    previous_node = [source] * num_nodes
    distances[source] = 0

    for _ in range(num_nodes - 1):
        for u, v, w in edge_list:
            if distances[u] != INF and distances[u] + w < distances[v]:
                distances[v] = distances[u] + w
                previous_node[v] = u

    return distances, previous_node


# Main function to run distance vector routing
def main():
    num_nodes = int(input("Enter the number of nodes: "))
    routing_table = input_routing_table(num_nodes)

    # Build edge list from routing table
    edge_list = []
    for i in range(num_nodes):
        for j in range(num_nodes):
            if routing_table[i][j] != INF and i != j:
                edge_list.append((i, j, routing_table[i][j]))

    # Run Bellman-Ford for each node as source
    for source in range(num_nodes):
        distances, previous_node = bellman_ford(num_nodes, edge_list, source)
        print(f"\nRouting table for router Node{source+1}:")
        for dest in range(num_nodes):
            if source == dest:
                continue
            if distances[dest] == INF:
                print(f"To Node{dest+1}: No path")
            else:
                print(f"To Node{dest+1}: Cost = {distances[dest]} via Node{previous_node[dest]}")


if __name__ == "__main__":
    main()
