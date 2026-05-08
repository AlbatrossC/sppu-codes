import seaborn as sns
import matplotlib.pyplot as plt

df = sns.load_dataset("titanic")
print(df.head())

# Count of survival (0 = died, 1 = survived)
sns.countplot(x="survived", data=df)
plt.title("Survival Count")
plt.show()

# Survival based on gender
sns.countplot(x="survived", hue="sex", data=df)
plt.title("Survival based on Gender")
plt.show()

# Histogram of Fare
plt.hist(df["fare"], bins=20)
plt.title("Fare Distribution")
plt.xlabel("Fare")
plt.ylabel("Number of Passengers")
plt.show()