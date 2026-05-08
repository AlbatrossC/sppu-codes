import pandas as pd

iris = pd.read_csv("iris.csv")
print(iris.head())

#  Group by species
grouped = iris.groupby("species")

# Mean values
print("Mean values for each species:\n")
print(grouped.mean())

# Standard deviation
print("Standard deviation for each species:\n")
print(grouped.std())

# Percentiles for each species
print("Percentiles for each species:\n")
percentiles = grouped.quantile([0.25, 0.5, 0.75])
print(percentiles)
