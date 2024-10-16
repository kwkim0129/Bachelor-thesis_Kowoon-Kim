import pandas as pd
import os
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.impute import SimpleImputer
from pm4py.objects.conversion.log import converter as log_converter
from pm4py.algo.discovery.alpha import algorithm as alpha_miner
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.visualization.petri_net import visualizer as pn_visualizer
from pm4py.objects.conversion.process_tree import converter as pt_converter
from pm4py.algo.discovery.dfg import algorithm as dfg_discovery
from pm4py.visualization.dfg import visualizer as dfg_visualization
from temp_delay import temp_delay
import time


def dfg(FILENAME, submit):
    df = pd.read_csv(FILENAME) # the file should be newly created csv by clustering above
    df = df.rename(columns={'label': 'concept:name', "time:timestamp": "timestamp"})
    df['timestamp'] = pd.to_datetime(df['timestamp'], format='mixed')

    parameters = {log_converter.Variants.TO_EVENT_LOG.value.Parameters.CASE_ID_KEY: 'case_id'}
    event_log = log_converter.apply(df, parameters=parameters)
    dfg = dfg_discovery.apply(event_log)
    gviz = dfg_visualization.apply(dfg, variant=dfg_visualization.Variants.FREQUENCY)
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    image_filename = f'dfg_{timestamp}.png'
    image_path = os.path.join('./static', image_filename)
    # image_path = './static/dfg_test.png'
    dfg_visualization.save(gviz, image_path)
    return image_path

if __name__ == '__main__':
    FILENAME = temp_delay("input_file.csv", "K means")
    # clustering = "K means"  # Example clustering algorithm
    submit = "Submit Selected"  # Example selected value
    image_path = dfg(FILENAME, submit)
    # dfg(FILENAME, submit)
    print(f"DFG image created at: {image_path}")

