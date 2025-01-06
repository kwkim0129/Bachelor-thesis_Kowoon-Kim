import os
import time

import pandas as pd
from scipy.stats import alpha
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.impute import SimpleImputer
from pm4py.objects.conversion.log import converter as log_converter
from pm4py.algo.discovery.heuristics import algorithm as heuristics_miner
from pm4py.visualization.petri_net import visualizer as pn_visualizer
from pm4py.algo.discovery.alpha import algorithm as alpha_miner
from sklearn.cluster import AgglomerativeClustering
from pm4py.algo.discovery.heuristics import algorithm as heu


def alpha(FILENAME, parameter, submit):
    df = pd.read_csv(FILENAME)
    df = df.rename(columns={'label': 'concept:name', "time:timestamp": "timestamp"})
    df['timestamp'] = pd.to_datetime(df['timestamp'], format='mixed')

    parameters = {log_converter.Variants.TO_EVENT_LOG.value.Parameters.CASE_ID_KEY: 'timestamp'}
    event_log = log_converter.apply(df, parameters=parameters)

    try:
        net, initial_marking, final_marking = alpha_miner.apply(event_log)
    except Exception as e:
        raise ValueError(f"Alpha Miner failed: {e}")

    try:
        gviz = pn_visualizer.apply(net, initial_marking, final_marking)
        if gviz is None:
            raise ValueError("Visualization (gviz) is None.")
    except Exception as e:
        raise ValueError(f"Visualization failed: {e}")

    # Save the visualization
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    image_filename = f'alpha_{timestamp}.png'
    image_path = os.path.join('./static', image_filename)
    os.makedirs('./static', exist_ok=True)  # Ensure static directory exists

    try:
        pn_visualizer.save(gviz, image_path)
        # pn_visualizer.view(gviz, image_path)
    except Exception as e:
        raise ValueError(f"Saving the visualization failed: {e}")

    return image_path

if __name__ == '__main__':
    FILENAME = alpha("input.csv", "submit", 1)

    param = "K means"
    submit = "Submit Selected"
    image_path = alpha(FILENAME, param, submit)
    print(f"Alpha created at: {image_path}")