from flask import Flask, render_template, request, redirect, url_for
from dfg import dfg
from alpha import alpha
from inductive import inductive
import os
from csvcon import yaml_to_csv
from temp_delay import temp_delay
from alpha_temp import dfg
from mult_delay import mult_delay

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
    # Get the selected CSV file from the form
    selected_file = request.form.get('csv_file')
    if not selected_file:
        return "No file selected", 400

    # Construct the full path to the selected CSV file
    file_path = os.path.join(CSV_FOLDER, selected_file)
    global FILENAME
    FILENAME = file_path

    # Do something with the selected CSV file (e.g., process it, display its content, etc.)
    # For now, just return a confirmation message
    return f"Selected file: {file_path}"


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
            return render_template('main.html', message="CSV file uploaded successfully!")

        elif file_extension == 'yaml':
            # Save the yaml file
            file_path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(file_path)

            csv_filename = os.path.join(CSV_FOLDER, file.filename.rsplit('.', 1)[0] + '.csv')
            csv_path = os.path.join(CSV_FOLDER, csv_filename)

            yaml_to_csv(file_path, csv_filename)

            FILENAME=csv_filename
            # print(FILENAME)
            # file.save(file_path)
            return render_template('main.html', message="File uploaded and converted successfully!")
    return "Invalid file type", 400

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

# debugging purpose
    print("selected_value:", selected_value)    # data to see
    print("selected_value1:", selected_value1)  # process discovery
    print("selected_value2:", selected_value2)  # clustering
    print("selected_value3:", selected_value3)  # submit
    print("dfg_variant:", dfg_variant) # dfg param
    print("inductive_var", inductive_variant) # inductive variant
    print("alpha_var", alpha_variant)  # inductive variant
    print("selectedKMeansValue:", selectedKMeansValue) # k means param
    print("selectedDBSCANValue:", selectDBSCANValue) # dbscan param

#------------------
    global FILENAME

    if selected_value == "Temperature":
        td_csv = None
        if selected_value2 == "K means":
            # if k means
            td_csv = temp_delay(FILENAME, selected_value2, selectedKMeansValue)
        if selected_value2 == "DBSCAN":
            # if dbscan
            td_csv = temp_delay(FILENAME, selected_value2, selectDBSCANValue)

        if td_csv is not None:
            if selected_value1 == "Directly Followed Graph":
                image_path = dfg(td_csv, selected_value3, dfg_variant)
                image_url = url_for('static', filename=os.path.basename(image_path))
            # elif selected_value1 == "Petri net":
            #     print(FILENAME)
            #     dfg(FILENAME)
            #     image_url = url_for('static', filename='pn.png')
            elif selected_value1 == "Inductive Miner":
                image_path = inductive(td_csv, inductive_variant, selected_value3)
                image_url = url_for('static', filename=os.path.basename(image_path))
            elif selected_value1 == "Alpha miner":
                image_path = alpha(td_csv, alpha_variant, selected_value3)
                image_url = url_for('static', filename=os.path.basename(image_path))

    if selected_value == "Multiple":
        td_csv = None
        if selected_value2 == "K means":
            td_csv = mult_delay(FILENAME, selected_value2, selectedKMeansValue)
        if selected_value2 == "DBSCAN":
            td_csv = mult_delay(FILENAME, selected_value2, selectDBSCANValue)
        if td_csv is not None:
            if selected_value1 == "Directly Followed Graph":
                    image_path = dfg(td_csv, selected_value3, dfg_variant)
                    image_url = url_for('static', filename=os.path.basename(image_path))
            elif selected_value1 == "Inductive miner":
                image_path = inductive(td_csv, inductive_variant, selected_value3)
                image_url = url_for('static', filename=os.path.basename(image_path))
            elif selected_value1 == "Alpha miner":
                image_path = alpha(td_csv, alpha_variant, selected_value3)
                image_url = url_for('static', filename=os.path.basename(image_path))

    return render_template('direct_graph.html', image_url=image_url)


if __name__ == '__main__':

    app.run(host='127.0.0.1', port=5000, debug=True)
