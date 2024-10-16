import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.cluster import AgglomerativeClustering
import numpy as np

def mult_delay(csvfile, clustering):
    # Load the original CSV file
    df = pd.read_csv(csvfile)

    # Add a column to retain the original order
    df['original_index'] = df.index

    # Filter rows where label is 'a7' or 'a1'
    df_a7 = df[df['label'] == 'a7'].copy()
    df_a1 = df[df['label'] == 'a1'].copy()

    # Ensure numeric columns for clustering (convert temp_value, pressure_value, and humidity_value to numeric)
    df_a7['temp_value'] = pd.to_numeric(df_a7['temp_value'], errors='coerce')
    df_a7['pressure_value'] = pd.to_numeric(df_a7['pressure_value'], errors='coerce')
    df_a7['humidity_value'] = pd.to_numeric(df_a7['humidity_value'], errors='coerce')

    # Remove rows with NaN values after conversion (those that couldn't be converted to numeric)
    df_a7 = df_a7.dropna(subset=['temp_value', 'pressure_value', 'humidity_value'])

    # Handle missing values (fill NaN with the mean of the respective column)
    df_a7['temp_value'].fillna(df_a7['temp_value'].mean(), inplace=True)
    df_a7['pressure_value'].fillna(df_a7['pressure_value'].mean(), inplace=True)
    df_a7['humidity_value'].fillna(df_a7['humidity_value'].mean(), inplace=True)

    # Clustering for 'a7'
    if not df_a7.empty:
        # Standardize the data for temp_value, pressure_value, and humidity_value
        scaler_a7 = StandardScaler()
        X_a7_scaled = scaler_a7.fit_transform(df_a7[['temp_value', 'pressure_value', 'humidity_value']])

        # Perform K-Means clustering
        if clustering == "K means":
            kmeans_a7 = KMeans(n_clusters=3, random_state=42)
            df_a7['cluster_label'] = kmeans_a7.fit_predict(X_a7_scaled)

            # Get the centroids (center points of each cluster)
            centroids = kmeans_a7.cluster_centers_

            # Compute the mean of each centroid to determine overall cluster values
            centroid_means = np.mean(centroids, axis=1)

            # Sort the clusters based on the centroid means
            sorted_cluster_indices = np.argsort(centroid_means)

            # Assign names based on the sorted centroids
            a7_cluster_names = {sorted_cluster_indices[0]: 'low weather',
                                sorted_cluster_indices[1]: 'moderate weather',
                                sorted_cluster_indices[2]: 'high weather'}
        df_a7['cluster_name'] = df_a7['cluster_label'].replace(a7_cluster_names)

    df_a1['delay'] = pd.to_numeric(df_a1['delay'], errors='coerce')
    df_a1 = df_a1.dropna(subset=['delay'])

    # Cluster for 'a1' remains the same as your previous logic
    if not df_a1.empty:
        # Standardize the data
        scaler_a1 = StandardScaler()
        X_a1_scaled = scaler_a1.fit_transform(df_a1[['delay']])

        # Choose clustering method based on the 'clustering' variable
        if clustering == "K means":
            kmeans_a1 = KMeans(n_clusters=3, random_state=42)
            df_a1['cluster_label'] = kmeans_a1.fit_predict(X_a1_scaled)

            # Get the centroids for the delay clusters
            centroids_a1 = kmeans_a1.cluster_centers_

            # Sort the centroids to determine the relative delay clusters (low, moderate, high)
            sorted_cluster_indices_a1 = np.argsort(centroids_a1.flatten())

            # Assign dynamic names to clusters based on sorted centroids
            a1_cluster_names = {sorted_cluster_indices_a1[0]: 'Low delay',
                                sorted_cluster_indices_a1[1]: 'Moderate delay',
                                sorted_cluster_indices_a1[2]: 'High delay'}


        elif clustering == "Agglomerative":
                agglomerative_a1 = AgglomerativeClustering(n_clusters=3, linkage='average')
                df_a1['cluster_label'] = agglomerative_a1.fit_predict(X_a1_scaled)
                a1_cluster_names = {0: 'Cluster 1', 1: 'Cluster 2', 2: 'Cluster 3'}

        else:
            print(f"Unsupported clustering method: {clustering}")

        # Apply the mapping to the cluster labels
        df_a1['cluster_name'] = df_a1['cluster_label'].replace(a1_cluster_names)
    else:
        print("Skipping clustering for df_a1 due to empty dataset.")

    # Combine the results back into one DataFrame without sorting by cluster label
    df_combined = pd.concat([df_a7, df_a1])

    # Sort by the original order (based on 'original_index')
    df_combined = df_combined.sort_values(by='original_index')

    # Drop the 'original_index' column
    df_combined = df_combined.drop(columns=['original_index'])
    df_combined = df_combined.rename(columns={
        'cluster_name': 'concept:name',
        'timestamp': 'time:timestamp'
    })

    # Save the clustered data to a new CSV file
    output_file = "mult_delay.csv"
    df_combined.to_csv(output_file, index=False)
    return output_file
