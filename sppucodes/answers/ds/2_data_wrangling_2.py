import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from scipy.stats import zscore

# load dataset
df = pd.read_csv("data.csv")

# display dataset
print("Dataset:\n")
print(df)

# check missing values
print("\nMissing Values:")
print(df.isnull().sum())

# fill missing values
df["Age"] = df["Age"].fillna(df["Age"].mean())
df["Attendance"] = df["Attendance"].fillna(df["Attendance"].median())

print("\nDataset after handling missing values:\n")
print(df)

# boxplot for outlier detection
df[['Age','GPA','Test_Score','Attendance']].boxplot()
plt.title("Boxplot")
plt.show()

# detect outliers using z-score
z = np.abs(zscore(df[['Age','GPA','Test_Score','Attendance']]))
df = df[(z < 3).all(axis=1)]

print("\nDataset after removing outliers:\n")
print(df)

# scatter plot
plt.scatter(df['GPA'], df['Test_Score'])
plt.xlabel("GPA")
plt.ylabel("Test Score")
plt.show()

# normalization
scaler = MinMaxScaler()
df[['Age','GPA','Test_Score','Attendance']] = scaler.fit_transform(
    df[['Age','GPA','Test_Score','Attendance']]
)

print("\nDataset after normalization:\n")
print(df)

# skewness
print("\nSkewness:")
print(df[['Age','GPA','Test_Score','Attendance']].skew())