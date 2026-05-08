import pandas as pd
import numpy as np
import os
import urllib.request
from sklearn.preprocessing import MinMaxScaler

file_name = "titanic.csv"
url = "https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv"

if os.path.exists(file_name):
    print("Dataset already Downloaded.")
else:
    urllib.request.urlretrieve(url, file_name)

# Load Dataset
df = pd.read_csv(file_name)

print("\nFirst 5 rows of dataset:")
print(df.head())

# Data Preprocessing

# Check missing values
print("\nMissing Values:")
print(df.isnull().sum())

# Dataset statistics
print("\nStatistical Summary:")
print(df.describe())

# Dataset dimensions
print("\nDataset Dimensions (rows, columns):")
print(df.shape)

# Dataset information
print("\nDataset Information:")
print(df.info())

#Data Formatting and Data Normalization

# Check data types
print("\nData Types Before Conversion:")
print(df.dtypes)

# Convert categorical variables
df['Sex'] = df['Sex'].astype('category')
df['Embarked'] = df['Embarked'].astype('category')

print("\nData Types After Conversion:")
print(df.dtypes)

# Handle missing values
df['Age'] = df['Age'].fillna(df['Age'].mean())
df['Embarked'] = df['Embarked'].fillna(df['Embarked'].mode()[0])

# Normalize numerical columns
scaler = MinMaxScaler()
df[['Age', 'Fare']] = scaler.fit_transform(df[['Age', 'Fare']])

print("\nNormalized Values (Age and Fare):")
print(df[['Age','Fare']].head())

# 6. Convert categorical variables to numerical

# Convert Sex to numeric
df['Sex'] = df['Sex'].cat.codes

# One-hot encoding for Embarked
df = pd.get_dummies(df, columns=['Embarked'])

print("\nDataset After Converting Categorical Variables:")
print(df.head())

print("\nFinal Dataset Dimensions:")
print(df.shape)