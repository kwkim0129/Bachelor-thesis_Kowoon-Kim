import multiprocessing
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans, DBSCAN
from sklearn.cluster import AgglomerativeClustering
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt


def cluster_data(df, stop_attr, parameter, clustering_method):
    """Function to apply clustering to a specific stop attribute."""
    df_filtered = df[df['stop/attr'] == stop_attr].copy()
    df_filtered['stream_value'] = pd.to_numeric(df_filtered['stream_value'], errors='coerce')
    if df_filtered['stream_value'].isna().any():
        raise TypeError(
            "Selected ids contain non-numeric data. Cannot apply min/max operations on non-numeric values.")

    df_filtered['stream_value'] = df_filtered['stream_value'].fillna(df_filtered['stream_value'].mean())

    # Remove 0.0 and NaN values
    df_filtered = df_filtered[df_filtered['stream_value'] != 0.0].dropna(subset=['stream_value'])

    # Standardize the data
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df_filtered[['stream_value']])

    # Apply clustering based on the selected method
    if clustering_method == "K means":
        model = KMeans(n_clusters=parameter, random_state=42)
        df_filtered['cluster_label'] = model.fit_predict(X_scaled)
        centroids = model.cluster_centers_
        centroid_means = np.mean(centroids, axis=1)
        sorted_indices = np.argsort(centroid_means)
        cluster_names = {
            cluster_label: f"{stop_attr}_{df_filtered.loc[df_filtered['cluster_label'] == cluster_label, 'stream_value'].min():.2f}-{df_filtered.loc[df_filtered['cluster_label'] == cluster_label, 'stream_value'].max():.2f}"
            for cluster_label in sorted_indices}

    elif clustering_method == "Agglomerative":
        model = AgglomerativeClustering(n_clusters=parameter, linkage='average')
        df_filtered['cluster_label'] = model.fit_predict(X_scaled)
        cluster_names = {
            cluster_label: f"{stop_attr}_{df_filtered.loc[df_filtered['cluster_label'] == cluster_label, 'stream_value'].min():.2f}-{df_filtered.loc[df_filtered['cluster_label'] == cluster_label, 'stream_value'].max():.2f}"
            for cluster_label in range(parameter)}

    elif clustering_method == "DBSCAN":
        model = DBSCAN(eps=parameter, min_samples=3)
        df_filtered['cluster_label'] = model.fit_predict(X_scaled)
        unique_clusters = np.unique(df_filtered['cluster_label'])
        unique_clusters = unique_clusters[unique_clusters != -1]  # Exclude noise (-1)
        cluster_names = {
            cluster_label: f"{str(stop_attr)}_{df_filtered.loc[df_filtered['cluster_label'] == cluster_label, 'stream_value'].min():.2f}-{df_filtered.loc[df_filtered['cluster_label'] == cluster_label, 'stream_value'].max():.2f}"
            for cluster_label in unique_clusters}


    else:
        raise ValueError(f"Unsupported clustering method: {clustering_method}")

    df_filtered['cluster_name'] = df_filtered['cluster_label'].replace(cluster_names)
    return df_filtered

# clustering: k means, dbscan / clusters = parameter for clustering algorithms
def temp_delay(csvfile, clustering, clusters, selected_ids):
    df = pd.read_csv(csvfile)
    df['original_index'] = df.index  # Create index internally to keep original index

    df_list = []

    for selected_id in selected_ids:
        df_temp = cluster_data(df, selected_id, clusters, clustering)
        df_list.append(df_temp)

    # Combine the results
    df_combined = pd.concat(df_list, ignore_index=True)
    df_combined = df_combined.sort_values(by='original_index').drop(columns=['original_index'])

    # Rename columns
    df_combined = df_combined.rename(columns={'cluster_name': 'concept:name', 'timestamp': 'time:timestamp'})

    # Save the output to a CSV file
    output_file = "temp_delay.csv"
    df_combined.to_csv(output_file, index=False)

    return output_file

if __name__ == "__main__":
    temp_delay('input.csv', 'K means', 3, ['id1, id2'])  # Replace with your actual file and method


