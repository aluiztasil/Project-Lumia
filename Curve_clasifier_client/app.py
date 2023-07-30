from flask import Flask, render_template, request, redirect, url_for, session
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import os
import json
import numpy as np
import random

def generate_curve_points(curve_name, data):
    # Extract metadata
    metadata = data[curve_name]['curve_metadata']
    
    # Extract 'LOW', 'HIGH', and 'NPOINTS' values
    low = metadata['LOW']
    high = metadata['HIGH']
    npoints = metadata['NPOINTS']
    
    # Generate a list with evenly distributed points
    points = np.linspace(low, high, npoints).tolist()
    
    return points


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
    global sampled_curve_names
    if 'username' not in session or 'session_size' not in session:
        return redirect(url_for('intro'))
        # Read data from .csv or .json
    file_path = 'Curve_clasifier_client/data/input.json'
    extension = '.json'
    # if extension == '.csv':
    #     df = pd.read_csv('data/input.csv')
    if extension == '.json':
        with open(file_path) as f:
            data = json.load(f)
    statement = 'Presta?' # what to measure, what statement is should be evaluated? #where should this information be caught from.
    attribute_name = ''
    # Sample curves given the session size
    session_size = min(50, int(session['session_size']))  # Ensure session size is not larger than total number of curves
    sampled_curve_names = random.sample(list(data.keys()), session_size)

    # Collect curve data for sampled curves
    sub_item_data = np.array([data[curve_name]['curve_data'] for curve_name in sampled_curve_names]).T

    # Create data frame
    df = pd.DataFrame(sub_item_data, columns=sampled_curve_names)

    # Iterate over sampled curves and process their metadata
    #for curve_name in sampled_curve_names: 
    # # instead of iterating here address the item via (user_response varivable)
    curve_name = sampled_curve_names[len(user_responses)]
    # Extract metadata
    metadata = data[curve_name]['curve_metadata']
    
    # Extract values
    high_value = metadata['HIGH']
    low_value = metadata['LOW']
    npoints_value = metadata['NPOINTS']
    rate_value = metadata['RATE']
    an_temp_value = metadata['AN_TEMP']
    an_time_value = metadata['AN_TIME']
    
    # Generate curve points
    temperature = generate_curve_points(curve_name, data)
    plt.figure(figsize=(10, 6))
    plt.plot(temperature, df[curve_name])
    plt.xlabel('Temperature')
    plt.ylabel('Luminescent')
    plt.title('Temperature vs Luminescent')
    plt.grid(True)
    plt.savefig('Curve_clasifier_client/static/image.png', format='png') # --  up to this part itworks, the page doesnt render


 




    if df.empty:
        return render_template('end.html')

 
    if request.method == 'POST':
        choice = request.form.get('choice')
        user_responses.append({
            "measured_attribute": choice,
            "username": session['username'],
            "session_size": session['session_size'],
            "curve_id": curve_name
        })
        #fix output file generation
        if len(user_responses) % int(session['session_size']):  # save file only in the end of the session (?)
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


    return render_template('index.html', curve_id=curve_name, statement=statement,
                           high_value=high_value, low_value=low_value, npoints_value=npoints_value,
                           rate_value=rate_value, an_temp_value=an_temp_value, an_time_value=an_time_value)

@app.route('/end', methods=['GET'])
def end():
    return render_template('end.html')