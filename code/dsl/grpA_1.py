grp_a = ['Alice', 'Bob', 'Charlie', 'David']    # Students who play Cricket
grp_b = ['Bob', 'Eve', 'Charlie']               # Students who play Badminton
grp_c = ['Alice', 'Frank', 'Charlie', 'Eve']    # Students who play Football
total_students = ['Alice', 'Bob', 'Charlie', 'David', 'Eve', 'Frank']  # All students

#a) List of students who play both cricket and badminton
def crick_bad(grp_a , grp_b):
    both = []
    for student in grp_a:
        if student in grp_b:
            both.append(student)
    print("Students who play both Cricket and Badmintion:" , both)

#b) List of students who play either cricket or badminton but not both
def eithercrick_bad(grp_a ,  grp_b):
    either_but_not_both = []
    for student in grp_a:
        if student not in grp_b:
            either_but_not_both.append(student)
    
    for student in grp_b:
        if student not in grp_a and student not in either_but_not_both:
            either_but_not_both.append(student)

    print("List of students who play either cricket or badminton but not both:" , either_but_not_both)

#c) Number of students who play neither cricket nor badminton
def niether(grp_a,grp_b):
    niether =[]
    for student in total_students:
        if student not in grp_a and student not in grp_b:
            niether.append(student)
    print("Number of students who play neither cricket nor badminton:" , niether)


# d) Number of students who play cricket and football but not badminton
def cric_foot_no_bad(grp_a , grp_b , grp_c , total_students):
    cric_foot_no_bad = []
    for students in total_students:
        if students in grp_a and students in grp_c:
            if students not in grp_b:
                cric_foot_no_bad.append(students)
    print("students who play cricket and football but not badminton:" , cric_foot_no_bad)

crick_bad(grp_a , grp_b)
eithercrick_bad(grp_a , grp_b)
niether(grp_a ,grp_b)
cric_foot_no_bad(grp_a,grp_b, grp_c , total_students)

