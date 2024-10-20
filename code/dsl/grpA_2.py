def input_marks():
    """
    Input marks for N students.
    Returns a list of marks and a count of absent students.
    """
    marks = []
    absent_count = 0
    N = int(input("Enter the number of students: "))
    
    for i in range(N):
        mark = input(f"Enter marks for student {i + 1} (or 'A' for absent): ")
        if mark.upper() == 'A':
            absent_count += 1
        else:
            try:
                marks.append(int(mark))
            except ValueError:
                print("Invalid input, please enter a valid mark or 'A' for absent.")
    
    return marks, absent_count

def calculate_average(marks):
    """
    Calculate and return the average score of the class.
    """
    if len(marks) == 0:
        return 0
    return sum(marks) / len(marks)

def find_highest_lowest(marks):
    """
    Find and return the highest and lowest scores.
    """
    if len(marks) == 0:
        return None, None
    return max(marks), min(marks)

def count_absent(absent_count):
    """
    Return the count of absent students.
    """
    return absent_count

def mark_with_highest_frequency(marks):
    """
    Find and return the mark with the highest frequency.
    """
    if len(marks) == 0:
        return None
    
    frequency = {}
    for mark in marks:
        if mark in frequency:
            frequency[mark] += 1
        else:
            frequency[mark] = 1
            
    highest_frequency = max(frequency.values())
    most_frequent_marks = [mark for mark, freq in frequency.items() if freq == highest_frequency]
    
    return most_frequent_marks, highest_frequency

def main():
    marks, absent_count = input_marks()
    
    average = calculate_average(marks)
    highest, lowest = find_highest_lowest(marks)
    absent = count_absent(absent_count)
    frequent_marks, frequency = mark_with_highest_frequency(marks)

    print(f"\nAverage score of the class: {average:.2f}")
    print(f"Highest score: {highest}")
    print(f"Lowest score: {lowest}")
    print(f"Count of students absent: {absent}")
    print(f"Mark(s) with the highest frequency: {frequent_marks} (Frequency: {frequency})")

if __name__ == "__main__":
    main()
    