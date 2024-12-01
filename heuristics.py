import os
import time

import pandas as pd
# from pm4py.objects.log.importer.csv import factory as csv_importer
from pm4py.objects.conversion.log import converter as log_converter
from pm4py.algo.discovery.heuristics import algorithm as heuristics_miner
from pm4py.visualization.heuristics_net import visualizer as vis

def heuristics(FILENAME):
    df = pd.read_csv(FILENAME)

    df = df.rename(columns={'label': 'concept:name', 'timestamp': 'time:timestamp'})

    df['time:timestamp'] = pd.to_datetime(df['time:timestamp'])

    parameters = {log_converter.Variants.TO_EVENT_LOG.value.Parameters.CASE_ID_KEY: 'cluster_label'}
    event_log = log_converter.apply(df, parameters=parameters)

    start_activities = {}
    end_activities = {}

    for trace in event_log:
        if len(trace) > 0:
            start_activity = trace[0]['concept:name']  # First event in the trace
            end_activity = trace[-1]['concept:name']  # Last event in the trace

            # Update the start activities dictionary
            if start_activity in start_activities:
                start_activities[start_activity] += 1
            else:
                start_activities[start_activity] = 1

            # Update the end activities dictionary
            if end_activity in end_activities:
                end_activities[end_activity] += 1
            else:
                end_activities[end_activity] = 1

    # debugging
        print("Start Activities:")
        print(start_activities)
        print("End Activities:")
        print(end_activities)

        heu_net = heuristics_miner.apply_heu(event_log)

        gviz = None

        gviz = vis.apply(heu_net)

        if gviz is None:
            raise ValueError(f"Invalid heuristics graph")

        timestamp = time.strftime("%Y%m%d-%H%M%S")
        image_filename = f'heu_{timestamp}.png'
        image_path = os.path.join('./static', image_filename)

        vis.save(gviz, image_path)

        return image_path

if __name__ == "__main__":
    df = pd.read_csv("temp_delay.csv")
    df = df.rename(columns={'label': 'concept:name', 'timestamp': 'time:timestamp'})
    df['time:timestamp'] = pd.to_datetime(df['time:timestamp'])
    parameters = {log_converter.Variants.TO_EVENT_LOG.value.Parameters.CASE_ID_KEY: 'cluster_label'}
    event_log = log_converter.apply(df, parameters=parameters)
    image_path = heuristics(event_log)
    print(f"Heuristics graph image saved at: {image_path}")

