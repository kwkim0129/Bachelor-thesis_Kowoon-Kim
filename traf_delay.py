import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.cluster import AgglomerativeClustering
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

# when one puts csv file as a parameter then the temp_delay csv will be created
def traf_delay(csvfile, clustering):
    # Load the original CSV file
    df = pd.read_csv(csvfile)

    # Add a column to retain the original order
    df['original_index'] = df.index

    # Filter rows where label is 'a7' or 'a1'
    df_a8 = df[df['label'] == 'a8'].copy()
    df_a1 = df[df['label'] == 'a1'].copy()

    # Debugging: Check how many rows are being filtered
    print("Rows in df_a8:", len(df_a8))
    print("Rows in df_a1:", len(df_a1))

    # Ensure numeric columns for clustering (convert temp_value and delay to numeric)
    df_a8['temp_value'] = pd.to_numeric(df_a8['traffic'], errors='coerce')
    df_a1['delay'] = pd.to_numeric(df_a1['delay'], errors='coerce')

    # Handle missing values (fill NaN with the mean of the respective column)
    df_a8['traffic'].fillna(df_a8['traffic'].mean(), inplace=True)
    df_a1['delay'].fillna(df_a1['delay'].mean(), inplace=True)

    # Debugging: Check for NaN values after filling
    print("NaN values in df_a8 traffic:", df_a8['traffic'].isna().sum())
    print("NaN values in df_a1 delay:", df_a1['delay'].isna().sum())

    # Check if there are rows left after filtering NaNs
    if df_a8.empty:
        print("Error: No rows in df_a8 after filtering.")
    if df_a1.empty:
        print("Error: No rows in df_a1 after filtering.")

    # Proceed only if there are rows to cluster
    # Clustering for 'a7'
    if not df_a8.empty:
        # Standardize the data
        scaler_a7 = StandardScaler()
        X_a7_scaled = scaler_a7.fit_transform(df_a8[['traffic']])

        # Choose clustering method based on the 'clustering' variable
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

        # Apply the mapping to the cluster labels
        df_a8['cluster_name'] = df_a8['cluster_label'].replace(a8_cluster_names)
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
            a1_cluster_names = {0: 'Low delay', 1: 'Moderate delay', 2: 'High delay'}

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
    df_combined = pd.concat([df_a8, df_a1])
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
    output_file = "traf_delay.csv"
    df_combined.to_csv(output_file, index=False)
    return output_file