import pandas as pd
from sklearn.cluster import AgglomerativeClustering
from sklearn.preprocessing import StandardScaler

# Load your data
df = pd.read_csv("weather_only.csv")
df.fillna({'column_name': 'temp_value'}, inplace=True)

# Assume 'traffic' is the feature you want to cluster on
features = df[['temp_value']]

# Standardize the data
scaler = StandardScaler()
X_scaled = scaler.fit_transform(features)

# Apply Agglomerative Clustering
clustering = AgglomerativeClustering(n_clusters=3, linkage='average')
df['cluster'] = clustering.fit_predict(X_scaled)
# cluster_names = {0: 'medium delay', 1: 'High delay', 2: 'Low delay'}

# Map the numeric cluster labels to custom names
# df['cluster_name'] = df['cluster_label'].map(cluster_names)

# Save the clustered data to a new CSV file
data = df.sort_values(by='temp_value')
data.to_csv('agglo_temp.csv', index=False)

print("Clustering completed and saved to csv")
