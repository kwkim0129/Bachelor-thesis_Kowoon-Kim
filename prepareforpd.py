import pandas as pd

# Step 1: Load the original CSV file
df = pd.read_csv("clustered_weather_delay_original_order.csv")

# Step 2: Select and rename the required columns
df = df.rename(columns={
    'case_id': 'case_id',
    'label': 'label',
    'temp_value': 'temp',
    'delay': 'delay',
    'timestamp': 'time:timestamp',
    'cluster_label': 'concept:name'
})

# Step 3: Map cluster_label to cluster names
cluster_mapping = {
    0: 'low delay',
    1: 'medium delay',
    2: 'high delay',
    # Add more mappings if needed
}

# Apply the mapping to the 'concept:name' column
df['concept:name'] = df['concept:name'].map(cluster_mapping)

# Step 4: Select the final columns in the desired order
df = df[['case_id', 'label', 'temp', 'delay', 'time:timestamp', 'traffic', 'concept:name']]

# Step 5: Save the transformed data to a new CSV file
df.to_csv("weather_delay.csv", index=False)

print("Transformation completed! New CSV saved as 'transformed_file.csv'.")
