import yaml
import os
import csv
import re
import sys


def yaml_to_csv(yaml_file, csv_file):
    # fields
    csvData = [["case_id","label","temp_value","pressure_value","humidity_value","traffic","delay","timestamp"]]

    # for filename in ['vienna-line-71.xes.yaml']:
    with open(yaml_file) as f_input:
        data = yaml.load_all(f_input, yaml.SafeLoader)

        for item in data:
            # extract weather data
            print(item) # for logging purpose
            if 'log' in item: #or 'concept:name' not in item:
                continue

            wea_temp_value = None
            wea_pressure_value = None
            wea_humidity_value = None
            # delay_value = None
            # delay_timestamp = None
            if item is not None and 'event' in item:    # None 인 다큐먼트 처리
                if item['event']['cpee:lifecycle:transition'] == 'sensor/stream' and item['event']['concept:name'] == 'Get Weather':
                    item = item['event']['stream:datastream']
                    for i in item:
                        id=str(i['stream:point']['stream:id'])
                        value=str(i['stream:point']['stream:value'])

                        if id=="temperature":
                            wea_temp_value = value
                        elif id=="pressure":
                            wea_pressure_value = value
                        elif id=="humidity":
                            wea_humidity_value = value

                    csvNewData = [0,"a7",wea_temp_value,wea_pressure_value,wea_humidity_value,'','',wea_timestamp]
                    csvData.append(csvNewData)
                elif item['event']['cpee:lifecycle:transition'] == 'activity/calling' and item['event']['concept:name'] == 'Get Weather':
                    wea_timestamp=item['event']['time:timestamp']

                elif item['event']['cpee:lifecycle:transition'] == 'activity/calling' and item['event']['concept:name'] == 'Get Delays ':
                        delay_timestamp=item['event']['time:timestamp']
                elif item['event']['cpee:lifecycle:transition'] == 'dataelements/change' and item['event'].get(
                    'concept:name') == 'Get Delays ':

                        # datastream = data.get('stream:datastream', [])
                    item_list = item['event']['stream:datastream']
                    for i in item_list:
                            if 'stream:datastream' in i:
                                for sub_item in i['stream:datastream']:
                                    if 'stream:point' in sub_item:
                                        delay_value = sub_item['stream:point']['stream:value']
                                        # timestamp = traffic_timestamp
                                        csvNewData = [0,'a1','','','','',delay_value,delay_timestamp]
                                        csvData.append(csvNewData)

                elif item['event']['cpee:lifecycle:transition'] == 'activity/calling' and item['event']['concept:name'] == 'Get Traffic status':
                    traffic_timestamp=item['event']['time:timestamp']
                elif item['event']['cpee:lifecycle:transition'] == 'sensor/stream' and item['event']['concept:name'] == 'Get Traffic status':
                    item_list = item['event']['stream:datastream']
                    for i in item_list:
                        if 'stream:datastream' in i:
                            for sub_item in i['stream:datastream']:
                                if 'stream:point' in sub_item:
                                    traf_value = sub_item['stream:point']['stream:value']
                                    timestamp = traffic_timestamp
                                    csvNewData = [0,'a8','','','',traf_value,'',traffic_timestamp]
                                    csvData.append(csvNewData)

                elif item['event']['cpee:lifecycle:transition'] == 'activity/calling' and item['event']['concept:name'] == 'Get Related Construction Sites':
                    const_timestamp=item['event']['time:timestamp']
                elif item['event']['cpee:lifecycle:transition'] == 'dataelements/change' and item['event'].get('concept:name') == 'Get Related Construction Sites':
                    item_list = item['event']['stream:datastream']
                    for i in item_list:
                        if 'stream:datastream' in i:
                            for sub_item in i['stream:datastream']:
                                if 'stream:point' in sub_item:
                                    # construction = ?
                                    csvNewData = [0,'a6','','','','','',const_timestamp]
                                    csvData.append(csvNewData)

    with open(csv_file, "w") as f_output:
        for v in csvData:
            line = ','.join(str(r) for r in v)
            f_output.write(line + "\n")

    # Reset csvData if needed
    csvData = [["case_id", "label", "temp_value", "pressure_value", "humidity_value", "traffic", "delay", "timestamp"]]
