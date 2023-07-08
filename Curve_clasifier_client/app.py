from flask import Flask, render_template, request, redirect, url_for, session
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import os
import json
import numpy as np

app = Flask(__name__, static_url_path='/Curve_clasifier_client/static')
app.config['WTF_CSRF_ENABLED'] = False
app.secret_key = 'your_secret_key'  # you should change this in your real app
user_responses = []

@app.route('/')
def root():
    return redirect(url_for('intro'))

@app.route('/intro', methods=['GET', 'POST'])
def intro(): #add a status page to get to know the status of the corrected dataset, and overviews the output
    if request.method == 'POST':
        session['username'] = request.form.get('username')
        session['session_size'] = request.form.get('session_size')
        return redirect(url_for('home'))
    return render_template('intro.html')
@app.route('/home', methods=['GET', 'POST'])
def home():
    global user_responses
    if 'username' not in session or 'session_size' not in session:
        return redirect(url_for('intro'))
        # Read data from .csv or .json
    file_path = 'Curve_clasifier_client/data/input.json'
    extension = '.json'
    if extension == '.csv':
        df = pd.read_csv('data/input.csv')
    elif extension == '.json':
        with open(file_path) as f:
            data = json.load(f)
    statement = 'Presta?'
    # Extract sub-item
    sub_item_data = np.array(data['curve_data']).T

    # Create data frame
    columns = ['Curve{}'.format(i) for i in range(len(sub_item_data[0]))]
    df = pd.DataFrame(sub_item_data, columns = columns)
    #df = pd.read_json('data/input.json',) #add headers as the curve ids stored
    temperature = [i for i in range(25,375)]


    # # Determine which curves have been measured in previous sessions
    # try:
    #     df_out = pd.read_csv('output.csv')
    #     measured_curves = df_out['curve_id'].unique()
    # except FileNotFoundError:
    #     measured_curves = []

    # # Filter out the measured curves
    # df = df[~df['curve_id'].isin(measured_curves)]

    if df.empty:
        return render_template('end.html')

    # Select a curve to measure

        #curve_id =  df.columns.iloc[0] #select the firs unmeasured curve
    if len(user_responses) == 0:
        curve_id =  list(df.columns)[0]
    if len(user_responses) > 0:
        curve_id =  list(df.columns)[len(user_responses)]  

    #it
    # Plot chart
    plt.figure(figsize=(10, 6))
    plt.plot(temperature, df[curve_id])
    plt.xlabel('Temperature')
    plt.ylabel('Luminescent')
    plt.title('Temperature vs Luminescent')
    plt.grid(True)
    plt.savefig('Curve_clasifier_client/static/image.png', format='png') # --  up to this part itworks, the page doesnt render

    #curve_id = 'your_curve_id'  # Replace with code to get curve id
    if request.method == 'POST':
        choice = request.form.get('choice')
        user_responses.append({
            "measured_attribute": choice,
            "username": session['username'],
            "session_size": session['session_size'],
            "curve_id": curve_id
        })
        #fix output file generation
        if len(user_responses) % 5 == 0:  # if there are five new responses
            try:
                # try to read the existing file
                df_out = pd.read_csv("Curve_clasifier_client/data/output.csv")
                # append new responses to the existing DataFrame
                new_df = pd.DataFrame(user_responses)
                df_out = df_out.append(new_df, ignore_index=True)
            except FileNotFoundError:
                # if the file doesn't exist, create a new DataFrame
                df_out = pd.DataFrame(user_responses)
            # save DataFrame to .csv
            df_out.to_csv("Curve_clasifier_client/data/output.csv", index=False)
            # reset the list after saving
            #user_responses = []
        if len(user_responses) >= int(session['session_size']):
            user_responses = []
            return redirect(url_for('end'))


    return render_template('index.html', curve_id=curve_id, statement=statement)


@app.route('/end', methods=['GET'])
def end():
    return render_template('end.html')