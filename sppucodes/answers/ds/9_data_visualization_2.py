import seaborn as sns
import matplotlib.pyplot as plt

# Load dataset
df = sns.load_dataset("titanic")

# Boxplot
sns.boxplot(x="sex", y="age", hue="survived", data=df)

plt.title("Age Distribution by Gender and Survival")
plt.show()