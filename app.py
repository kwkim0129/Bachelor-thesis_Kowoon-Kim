from select import select

from flask import Flask, render_template, request, redirect, url_for
from alpha import alpha
from inductive import inductive
import os
from csvcon import yaml_to_csv
from csvcon2 import extract_to_csv
from temp_delay import temp_delay
from dfgg import dfg
from flask import render_template
from markupsafe import Markup
import yaml
import pandas as pd
from heuristics import heuristics

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
CSV_FOLDER = 'converted_csv'     # csv to convert
ALLOWED_EXTENSIONS = {'yaml', 'csv'}    # yaml
FILENAME=""
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CSV_FOLDER, exist_ok=True)

@app.route('/')
def home():
    # Get list of CSV files
    csv_files = os.listdir(CSV_FOLDER)
    # Pass the list of files to the template
    return render_template('main.html', csv_files=csv_files)

@app.route('/use_existing_csv', methods=['POST'])
def use_existing_csv():
    selected_file = request.form.get('csv_file')
    if selected_file:
        global FILENAME
        FILENAME = os.path.join(CSV_FOLDER, selected_file)  # Set FILENAME to the selected CSV path
        return redirect(url_for('generate_buttons'))  # Redirect to generate_buttons to display unique_ids
    return "No file selected", 400


@app.route('/yaml')
def yaml_view():
    # page that shows raw yaml file
    with open("vienna-line-71.xes.yaml", "r") as file:
        yaml_content = file.read()

    formatted_yaml = Markup("<pre>" + yaml_content + "</pre>")

    return render_template('yaml.html', yaml_data=formatted_yaml)

# upload yaml
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part", 400

    file = request.files['file']
    if file.filename == '':
        return "No file selected", 400

    if file:
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        global FILENAME

        if file_extension == 'csv':
            file_path = os.path.join(CSV_FOLDER, file.filename)
            file.save(file_path)

            FILENAME = file_path
            return redirect(url_for('generate_buttons'))  # Redirect after uploading CSV

        elif file_extension == 'yaml':
            file_path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(file_path)

            csv_filename = file.filename.rsplit('.', 1)[0] + '.csv'
            csv_path = os.path.join(CSV_FOLDER, csv_filename)
            extract_to_csv(file_path, csv_path)

            FILENAME = csv_path  # Set FILENAME to the converted CSV file
            return redirect(url_for('generate_buttons'))  # Redirect after conversion

    return "Invalid file type", 400


@app.route('/generate_buttons', methods=['GET', 'POST'])
def generate_buttons():
    if not FILENAME:
        return "No file selected. Please upload a file first.", 400

    try:
        # Read only the id_id column from the CSV file
        df = pd.read_csv(FILENAME, usecols=['stop/attr'])
        unique_ids = df['stop/attr'].dropna().unique()  # Get unique and non-NaN values
        print(f"Unique 'stop/attr' values extracted: {unique_ids}")

        # Pass unique IDs to the template
        return render_template('main.html', unique_ids=unique_ids)
    except Exception as e:
        return f"Error processing file: {e}", 500

@app.route('/direct_graph', methods=['POST'])
def show_graph():
    selectedArea = request.form.get('selectedArea')
    selected_value = request.form.get('selected_value')

    # Image URL could be dynamically generated based on the area and value
    image_url = '/static/graph_image.png'

    return render_template('direct_graph.html',
                           selected_area=selectedArea,
                           selected_value=selected_value,
                           image_url=image_url)


@app.route('/main', methods=['POST'])
def main():
    # Get the selected unique IDs (this will be a list of values)
    selected_ids = request.form.getlist('unique_ids')

    # If multiple IDs are selected, assign them to id1, id2
    if len(selected_ids) >= 2:
        id1 = selected_ids[0]
        id2 = selected_ids[1]
    else:
        id1 = selected_ids[0] if selected_ids else None
        id2 = None

    print(f"Selected IDs in '/main': id1 = {id1}, id2 = {id2}")

    # Render main.html with the selected IDs for further action
    return render_template('main.html', id1=id1, id2=id2)

# button 마다 algorithm 설정해주기
@app.route('/submit', methods=['POST'])
def submit():
    print("Request form data:", request.form)
    image_url=""
    selected_value = request.form.get('selected_value', None)  # Get value from data to cluster
    selected_value1 = request.form.get('selected_value1', None)  # Get value from process discovery
    selected_value2 = request.form.get('selected_value2', None)  # Get value from clustering
    selected_value3 = request.form.get('selected_value3', None) # submit
    dfg_variant = request.form.get('dfg_variant', None)
    inductive_variant = request.form.get('inductive_variant', None)
    alpha_variant = request.form.get('alpha_variant', None)
    selectedKMeansValue = int(request.form.get('selectedKMeansValue', 3))
    selectDBSCANValue = float(request.form.get('selectDBSCANValue', 0.5))
    selectedAggloValue = int(request.form.get('selectedAggloValue', 2))
    selectedArea = request.form.get('selectedArea', None) # area selection
    id1 = request.form.get('id1', None) # a1,a6,a7,a8
    id2 = request.form.get('id2', None)  # a1,a6,a7,a8

# debugging purpose
    print('selectedArea:', selectedArea)  # city center, on the way, zentralfriedhof
    print("selected_value:", selected_value)    # data to see
    print("selected_value1:", selected_value1)  # process discovery
    print("selected_value2:", selected_value2)  # clustering
    print("selected_value3:", selected_value3)  # submit
    print("dfg_variant:", dfg_variant) # dfg param
    print("inductive_var", inductive_variant) # inductive variant
    print("alpha_var", alpha_variant)  # inductive variant
    print("selectedKMeansValue:", selectedKMeansValue) # k means param
    print("selectedDBSCANValue:", selectDBSCANValue) # dbscan param
    print("selectedAggloValue:", selectedAggloValue)  # agglomerative param
    print("id1:", id1) # a1,a6,a7,a8 - change later to names
    print("id2:", id2)  # a1,a6,a7,a8 - change later to names

#------------------
    global FILENAME

    # if selected_value == "Temperature":
    #     td_csv = None
    if selected_value2 == "K means":
        # if k means
        td_csv = temp_delay(FILENAME, selected_value2, selectedKMeansValue, selectedArea, id1, id2)
    if selected_value2 == "DBSCAN":
        # if dbscan
        td_csv = temp_delay(FILENAME, selected_value2, selectDBSCANValue, selectedArea, id1, id2)
    if selected_value2 == "Agglomerative":
        td_csv = temp_delay(FILENAME, selected_value2, selectedAggloValue, selectedArea, id1, id2)

    if td_csv is not None:
        if selected_value1 == "Directly Followed Graph":
            image_path = dfg(td_csv, selected_value3, dfg_variant)
            image_url = url_for('static', filename=os.path.basename(image_path))
        elif selected_value1 == "Inductive Miner":
            image_path = inductive(td_csv, inductive_variant, selected_value3)
            image_url = url_for('static', filename=os.path.basename(image_path))
        elif selected_value1 == "Heuristics Miner":
            image_path = heuristics(td_csv)
            image_url = url_for('static', filename=os.path.basename(image_path))
        elif selected_value1 == "Alpha Miner":
            image_path = alpha(td_csv, alpha_variant, selected_value3)
            image_url = url_for('static', filename=os.path.basename(image_path))

    return render_template('direct_graph.html',
                           image_url=image_url,
                           selected_value=selected_value,
                           selectedArea=selectedArea,
                           selected_value2=selected_value2,
                           selected_value1=selected_value1,
                           id1=id1,
                           id2=id2)

if __name__ == '__main__':

    app.run(host='127.0.0.1', port=5000, debug=True)
