import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# load dataset
df = sns.load_dataset("iris")

print("Dataset:\n", df.head())

# features cand types
print("\nFeatures and Data Types:\n")
print(df.dtypes)

# histograms
df.hist(figsize=(8,6))
plt.suptitle("Histograms")
plt.show()

# boxplots
for col in df.columns[:-1]:
    sns.boxplot(y=df[col])
    plt.title(col)
    plt.show()