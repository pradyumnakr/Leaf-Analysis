from flask import Flask, request, render_template, redirect, url_for, send_file
import os
import pandas as pd
from main import process_images

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
RESULT_FILE = 'leaf_damage_analysis.xlsx'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Process images when the button is clicked
        process_images(app.config['UPLOAD_FOLDER'], RESULT_FILE)
        return redirect(url_for('download'))
    return render_template('index.html')

@app.route('/download')
def download():
    return send_file(RESULT_FILE, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
