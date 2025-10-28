def selection_sort(a):
    for i in range(len(a)):
        min_idx = i
        for j in range(i+1, len(a)):
            if a[j] < a[min_idx]:
                min_idx = j
        a[i], a[min_idx] = a[min_idx], a[i]
    return a

arr = [64, 25, 12, 22, 11]
print(selection_sort(arr))
