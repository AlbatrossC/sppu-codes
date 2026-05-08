import pandas as pd

df = pd.read_csv("data3.csv")
print("Dataset:\n", df)

# Group by categorical variable (Gender)
grouped = df.groupby("Gender")["Income"]

# Calculate statistics
summary = grouped.agg(['mean', 'median', 'min', 'max', 'std'])

print("Summary Statistics (Income grouped by Gender):\n")
print(summary)

# Create list for each category
income_list = grouped.apply(list)

print("\nIncome values grouped by Gender:\n")
print(income_list)