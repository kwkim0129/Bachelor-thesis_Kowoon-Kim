import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans, DBSCAN
from sklearn.cluster import AgglomerativeClustering
import numpy as np
from sklearn.decomposition import PCA


def mult_delay(csvfile, clustering, clusters):
    df = pd.read_csv(csvfile)
    df['original_index'] = df.index

    df_a7 = df[df['label'] == 'a7'].copy()
    df_a1 = df[df['label'] == 'a1'].copy()

    df_a7['temp_value'] = pd.to_numeric(df_a7['temp_value'], errors='coerce')
    df_a7['pressure_value'] = pd.to_numeric(df_a7['pressure_value'], errors='coerce')
    df_a7['humidity_value'] = pd.to_numeric(df_a7['humidity_value'], errors='coerce')
    df_a1['delay'] = pd.to_numeric(df_a1['delay'], errors='coerce')

    # Remove rows with NaN values after conversion (those that couldn't be converted to numeric)
    df_a7 = df_a7.dropna(subset=['temp_value', 'pressure_value', 'humidity_value'])

    # Handle missing values (fill NaN with the mean of the respective column)
    df_a7['temp_value'].fillna(df_a7['temp_value'].mean(), inplace=True)
    df_a7['pressure_value'].fillna(df_a7['pressure_value'].mean(), inplace=True)
    df_a7['humidity_value'].fillna(df_a7['humidity_value'].mean(), inplace=True)
    df_a1 = df_a1[df_a1['delay'] != 0.0]
    df_a1 = df_a1.dropna(subset=['delay'])

    # Clustering for 'a7'
    if not df_a7.empty:
        # Standardize the data for temp_value, pressure_value, and humidity_value
        scaler_a7 = StandardScaler()
        X_a7_scaled = scaler_a7.fit_transform(df_a7[['temp_value', 'pressure_value', 'humidity_value']])

        # Perform K-Means clustering
        if clustering == "K means":
            kmeans_a7 = KMeans(n_clusters=clusters, random_state=42)
            df_a7['cluster_label'] = kmeans_a7.fit_predict(X_a7_scaled)

            a7_cluster_names = {}

            # Apply PCA for cluster naming
            pca = PCA(n_components=1)
            X_a7_pca = pca.fit_transform(X_a7_scaled)
            df_a7['pca_component'] = X_a7_pca

            # Generate names based on PCA values
            for cluster_label in df_a7['cluster_label'].unique():
                cluster_mask = (df_a7['cluster_label'] == cluster_label)
                min_pca = df_a7.loc[cluster_mask, 'pca_component'].min()
                max_pca = df_a7.loc[cluster_mask, 'pca_component'].max()
                a7_cluster_names[cluster_label] = f'combined_{min_pca:.2f}_{max_pca:.2f}'

        # df_a7['cluster_name'] = df_a7['cluster_label'].replace(a7_cluster_names)
        elif clustering == "Agglomerative":
            agglomerative_a7 = AgglomerativeClustering(n_clusters=clusters, linkage='average', compute_full_tree=True)
            df_a7['cluster_label'] = agglomerative_a7.fit_predict(X_a7_scaled)
            a7_cluster_names = {}

            pca = PCA(n_components=1)
            X_a7_pca = pca.fit_transform(X_a7_scaled)
            df_a7['pca_component'] = X_a7_pca

            unique_clusters = np.unique(df_a7['cluster_label'])

            for cluster_label in unique_clusters:
                cluster_mask = (df_a7['cluster_label'] == cluster_label)
                min_pca = df_a7.loc[cluster_mask, 'pca_component'].min()
                max_pca = df_a7.loc[cluster_mask, 'pca_component'].max()
                a7_cluster_names[cluster_label] = f'combined_{min_pca:.2f}_{max_pca:.2f}'

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
                cluster_mask =      (df_a7['cluster_label'] == cluster_label)

                # Use the mask to select rows from X_a7_scaled
                cluster_points = X_a7_scaled[cluster_mask]  # This gives the scaled points for the current cluster

                # If you need to work with the temp_value specifically, you need to use df_a7
                temp_values = df_a7.loc[cluster_mask, 'temp_value']

                # Now you can calculate min and max values from the original temp_value column
                min_value = temp_values.min()
                max_value = temp_values.max()

                # Create the cluster name dynamically
                a7_cluster_names[cluster_label] = f"weather_{min_value:.2f}-{max_value:.2f}"

        else:
            print(f"Unsupported clustering method: {clustering}")
        df_a7['cluster_name'] = df_a7['cluster_label'].replace(a7_cluster_names)
    else:
        print("Skipping clustering for df_a7 due to empty dataset.")

    if not df_a1.empty:
        # Standardize the data
        scaler_a1 = StandardScaler()
        X_a1_scaled = scaler_a1.fit_transform(df_a1[['delay']])

        # Choose clustering method based on the 'clustering' variable
        if clustering == "K means":
            kmeans_a1 = KMeans(n_clusters=clusters, random_state=42)
            df_a1['cluster_label'] = kmeans_a1.fit_predict(X_a1_scaled)

            # Get the centroids for the delay clusters
            centroids_a1 = kmeans_a1.cluster_centers_
            centroid_means_a1 = np.mean(centroids_a1, axis=1)
            sorted_cluster_indices_a1 = np.argsort(centroids_a1.flatten())

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
