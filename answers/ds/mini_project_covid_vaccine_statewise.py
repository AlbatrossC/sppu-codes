import pandas as pd

# Load dataset
df = pd.read_csv("covid_vaccine_statewise.csv")

# Clean column names
df.columns = df.columns.str.strip()

# Convert date column
df["Updated On"] = pd.to_datetime(df["Updated On"], dayfirst=True)

# Sort values
df = df.sort_values(by=["State", "Updated On"])

# Get latest data for each state
latest = df.groupby("State").last().reset_index()

# Remove India total row
state_data = latest[latest["State"] != "India"]

# First dose state-wise
print("\nFirst Dose (State-wise):")
print(state_data[["State", "First Dose Administered"]])

# Second dose state-wise
print("\nSecond Dose (State-wise):")
print(state_data[["State", "Second Dose Administered"]])

# Total males vaccinated
total_male = state_data["Male (Doses Administered)"].sum()
print("\nTotal Male Vaccinated:", int(total_male))

# Total females vaccinated
total_female = state_data["Female (Doses Administered)"].sum()
print("Total Female Vaccinated:", int(total_female))
