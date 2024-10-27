import multiprocessing
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans, DBSCAN
from sklearn.cluster import AgglomerativeClustering
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import numpy as np

# clustering: k means, dbscan / clusters = parameter for clustering algorithms
def temp_delay(csvfile, clustering, clusters):
    df = pd.read_csv(csvfile)
    df['original_index'] = df.index # create index internally to keep original index

    # Filter out rows where label is 'a7' or 'a1'
    df_a7 = df[df['label'] == 'a7'].copy()
    df_a1 = df[df['label'] == 'a1'].copy()

    # -------- Debug: Check how many rows are being filtered ( can remove later )
    print("Rows in df_a7:", len(df_a7))
    print("Rows in df_a1:", len(df_a1))
    # --------
    df_a7['temp_value'] = pd.to_numeric(df_a7['temp_value'], errors='coerce')
    df_a1['delay'] = pd.to_numeric(df_a1['delay'], errors='coerce')

    df_a7['temp_value'] = df_a7['temp_value'].fillna(df_a7['temp_value'].mean())
    # df_a1['delay'] = df_a1['delay'].fillna(df_a1['delay'].mean())
    # remove 0.0 and string values in a1
    df_a1 = df_a1[df_a1['delay'] != 0.0]
    df_a1 = df_a1.dropna(subset=['delay'])
    # --------- Debugging: Check for NaN values after filling ( can remove later )
    print("NaN values in df_a7 temp_value:", df_a7['temp_value'].isna().sum())
    print("NaN values in df_a1 delay:", df_a1['delay'].isna().sum())
    if df_a7.empty:
        print("Error: No rows in df_a7 after filtering.")
    if df_a1.empty:
        print("Error: No rows in df_a1 after filtering.")
    # ----------

    # Clustering for 'a7'
    if not df_a7.empty:
        # Standardize the data
        scaler_a7 = StandardScaler()
        X_a7_scaled = scaler_a7.fit_transform(df_a7[['temp_value']])

        # Choose clustering method based on the 'clustering' variable
        if clustering == "K means":
            kmeans_a7 = KMeans(n_clusters=clusters, random_state=42)

            df_a7['cluster_label'] = kmeans_a7.fit_predict(X_a7_scaled)

            # Get the centroids for the clusters and calculate them
            centroids_a7 = kmeans_a7.cluster_centers_
            centroid_means_a7 = np.mean(centroids_a7, axis=1)

            # Sort the centroid means to identify relative cluster labels (low, moderate, high)
            sorted_cluster_indices_a7 = np.argsort(centroid_means_a7)

            # dynamic names to clusters based on sorted centroids
            a7_cluster_names = {}
            for cluster_label in sorted_cluster_indices_a7:
                # Mask to filter the rows for the current cluster
                cluster_mask = (df_a7['cluster_label'] == cluster_label)

                # Calculate min and max temp_value for the current cluster for the naming
                min_value = df_a7.loc[cluster_mask, 'temp_value'].min()
                max_value = df_a7.loc[cluster_mask, 'temp_value'].max()

                a7_cluster_names[cluster_label] = f'temp_{min_value:.2f}_{max_value:.2f}'

        elif clustering == "Agglomerative":
            agglomerative_a7 = AgglomerativeClustering(n_clusters=3, linkage='average', compute_full_tree=True)
            df_a7['cluster_label'] = agglomerative_a7.fit_predict(X_a7_scaled)
            a7_cluster_names = {0: 'Cluster 1', 1: 'Cluster 2', 2: 'Cluster 3'}

        elif clustering == "DBSCAN":
            dbscan_a7 = DBSCAN(eps=clusters, min_samples=5)  # You can adjust eps and min_samples as needed

            df_a7['cluster_label'] = dbscan_a7.fit_predict(X_a7_scaled)
            # Get the unique cluster labels (ignoring noise points labeled as -1)
            unique_clusters_a7 = np.unique(df_a7['cluster_label'])
            unique_clusters_a7 = unique_clusters_a7[unique_clusters_a7 != -1]  # Exclude noise (-1)

            if len(unique_clusters_a7) < 3:
                print(
                    f"Warning: DBSCAN found only {len(unique_clusters_a7)} a7 clusters. Adjusting cluster names accordingly.")

            # Get the mean values for each cluster (ignoring the noise cluster)
            a7_cluster_names = {}
            for cluster_label in unique_clusters_a7:
                cluster_mask = (df_a7['cluster_label'] == cluster_label)

                # Use the mask to select rows from X_a7_scaled
                cluster_points = X_a7_scaled[cluster_mask]  # This gives the scaled points for the current cluster

                # If you need to work with the temp_value specifically, you need to use df_a7
                temp_values = df_a7.loc[cluster_mask, 'temp_value']

                # Now you can calculate min and max values from the original temp_value column
                min_value = temp_values.min()
                max_value = temp_values.max()

                # Create the cluster name dynamically
                a7_cluster_names[cluster_label] = f"temp_{min_value:.2f}-{max_value:.2f}"
            # df_a7['cluster_name'] = df_a7['cluster_label'].map(a7_cluster_names)

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

        if clustering == "K means":
            kmeans_a1 = KMeans(n_clusters=clusters, random_state=42)
            df_a1['cluster_label'] = kmeans_a1.fit_predict(X_a1_scaled)
            #debug
            cluster_sizes = df_a1['cluster_label'].value_counts()
            print("Cluster sizes for a1:\n", cluster_sizes)

            centroids_a1 = kmeans_a1.cluster_centers_

            centroid_means_a1 = np.mean(centroids_a1, axis=1)
            sorted_cluster_indices_a1 = np.argsort(centroid_means_a1)

            a1_cluster_names = {}
            for cluster_label in sorted_cluster_indices_a1:
                cluster_mask = (df_a1['cluster_label'] == cluster_label)

                min_delay = df_a1.loc[cluster_mask, 'delay'].min()
                max_delay = df_a1.loc[cluster_mask, 'delay'].max()

                a1_cluster_names[cluster_label] = f'delay_{min_delay:.2f}_{max_delay:.2f}'
            print("Cluster names for a1:", a1_cluster_names)

        elif clustering == "Agglomerative":
                agglomerative_a1 = AgglomerativeClustering(n_clusters=3, linkage='average')
                df_a1['cluster_label'] = agglomerative_a1.fit_predict(X_a1_scaled)
                a1_cluster_names = {0: 'Cluster 1', 1: 'Cluster 2', 2: 'Cluster 3'}

        elif clustering == "DBSCAN":
            dbscan_a1 = DBSCAN(eps=0.1, min_samples=5)  # You can adjust eps and min_samples as needed

            df_a1['cluster_label'] = dbscan_a1.fit_predict(X_a1_scaled)
            # Get the unique cluster labels (ignoring noise points labeled as -1)
            unique_clusters_a1 = np.unique(df_a1['cluster_label'])
            unique_clusters_a1 = unique_clusters_a1[unique_clusters_a1 != -1]  # Exclude noise (-1)

            if len(unique_clusters_a1) < 3:
                print(
                    f"Warning: DBSCAN found only {len(unique_clusters_a1)} a1 clusters. Adjusting cluster names accordingly.")

            a1_cluster_names = {}
            for cluster_label in unique_clusters_a1:
                cluster_mask = (df_a1['cluster_label'] == cluster_label)

                cluster_points = X_a1_scaled[cluster_mask]  # This gives the scaled  points for the current cluster

                delay_values = df_a1.loc[cluster_mask, 'delay']

                min_value = delay_values.min()
                max_value = delay_values.max()

                a1_cluster_names[cluster_label] = f"delay_{min_value:.2f}-{max_value:.2f}"

            else:
                print(f"Unsupported clustering method: {clustering}")

            # Apply the mapping to the cluster labels
        df_a1['cluster_name'] = df_a1['cluster_label'].replace(a1_cluster_names)
    else:
        print("Skipping clustering for df_a1 due to empty dataset.")


    #-------- combine temp and delay rows ----------
    df_combined = pd.concat([df_a7, df_a1])
    # df_combined = df_combined.drop(columns=['original_index', 'cluster_label'])
    print(df_combined.head(10))
    df_combined = df_combined.sort_values(by='original_index')
    df_combined = df_combined.drop(columns=['original_index'])
    print(df_combined.head(10))
    df_combined = df_combined.rename(columns={
        'cluster_name': 'concept:name',
        'timestamp': 'time:timestamp'
    })
    output_file = "temp_delay.csv"
    df_combined.to_csv(output_file, index=False)

    print("Combined DataFrame:\n", df_combined)
    return output_file

if __name__ == "__main__":
    temp_delay('your_csv_file.csv', 'K means')  # Replace with your actual file and method


