from select import select

from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from alpha import alpha
from inductive import inductive
import os
from csvcon import yaml_to_csv
from csvcon2 import extract_to_csv
from temp_delay import temp_delay
from dfgg import dfg
from flask import render_template, flash, redirect, url_for
from markupsafe import Markup
import yaml
import pandas as pd
from heuristics import heuristics
from flask import session

from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'supersecretkey123'

UPLOAD_FOLDER = 'uploads'
CSV_FOLDER = 'converted_csv'     # csv to convert
ALLOWED_EXTENSIONS = {'yaml', 'csv'}    # yaml
FILENAME=""
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CSV_FOLDER, exist_ok=True)
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


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


# @app.route('/yaml')
# def yaml_view():
#     if request.method == 'POST':
#         # Check if a file was uploaded
#         if 'file' not in request.files:
#             return "No file part", 400
#
#         file = request.files['file']
#
#         # If no file is selected
#         if file.filename == '':
#             return "No selected file", 400
#
#         # Save the file securely
#         filename = secure_filename(file.filename)
#         file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#         file.save(file_path)
#
#         # Read the content of the uploaded file
#         with open(file_path, 'r') as uploaded_file:
#             yaml_content = uploaded_file.read()
#
#         # Format the YAML content for HTML rendering
#         formatted_yaml = Markup("<pre>" + yaml_content + "</pre>")
#
#         return render_template('yaml.html', yaml_data=formatted_yaml)

# upload yaml
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    if file:
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        global FILENAME

        if file_extension == 'csv':
            file_path = os.path.join(CSV_FOLDER, file.filename)
            file.save(file_path)
            FILENAME = file_path

        elif file_extension == 'yaml':
            file_path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(file_path)
            csv_filename = file.filename.rsplit('.', 1)[0] + '.csv'
            csv_path = os.path.join(CSV_FOLDER, csv_filename)
            extract_to_csv(file_path, csv_path)
            FILENAME = csv_path

        # Read and extract unique IDs after file is saved
        try:
            df = pd.read_csv(FILENAME, usecols=['stop/attr'])
            unique_ids = df['stop/attr'].dropna()
            # Remove 'traffic' and any IDs that occur only once
            unique_ids = unique_ids[~unique_ids.isin(['traffic'])]
            unique_ids = unique_ids[unique_ids.duplicated(keep=False)].unique().tolist()
            return jsonify({
                "success": True,
                "filename": file.filename,
                "unique_ids": unique_ids
            })

        except Exception as e:
            return jsonify({"error": f"Error processing file: {e}"}), 500

    return jsonify({"error": "Invalid file type"}), 400


@app.route('/generate_buttons', methods=['GET'])
def generate_buttons():
    if not FILENAME:
        print("No file selected.")  # Debugging output
        return jsonify({"error": "No file selected"}), 400

    try:
        print(f"Reading file: {FILENAME}")  # Debugging output
        df = pd.read_csv(FILENAME, usecols=['stop/attr'])

        unique_ids = df['stop/attr'].dropna().unique().tolist()
        print(f"Extracted unique IDs: {unique_ids}")  # Debugging output
        return jsonify({"unique_ids": unique_ids})

    except pd.errors.EmptyDataError:
        print("The file is empty.")
        return jsonify({"error": "The file is empty."}), 400

    except KeyError as e:
        print(f"Missing expected column: {e}")
        return jsonify({"error": f"Missing expected column: {e}"}), 400

    except Exception as e:
        print(f"Error processing file: {e}")  # Debugging output
        return jsonify({"error": f"Error processing file: {e}"}), 500



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


@app.route('/main', methods=['POST','GET'])
def main():
    selected_ids = request.form.getlist('unique_ids')

    # Exclude 'traffic' if the input file is 'vienna-line-71.xes.csv'
    if request.files.get('file') and request.files['file'].filename == 'vienna-line-71.xes.csv':
        selected_ids = [id for id in selected_ids if id != 'traffic']

    session['selected_ids'] = selected_ids

    print(f"Selected IDs in '/main': {selected_ids}")
    return render_template('main.html', selected_ids=selected_ids)

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
    heuristics_variant = request.form.get('heuristics_variant', None)
    selectedKMeansValue = int(request.form.get('selectedKMeansValue', 3))
    selectDBSCANValue = float(request.form.get('selectDBSCANValue', 0.5))
    selectedAggloValue = int(request.form.get('selectedAggloValue', 2))
    selectedArea = request.form.get('selectedArea', None) # area selection
    selected_ids = session.get('selected_ids', [])  # Retrieve the list from session

    # debugging purpose
    print('selectedArea:', selectedArea)  # city center, on the way, zentralfriedhof
    print("selected_value:", selected_value)    # data to see
    print("selected_value1:", selected_value1)  # process discovery
    print("selected_value2:", selected_value2)  # clustering
    print("selected_value3:", selected_value3)  # submit
    print("dfg_variant:", dfg_variant) # dfg param
    print("inductive_var", inductive_variant) # inductive variant
    print("alpha_var", alpha_variant)  # inductive variant
    print("heuristics_var", heuristics_variant) # heuristics variant
    print("selectedKMeansValue:", selectedKMeansValue) # k means param
    print("selectedDBSCANValue:", selectDBSCANValue) # dbscan param
    print("selectedAggloValue:", selectedAggloValue)  # agglomerative param
    print(f"Submitted IDs: {selected_ids}")

#------------------
    global FILENAME

    try:
        if selected_value2 == "K means":
            # if k means
            td_csv = temp_delay(FILENAME, selected_value2, selectedKMeansValue, selected_ids)
        elif selected_value2 == "DBSCAN":
            # if dbscan
            td_csv = temp_delay(FILENAME, selected_value2, selectDBSCANValue, selected_ids)
        elif selected_value2 == "Agglomerative":
            td_csv = temp_delay(FILENAME, selected_value2, selectedAggloValue, selected_ids)

        if len(td_csv) < 2:
            flash('Not enough data points to cluster. Please select more data.', 'error')
            return render_template('main.html', selected_value2=selected_value2)

        # Only reach this part if clustering succeeds and td_csv is valid
        if td_csv is not None:
            if selected_value1 == "Directly Followed Graph":
                image_path = dfg(td_csv, selected_value3, dfg_variant)
            elif selected_value1 == "Inductive Miner":
                image_path = inductive(td_csv, inductive_variant, selected_value3)
            elif selected_value1 == "Heuristics Miner":
                image_path = heuristics(td_csv, heuristics_variant)
            elif selected_value1 == "Alpha Miner":
                image_path = alpha(td_csv, alpha_variant, selected_value3)

            image_url = url_for('static', filename=os.path.basename(image_path))
            # flash('Clustering and process discovery successful!', 'success')
            return render_template('direct_graph.html',
                                   image_url=image_url,
                                   selected_value=selected_value,
                                   selected_value2=selected_value2,
                                   selected_value1=selected_value1,
                                   selected_ids=selected_ids)

    except ValueError as e:
        # Specifically catch the "n_samples < n_clusters" error
        if 'n_samples' in str(e):
            flash('Clustering failed: Not enough data points for the number of clusters requested. Please go back and reselect ids or number of clusters', 'error')
        elif 'Found array with 0 sample(s)' in str(e):
            flash('Clustering failed: No data exists for one of the selected ids. Please go back and reselect a new one.', 'error')
        else:
            flash(f'Clustering failed: {str(e)}', 'error')

        return render_template('main.html', selected_value2=selected_value2)

    except ValueError as e:
        # Specifically catch the "n_samples < n_clusters" error
        if 'n_samples' in str(e):
            flash(
                'Clustering failed: Not enough data points for the number of clusters requested. Please go back and reselect ids or number of clusters',
                'error')
        elif 'Found array with 0 sample(s)' in str(e):
            flash(
                'Clustering failed: No data exists for one of the selected ids. Please go back and reselect a new one.',
                'error')
        else:
            flash(f'Clustering failed: {str(e)}', 'error')

        return render_template('main.html', selected_value2=selected_value2)

    except TypeError as e:
        flash(f"Error: {e}", 'error')
        print(f"Error: {e}")
        return render_template('main.html', selected_value2=selected_value2)

if __name__ == '__main__':

    app.run(host='::1', port=5000, debug=True)
