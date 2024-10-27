from pm4py.algo.discovery.inductive import algorithm as inductive_miner
# from pm4py.visualization.petrinet import visualizer as pn_visualizer
import pandas as pd
import statistics
import pm4py
import matplotlib.pyplot as plt
from pm4py.objects.log.importer.xes import importer
from pm4py.objects.conversion.log.converter import to_data_frame
from pm4py.algo.filtering.pandas.attributes import attributes_filter
# from pm4py.statistics.traces.log import case_statistics
from pm4py.objects.log.util import interval_lifecycle
# from pm4py.statistics.traces.log import case_arrival
# from pm4py.statistics.sojourn_time.log import get as soj_time_get
from pm4py.visualization.graphs import visualizer as graphs_visualizer
from pm4py.util import constants
from pm4py.algo.filtering.log.timestamp import timestamp_filter
from pm4py.algo.filtering.log.end_activities import end_activities_filter
from pm4py.algo.filtering.log.start_activities import start_activities_filter
from pm4py.algo.discovery.alpha import algorithm as alpha_miner
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.algo.discovery.dfg import algorithm as dfg_discovery
from pm4py.visualization.dfg import visualizer as dfg_visualization
from pm4py.visualization.petri_net import visualizer as pn_visualizer
from pm4py.objects.conversion.log import converter as log_converter
from pm4py.objects.conversion.process_tree import converter as pt_converter
from pm4py.visualization.process_tree import visualizer as pt_visualization
import os
import time
from temp_delay import temp_delay


def inductive(FILENAME, parameter, submit):
    df = pd.read_csv(FILENAME)
    df = df.rename(columns={'label': 'concept:name', "time:timestamp": "timestamp"})
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.drop_duplicates()

    parameters = {log_converter.Variants.TO_EVENT_LOG.value.Parameters.CASE_ID_KEY: 'case_id',  "noise_threshold": parameter}
    event_log = log_converter.apply(df, parameters=parameters)
    process_tree = inductive_miner.apply(event_log, parameters=parameters)

    gviz = None

    # Discover Petri net using Inductive Miner
    net, initial_marking, final_marking = pt_converter.apply(process_tree)
    gviz = pn_visualizer.apply(net, initial_marking, final_marking)
    # pn_visualizer.view(gviz)

    # Visualize the process tree
    # gviz = pt_visualization.apply(process_tree)
    # pt_visualization.view(gviz)
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    image_filename = f'inductive_{timestamp}.png'
    image_path = os.path.join('./static', image_filename)
    # image_path = './static/inductive.png'
    pn_visualizer.save(gviz, image_path)
    return image_path

if __name__ == '__main__':
    FILENAME = temp_delay("input_file.csv", "K means", 1)
    parameter = 0.2  # Example noise threshold parameter
    image_path = inductive(FILENAME, parameter, submit="Submit Selected")

    print(f"Inductive miner image created at : {image_path}")

