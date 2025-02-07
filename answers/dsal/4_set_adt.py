# Input elements for Set A
total = int(input("Please enter the number of elements in set A: "))
A = []
while total > 0:
    element = int(input("-> "))
    A.append(element)
    total -= 1
print("Set A:", A)

# Remove duplicates from Set A
new_A = []
for i in A:
    if i not in new_A:
        new_A.append(i)
print("Set A without duplication:", new_A)

# Input elements for Set B
total = int(input("Please enter the number of elements in set B: "))
B = []
while total > 0:
    element = int(input("-> "))
    B.append(element)
    total -= 1
print("Set B:", B)

# Remove duplicates from Set B
new_B = []
for i in B:
    if i not in new_B:
        new_B.append(i)
print("Set B without duplication:", new_B)

# Intersection of Set A and Set B
intersection = []
for i in new_A:
    if i in new_B:
        intersection.append(i)
print("The intersection of A and B:", intersection)

# Union of Set A and Set B
union = new_A + new_B
new_union = []
for i in union:
    if i not in new_union:
        new_union.append(i)
print("The union of A and B:", new_union)

# Difference of A - B
A_B = []
for i in new_A:
    if i not in new_B:
        A_B.append(i)
print("A - B:", A_B)

# Difference of B - A
B_A = []
for i in new_B:
    if i not in new_A:
        B_A.append(i)
print("B - A:", B_A)

# Size of Set A
size_A = len(new_A)
print("Size of A:", size_A)

# Size of Set B
size_B = len(new_B)
print("Size of B:", size_B)

# Remove element from Set A
rem_A = int(input("Please enter an element to be removed from A: "))
if rem_A in new_A:
    print(f"Element {rem_A} found in A!")
    new_A2 = []
    for i in new_A:
        if i != rem_A:
            new_A2.append(i)
    print(f"The set A after deletion of {rem_A}: {new_A2}")
else:
    print(f"Element {rem_A} not found in A.")

# Remove element from Set B
rem_B = int(input("Please enter an element to be removed from B: "))
if rem_B in new_B:
    print(f"Element {rem_B} found in B!")
    new_B2 = []
    for i in new_B:
        if i != rem_B:
            new_B2.append(i)
    print(f"The set B after deletion of {rem_B}: {new_B2}")
else:
    print(f"Element {rem_B} not found in B.")

# Check if A is a subset of B
if all(i in new_B2 for i in new_A2):
    print("A is a subset of B")
else:
    print("A is NOT a subset of B")

# Check if B is a subset of A
if all(i in new_A2 for i in new_B2):
    print("B is a subset of A")
else:
    print("B is NOT a subset of A")
