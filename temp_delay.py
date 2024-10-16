import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.cluster import AgglomerativeClustering
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import numpy as np

# when one puts csv file as a parameter then the temp_delay csv will be created
def temp_delay(csvfile, clustering):
    # Load the original CSV file
    df = pd.read_csv(csvfile)

    # Add a column to retain the original order
    df['original_index'] = df.index

    # Filter rows where label is 'a7' or 'a1'
    df_a7 = df[df['label'] == 'a7'].copy()
    df_a1 = df[df['label'] == 'a1'].copy()

    # Debugging: Check how many rows are being filtered
    print("Rows in df_a7:", len(df_a7))
    print("Rows in df_a1:", len(df_a1))

    # Ensure numeric columns for clustering (convert temp_value and delay to numeric)
    df_a7['temp_value'] = pd.to_numeric(df_a7['temp_value'], errors='coerce')
    df_a1['delay'] = pd.to_numeric(df_a1['delay'], errors='coerce')

    # Handle missing values (fill NaN with the mean of the respective column)
    df_a7['temp_value'] = df_a7['temp_value'].fillna(df_a7['temp_value'].mean())
    df_a1['delay'] = df_a1['delay'].fillna(df_a1['delay'].mean())

    # Debugging: Check for NaN values after filling
    print("NaN values in df_a7 temp_value:", df_a7['temp_value'].isna().sum())
    print("NaN values in df_a1 delay:", df_a1['delay'].isna().sum())

    # Check if there are rows left after filtering NaNs
    if df_a7.empty:
        print("Error: No rows in df_a7 after filtering.")
    if df_a1.empty:
        print("Error: No rows in df_a1 after filtering.")

    # Proceed only if there are rows to cluster
    # Clustering for 'a7'
    if not df_a7.empty:
        # Standardize the data
        scaler_a7 = StandardScaler()
        X_a7_scaled = scaler_a7.fit_transform(df_a7[['temp_value']])

        # Choose clustering method based on the 'clustering' variable
        if clustering == "K means":
            kmeans_a7 = KMeans(n_clusters=3, random_state=42)
            df_a7['cluster_label'] = kmeans_a7.fit_predict(X_a7_scaled)

            # Get the centroids for the clusters
            centroids_a7 = kmeans_a7.cluster_centers_

            # Calculate the mean of each centroid (since multiple features are involved)
            centroid_means_a7 = np.mean(centroids_a7, axis=1)

            # Sort the centroid means to identify relative cluster labels (low, moderate, high)
            sorted_cluster_indices_a7 = np.argsort(centroid_means_a7)

            # Assign dynamic names to clusters based on sorted centroids
            a7_cluster_names = {sorted_cluster_indices_a7[0]: 'low temperature',
                                sorted_cluster_indices_a7[1]: 'moderate temperature',
                                sorted_cluster_indices_a7[2]: 'high temperature'}

        elif clustering == "Agglomerative":
            agglomerative_a7 = AgglomerativeClustering(n_clusters=3, linkage='average', compute_full_tree=True)
            df_a7['cluster_label'] = agglomerative_a7.fit_predict(X_a7_scaled)
            a7_cluster_names = {0: 'Cluster 1', 1: 'Cluster 2', 2: 'Cluster 3'}

        else:
            print(f"Unsupported clustering method: {clustering}")

        # Apply the mapping to the cluster labels
        df_a7['cluster_name'] = df_a7['cluster_label'].replace(a7_cluster_names)
    else:
        print("Skipping clustering for df_a7 due to empty dataset.")

    # Cluster according to the input parameter
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
    # df_combined = df_combined.drop(columns=['original_index', 'cluster_label'])

    # Sort by the original order (based on 'original_index')
    df_combined = df_combined.sort_values(by='original_index')

    # Drop the 'original_index' column (optional, if you don't want it in the final CSV)
    df_combined = df_combined.drop(columns=['original_index'])
    df_combined = df_combined.rename(columns={
        'cluster_name': 'concept:name',
        'timestamp': 'time:timestamp'
    })
    # Save the clustered data to a new CSV file
    output_file = "temp_delay.csv"
    df_combined.to_csv(output_file, index=False)
    return output_file

