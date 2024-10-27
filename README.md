Description of the files

[Website]
- static => where image files go after process model has been created
- uploads => csv created with clusters
- templates => main.html and direct_graph.html which control style of my website
- app => backend of flask

[yaml to csv]
- csvcon.py: yaml to csv => yaml to csv only that extract values for each activity

[clustering]
- temp_delay.py => temp and delay CSV with kmeans / agglomerative 
- traf_delay => traffic and delay CSV with kmenas / agglomerative 
- mult_delay => traffic and delay CSV with kmenas / agglomeration
- prepareforpd => example for creating csv with clusters that have columns required for process discovery algorithm

[discovery]
- alpha_temp => extracts dfg 
- inductive => extracts petri net with inductive miner
- alpha => extracts petri net with alpha miner 

