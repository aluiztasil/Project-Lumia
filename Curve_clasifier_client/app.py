from flask import Flask, render_template, request, redirect, url_for, session
import matplotlib.pyplot as plt
import pandas as pd
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # you should change this in your real app
user_responses = []

@app.route('/')
def root():
    return redirect(url_for('intro'))

@app.route('/intro', methods=['GET', 'POST'])
def intro():
    if request.method == 'POST':
        session['username'] = request.form.get('username')
        session['session_size'] = request.form.get('session_size')
        return redirect(url_for('home'))
    return render_template('intro.html')

@app.route('/home', methods=['GET', 'POST'])
def home():
    if 'username' not in session or 'session_size' not in session:
        return redirect(url_for('intro'))
        # Read data from .csv or .json
    file_path = '/data'
    extension = os.path.splitext(file_path)[1]
    if extension == '.csv':
        df = pd.read_csv('data/input.csv')
    elif extension == '.json':
        df = pd.read_json('data/input.json') #add headers as the curve ids stored



    # Determine which curves have been measured in previous sessions
    try:
        df_out = pd.read_csv('output.csv')
        measured_curves = df_out['curve_id'].unique()
    except FileNotFoundError:
        measured_curves = []

    # Filter out the measured curves
    df = df[~df['curve_id'].isin(measured_curves)]

    if df.empty:
        return render_template('end.html')

    # Select a curve to measure
    curve_id =  df['curve_id'].iloc[0] #select the firs unmeasured curve

    #it
    # Plot chart
    plt.figure(figsize=(10, 6))
    plt.plot(df.iloc[:, 0], df.iloc[:, 1])
    plt.xlabel('Temperature')
    plt.ylabel('Luminescent')
    plt.title('Temperature vs Luminescent')
    plt.grid(True)
    plt.savefig('static/image.png', format='png')
    curve_id = 'your_curve_id'  # Replace with code to get curve id
    if request.method == 'POST':
        choice = request.form.get('choice')
        user_responses.append({
            "measured_attribute": choice,
            "username": session['username'],
            "session_size": session['session_size'],
            "curve_id": curve_id
        })
        
        if len(user_responses) % 5 == 0:  # if there are five new responses
            try:
                # try to read the existing file
                df_out = pd.read_csv("output.csv")
                # append new responses to the existing DataFrame
                new_df = pd.DataFrame(user_responses)
                df_out = df_out.append(new_df, ignore_index=True)
            except FileNotFoundError:
                # if the file doesn't exist, create a new DataFrame
                df_out = pd.DataFrame(user_responses)
            # save DataFrame to .csv
            df_out.to_csv("output.csv", index=False)
            # reset the list after saving
            user_responses = []
        if len(user_responses) >= int(session['session_size']):
            return redirect(url_for('end'))


    return render_template('index.html', curve_id=curve_id)

@app.route('/end', methods=['GET'])
def end():
    return render_template('end.html')