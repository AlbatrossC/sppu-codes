def marks():
    n = int(input("Enter Total no of Students:"))
    global marks
    global absent_count
    absent_count = 0
    marks = []
    for i in range(n):
        mark = input(f"Enter the marks of Student {i+1} , A if Absent:")
        if (mark == "A"):
             absent_count += 1
        else:
            marks.append(int(mark))
    print("Marks of Students:" , marks)

def average():
    total = len(marks)
    sum = 0

    for mark in marks:
        if mark is not None:
            for i in marks:
                sum = sum + i

    print("Average Score of this class:" , (sum/total))

def highest_lowest():
    maximum = max(marks)
    print("The Highest scorer:" , maximum)

    lowest = min(marks)
    print("Lowest Scorer:" , lowest)

def count_absent():
    print("Number of students absent for the test:", absent_count)


def highest_frequency_mark():

    frequency = {}
    for mark in marks:
        if mark in frequency:
            frequency[mark] += 1
        else:
            frequency[mark] = 1

    print("Highest Freuqency:" , frequency)

marks()
average()
highest_lowest()
count_absent()
highest_frequency_mark()

