import csv
import yaml

input_file = "test.xes.yaml"
output_file = "output2.csv"

def process_stream_data(stream_data, rows, event_id, stop_id="N/A"):
    """
    Recursively process stream:datastream and append relevant rows.

    Args:
    - stream_data: The current stream data (dict or list).
    - rows: The list to append the extracted rows.
    - event_id: The event ID to include in the rows.
    - stop_id: The current stop_id, inherited from parent levels.
    """
    if isinstance(stream_data, list):  # Handle list of stream data
        for item in stream_data:
            process_stream_data(item, rows, event_id, stop_id)

    elif isinstance(stream_data, dict):
        # Update the stop_id only if stream:id is present in the current dictionary
        current_stop_id = stop_id  # Inherit from parent by default
        if "stream:point" in stream_data:
            point = stream_data["stream:point"]
            if isinstance(point, list):  #  list of points
                for p in point:
                    if isinstance(p, dict):
                        current_stop_id = p.get("stream:id", current_stop_id)
                        stream_value = p.get("stream:value", "N/A")
                        timestamp = p.get("stream:timestamp", "N/A")
                        rows.append([0, current_stop_id, event_id, stream_value, timestamp])
            elif isinstance(point, dict):  # Single point
                current_stop_id = point.get("stream:id", current_stop_id)
                stream_value = point.get("stream:value", "N/A")
                timestamp = point.get("stream:timestamp", "N/A")
                rows.append([0, current_stop_id, event_id, stream_value, timestamp])

        # If no stream:point, inherit the stop_id
        elif "stream:datastream" in stream_data:
            nested_datastream = stream_data["stream:datastream"]
            process_stream_data(nested_datastream, rows, event_id, current_stop_id)



# Function to process a single event
def process_event(event):
    rows = []
    event_id = event.get("id:id", "N/A")

    # Debugg
    print(f"Processing event with ID: {event_id}")

    # Iterate over stream:datastream entries in the event
    for stream_data in event.get("stream:datastream", []):
        process_stream_data(stream_data, rows, event_id)

    return rows

def extract_to_csv(input_file, output_file):
    with open(input_file, "r") as file:
        data = yaml.load_all(file, yaml.SafeLoader)

        csv_data = [["case_id", "stop/attr", "id_id", "stream_value", "timestamp"]]

        for document in data:
            event = document.get("event", [])
            if event:
                csv_data.extend(process_event(event))

    with open(output_file, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(csv_data)


# Call the main function
# extract_to_csv(input_file, output_file)
# print(f"Data extracted to {output_file}")

