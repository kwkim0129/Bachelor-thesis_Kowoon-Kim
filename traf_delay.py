import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.cluster import AgglomerativeClustering
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

def traf_delay(csvfile, clustering):
    df = pd.read_csv(csvfile)

    df['original_index'] = df.index

    df_a8 = df[df['label'] == 'a8'].copy()
    df_a1 = df[df['label'] == 'a1'].copy()

    print("Rows in df_a8:", len(df_a8))
    print("Rows in df_a1:", len(df_a1))

    df_a8['temp_value'] = pd.to_numeric(df_a8['traffic'], errors='coerce')
    df_a1['delay'] = pd.to_numeric(df_a1['delay'], errors='coerce')

    df_a8['traffic'].fillna(df_a8['traffic'].mean(), inplace=True)
    df_a1['delay'].fillna(df_a1['delay'].mean(), inplace=True)

    # Debugging
    print("NaN values in df_a8 traffic:", df_a8['traffic'].isna().sum())
    print("NaN values in df_a1 delay:", df_a1['delay'].isna().sum())

    if df_a8.empty:
        print("Error: No rows in df_a8 after filtering.")
    if df_a1.empty:
        print("Error: No rows in df_a1 after filtering.")

    # Clustering for 'a7'
    if not df_a8.empty:
        scaler_a7 = StandardScaler()
        X_a7_scaled = scaler_a7.fit_transform(df_a8[['traffic']])

        if clustering == "K means":
            kmeans_a8 = KMeans(n_clusters=3, random_state=42)
            df_a8['cluster_label'] = kmeans_a8.fit_predict(X_a7_scaled)
            a8_cluster_names = {0: 'low temp', 1: 'moderate temp', 2: 'high temp'}

        elif clustering == "Agglomerative":
            agglomerative_a8 = AgglomerativeClustering(n_clusters=3, linkage='average')
            df_a8['cluster_label'] = agglomerative_a8.fit_predict(X_a7_scaled)
            a8_cluster_names = {0: 'Cluster 1', 1: 'Cluster 2', 2: 'Cluster 3'}

        else:
            print(f"Unsupported clustering method: {clustering}")

        df_a8['cluster_name'] = df_a8['cluster_label'].replace(a8_cluster_names)
    else:
        print("Skipping clustering for df_a7 due to empty dataset.")

    if not df_a1.empty:
        scaler_a1 = StandardScaler()
        X_a1_scaled = scaler_a1.fit_transform(df_a1[['delay']])

        if clustering == "K means":
            kmeans_a1 = KMeans(n_clusters=3, random_state=42)
            df_a1['cluster_label'] = kmeans_a1.fit_predict(X_a1_scaled)
            a1_cluster_names = {0: 'Low delay', 1: 'Moderate delay', 2: 'High delay'}

        elif clustering == "Agglomerative":
            agglomerative_a1 = AgglomerativeClustering(n_clusters=3, linkage='average')
            df_a1['cluster_label'] = agglomerative_a1.fit_predict(X_a1_scaled)
            a1_cluster_names = {0: 'Cluster 1', 1: 'Cluster 2', 2: 'Cluster 3'}

        else:
            print(f"Unsupported clustering method: {clustering}")

        df_a1['cluster_name'] = df_a1['cluster_label'].replace(a1_cluster_names)
    else:
        print("Skipping clustering for df_a1 due to empty dataset.")

    df_combined = pd.concat([df_a8, df_a1])

    # Sort by the original order (based on 'original_index')
    df_combined = df_combined.sort_values(by='original_index')

    # Drop the 'original_index' column (optional, if you don't want it in the final CSV)
    df_combined = df_combined.drop(columns=['original_index'])
    df_combined = df_combined.rename(columns={
        'cluster_name': 'concept:name',
        'timestamp': 'time:timestamp'
    })
    output_file = "traf_delay.csv"
    df_combined.to_csv(output_file, index=False)
    return output_file
