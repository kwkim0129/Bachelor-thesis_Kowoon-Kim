import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans, DBSCAN
from sklearn.cluster import AgglomerativeClustering
import numpy as np

def mult_delay(csvfile, clustering, clusters):
    df = pd.read_csv(csvfile)
    df['original_index'] = df.index

    df_a7 = df[df['label'] == 'a7'].copy()
    df_a1 = df[df['label'] == 'a1'].copy()

    df_a7['temp_value'] = pd.to_numeric(df_a7['temp_value'], errors='coerce')
    df_a7['pressure_value'] = pd.to_numeric(df_a7['pressure_value'], errors='coerce')
    df_a7['humidity_value'] = pd.to_numeric(df_a7['humidity_value'], errors='coerce')
    df_a1['delay'] = pd.to_numeric(df_a1['delay'], errors='coerce')

    df_a7 = df_a7.dropna(subset=['temp_value', 'pressure_value', 'humidity_value'])

    df_a7['temp_value'].fillna(df_a7['temp_value'].mean(), inplace=True)
    df_a7['pressure_value'].fillna(df_a7['pressure_value'].mean(), inplace=True)
    df_a7['humidity_value'].fillna(df_a7['humidity_value'].mean(), inplace=True)
    df_a1 = df_a1[df_a1['delay'] != 0.0]
    df_a1 = df_a1.dropna(subset=['delay'])

    if not df_a7.empty:
        scaler_a7 = StandardScaler()
        X_a7_scaled = scaler_a7.fit_transform(df_a7[['temp_value', 'pressure_value', 'humidity_value']])

        if clustering == "K means":
            kmeans_a7 = KMeans(n_clusters=clusters, random_state=42)
            df_a7['cluster_label'] = kmeans_a7.fit_predict(X_a7_scaled)

            centroids_a7 = kmeans_a7.cluster_centers_
            centroid_means_a7 = np.mean(centroids_a7, axis=1)

            sorted_cluster_indices_a7 = np.argsort(centroid_means_a7)

            a7_cluster_names = {}
            for cluster_label in sorted_cluster_indices_a7:
                cluster_mask = (df_a7['cluster_label'] == cluster_label)
                min_value = df_a7.loc[cluster_mask, 'temp_value'].min()
                max_value = df_a7.loc[cluster_mask, 'temp_value'].max()
                a7_cluster_names[cluster_label] = f'weather_{min_value:.2f}_{max_value:.2f}'

        elif clustering == "Agglomerative":
            agglomerative_a7 = AgglomerativeClustering(n_clusters=3, linkage='average', compute_full_tree=True)
            df_a7['cluster_label'] = agglomerative_a7.fit_predict(X_a7_scaled)
            a7_cluster_names = {0: 'Cluster 1', 1: 'Cluster 2', 2: 'Cluster 3'}

        elif clustering == "DBSCAN":
            dbscan_a7 = DBSCAN(eps=clusters, min_samples=5)  

            df_a7['cluster_label'] = dbscan_a7.fit_predict(X_a7_scaled)
            unique_clusters_a7 = np.unique(df_a7['cluster_label'])
            unique_clusters_a7 = unique_clusters_a7[unique_clusters_a7 != -1]  

            if len(unique_clusters_a7) < 3:
                print(
                    f"Warning: DBSCAN found only {len(unique_clusters_a7)} a7 clusters. Adjusting cluster names accordingly.")

            a7_cluster_names = {}
            for cluster_label in unique_clusters_a7:
                cluster_mask = (df_a7['cluster_label'] == cluster_label)

                cluster_points = X_a7_scaled[cluster_mask]  

                temp_values = df_a7.loc[cluster_mask, 'temp_value']

                min_value = temp_values.min()
                max_value = temp_values.max()

                a7_cluster_names[cluster_label] = f"weather_{min_value:.2f}-{max_value:.2f}"

        else:
            print(f"Unsupported clustering method: {clustering}")
        df_a7['cluster_name'] = df_a7['cluster_label'].replace(a7_cluster_names)
    else:
        print("Skipping clustering for df_a7 due to empty dataset.")

    if not df_a1.empty:
        scaler_a1 = StandardScaler()
        X_a1_scaled = scaler_a1.fit_transform(df_a1[['delay']])

        if clustering == "K means":
            kmeans_a1 = KMeans(n_clusters=clusters, random_state=42)
            df_a1['cluster_label'] = kmeans_a1.fit_predict(X_a1_scaled)

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
            dbscan_a1 = DBSCAN(eps=0.1, min_samples=5) 

            df_a1['cluster_label'] = dbscan_a1.fit_predict(X_a1_scaled)
           
            unique_clusters_a1 = np.unique(df_a1['cluster_label'])
            unique_clusters_a1 = unique_clusters_a1[unique_clusters_a1 != -1]  

            if len(unique_clusters_a1) < 3:
                print(
                    f"Warning: DBSCAN found only {len(unique_clusters_a1)} a1 clusters. Adjusting cluster names accordingly.")

            a1_cluster_names = {}
            for cluster_label in unique_clusters_a1:
                cluster_mask = (df_a1['cluster_label'] == cluster_label)

                cluster_points = X_a1_scaled[cluster_mask] 

                delay_values = df_a1.loc[cluster_mask, 'delay']

                min_value = delay_values.min()
                max_value = delay_values.max()

                a1_cluster_names[cluster_label] = f"delay_{min_value:.2f}-{max_value:.2f}"

        else:
            print(f"Unsupported clustering method: {clustering}")

        df_a1['cluster_name'] = df_a1['cluster_label'].replace(a1_cluster_names)
    else:
        print("Skipping clustering for df_a1 due to empty dataset.")

    df_combined = pd.concat([df_a7, df_a1])

    df_combined = df_combined.sort_values(by='original_index')

    df_combined = df_combined.drop(columns=['original_index'])
    df_combined = df_combined.rename(columns={
        'cluster_name': 'concept:name',
        'timestamp': 'time:timestamp'
    })

    # Save the clustered data to a new CSV file
    output_file = "mult_delay.csv"
    df_combined.to_csv(output_file, index=False)
    return output_file
