# a) Students who play both cricket and badminton
def crick_bad(grp_a, grp_b):
    both = []
    for student in grp_a:
        if student in grp_b:
            both.append(student)
    print("Students who play both Cricket and Badminton:", both)

# b) Students who play either cricket or badminton but not both
def eithercrick_bad(grp_a, grp_b):
    either_but_not_both = []
    for student in grp_a:
        if student not in grp_b:
            either_but_not_both.append(student)
    for student in grp_b:
        if student not in grp_a and student not in either_but_not_both:
            either_but_not_both.append(student)
    print("List of students who play either cricket or badminton but not both:", either_but_not_both)

# c) Students who play neither cricket nor badminton
def neither(grp_a, grp_b):
    neither = []
    for student in total_students:
        if student not in grp_a and student not in grp_b:
            neither.append(student)
    print("Number of students who play neither cricket nor badminton:", neither)

# d) Students who play cricket and football but not badminton
def cric_foot_no_bad(grp_a, grp_b, grp_c, total_students):
    cric_foot_no_bad = []
    for students in total_students:
        if students in grp_a and students in grp_c:
            if students not in grp_b:
                cric_foot_no_bad.append(students)
    print("Students who play cricket and football but not badminton:", cric_foot_no_bad)

grp_a = ['Alice', 'Bob', 'Charlie', 'David']
grp_b = ['Bob', 'Eve', 'Charlie']
grp_c = ['Alice', 'Frank', 'Charlie', 'Eve']
total_students = ['Alice', 'Bob', 'Charlie', 'David', 'Eve', 'Frank']


crick_bad(grp_a, grp_b)
eithercrick_bad(grp_a, grp_b)
neither(grp_a, grp_b)
cric_foot_no_bad(grp_a, grp_b, grp_c, total_students)
