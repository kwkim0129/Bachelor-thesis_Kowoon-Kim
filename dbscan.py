import pandas as pd
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler

# Load the dataset
df = pd.read_csv("weather_only.csv")

# Selecting numeric columns for clustering
X = df[['temp_value']] #'temp_value', 'pressure_value', 'humidity_value',

X = X.fillna(X.mean())

# Normalize the data
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Apply DBSCAN
dbscan = DBSCAN(eps=0.1, min_samples=5)  # You can adjust eps and min_samples
clusters = dbscan.fit_predict(X_scaled)

# Add cluster labels to the original dataframe
df['cluster'] = clusters
unique_clusters = set(clusters) - {-1}  # Exclude noise points (-1)

# Print the number of valid clusters found 
print(f"Number of clusters found: {len(unique_clusters)}")
# Display the resulting clusters
print(df[['case_id', 'label', 'temp_value', 'cluster']])
