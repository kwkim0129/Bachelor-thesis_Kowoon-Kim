import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans, DBSCAN
from sklearn.cluster import AgglomerativeClustering
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

# when one puts csv file as a parameter then the temp_delay csv will be created
def traf_delay(csvfile, clustering, clusters):
    df = pd.read_csv(csvfile)
    df['original_index'] = df.index

    df_a8 = df[df['label'] == 'a8'].copy()
    df_a1 = df[df['label'] == 'a1'].copy()

    print("Rows in df_a8:", len(df_a8))
    print("Rows in df_a1:", len(df_a1))

    df_a8['traffic'] = pd.to_numeric(df_a8['traffic'], errors='coerce')
    df_a1['delay'] = pd.to_numeric(df_a1['delay'], errors='coerce')
    df_a8['traffic'].fillna(df_a8['traffic'].mean(), inplace=True)
    df_a1 = df_a1[df_a1['delay'] != 0.0]
    df_a1 = df_a1.dropna(subset=['delay'])

    print("NaN values in df_a8 traffic:", df_a8['traffic'].isna().sum())
    print("NaN values in df_a1 delay:", df_a1['delay'].isna().sum())


    if not df_a8.empty:
        # Standardize the data
        scaler_a8 = StandardScaler()
        X_a8_scaled = scaler_a8.fit_transform(df_a8[['traffic']])

        # Choose clustering method based on the 'clustering' variable
        if clustering == "K means":
            kmeans_a8 = KMeans(n_clusters=clusters, random_state=42)
            df_a8['cluster_label'] = kmeans_a8.fit_predict(X_a8_scaled)
            # debug
            cluster_sizes = df_a8['cluster_label'].value_counts()
            print("Cluster sizes for a1:\n", cluster_sizes)

            centroids_a8 = kmeans_a8.cluster_centers_
            centroid_means_a8 = np.mean(centroids_a8, axis=1)

            sorted_cluster_indices_a8 = np.argsort(centroid_means_a8)

            a8_cluster_names = {}
            for cluster_label in sorted_cluster_indices_a8:
                cluster_mask = (df_a8['cluster_label'] == cluster_label)

                min_value = df_a8.loc[cluster_mask, 'traffic'].min()
                max_value = df_a8.loc[cluster_mask, 'traffic'].max()

                #debug
                a8_cluster_names[cluster_label] = f'traf_{min_value:.2f}_{max_value:.2f}'
                print("Cluster names for a8:", a8_cluster_names)

        elif clustering == "Agglomerative":
            agglomerative_a8 = AgglomerativeClustering(n_clusters=clusters, linkage='average')
            df_a8['cluster_label'] = agglomerative_a8.fit_predict(X_a8_scaled)
            a8_cluster_names = {}
            for cluster_label in range(clusters):
                cluster_mask = (df_a8['cluster_label'] == cluster_label)

                min_traf= df_a8.loc[cluster_mask, 'traffic'].min()
                max_traf = df_a8.loc[cluster_mask, 'traffic'].max()

                a8_cluster_names[cluster_label] = f'traf_{min_traf:.2f}_{max_traf:.2f}'

        elif clustering == "DBSCAN":
            dbscan_a8 = DBSCAN(eps=0.15, min_samples=3)

            df_a8['cluster_label'] = dbscan_a8.fit_predict(X_a8_scaled)
            unique_clusters_a8 = np.unique(df_a8['cluster_label'])
            unique_clusters_a8 = unique_clusters_a8[unique_clusters_a8 != -1]  # Exclude noise (-1)

            if len(unique_clusters_a8) < 3:
                print(
                    f"Warning: DBSCAN found only {len(unique_clusters_a8)} a8 clusters. Adjusting cluster names accordingly.")

            # Get the mean values for each cluster (ignoring the noise cluster)
            a8_cluster_names = {}
            for cluster_label in unique_clusters_a8:
                cluster_mask = (df_a8['cluster_label'] == cluster_label)

                cluster_points = X_a8_scaled[cluster_mask]  # This gives the scaled points for the current cluster

                traf_values = df_a8.loc[cluster_mask, 'traffic']

                min_value = traf_values.min()
                max_value = traf_values.max()

                a8_cluster_names[cluster_label] = f"traf_{min_value:.2f}-{max_value:.2f}"

        else:
            print(f"Unsupported clustering method: {clustering}")

        df_a8['cluster_name'] = df_a8['cluster_label'].replace(a8_cluster_names)

    else:
        print("Skipping clustering for df_a8 due to empty dataset.")

    # Cluster according to the input parameter
    if not df_a1.empty:
        scaler_a1 = StandardScaler()
        X_a1_scaled = scaler_a1.fit_transform(df_a1[['delay']])

        if clustering == "K means":
            kmeans_a1 = KMeans(n_clusters=clusters, random_state=42)
            df_a1['cluster_label'] = kmeans_a1.fit_predict(X_a1_scaled)
            # debug
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
            agglomerative_a1 = AgglomerativeClustering(n_clusters=clusters, linkage='average')
            df_a1['cluster_label'] = agglomerative_a1.fit_predict(X_a1_scaled)
            a1_cluster_names = {}
            for cluster_label in range(clusters):
                cluster_mask = (df_a1['cluster_label'] == cluster_label)

                min_delay = df_a1.loc[cluster_mask, 'delay'].min()
                max_delay = df_a1.loc[cluster_mask, 'delay'].max()

                a1_cluster_names[cluster_label] = f'delay_{min_delay:.2f}_{max_delay:.2f}'

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

    df_combined = pd.concat([df_a8, df_a1])
    df_combined = df_combined.sort_values(by='original_index')
    df_combined = df_combined.drop(columns=['original_index'])
    df_combined = df_combined.rename(columns={
        'cluster_name': 'concept:name',
        'timestamp': 'time:timestamp'
    })
    output_file = "traf_delay.csv"
    df_combined.to_csv(output_file, index=False)
    return output_file

if __name__ == "__main__":
    traf_delay('input.csv', 'K means')


