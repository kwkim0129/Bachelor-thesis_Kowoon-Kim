import pandas as pd
from pm4py.objects.log.util import dataframe_utils
from pm4py.objects.conversion.log import converter as log_converter
from pm4py.algo.discovery.dfg import algorithm as dfg_discovery
from pm4py.visualization.dfg import visualizer as dfg_visualization
from pm4py.algo.discovery.heuristics import algorithm as heuristics_miner
from pm4py.visualization.petri_net import visualizer as pn_visualizer
from pm4py.algo.discovery.alpha import algorithm as alpha_miner
import os

# def dfg(FILENAME):
df = pd.read_csv("clustered_weather_delay_original_order.csv")
df = df.rename(columns={'label': 'concept:name',"time:timestamp": "timestamp"})
df['timestamp'] = pd.to_datetime(df['timestamp'], format='mixed')

parameters = {log_converter.Variants.TO_EVENT_LOG.value.Parameters.CASE_ID_KEY: 'case_id'}
event_log = log_converter.apply(df, parameters=parameters)

# net, initial_marking, final_marking = heuristics_miner.apply(event_log)
# gviz = pn_visualizer.apply(net, initial_marking, final_marking)
# pn_visualizer.view(gviz)
dfg = dfg_discovery.apply(event_log)
gviz = dfg_visualization.apply(dfg, variant=dfg_visualization.Variants.FREQUENCY)
# dfg_visualization.view(gviz)
