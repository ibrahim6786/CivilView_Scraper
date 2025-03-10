from flask import Flask, render_template_string, jsonify, send_file
from CivilView import Scraper, HTML_TEMPLATE
import pandas as pd
import threading
import io


app = Flask(__name__)

scraper = Scraper()


@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)


@app.route('/run-scraper')
def run_scraper():
    if scraper.is_running:
        return jsonify({'status': 'running', 'message': 'Scraper is already running.'})
    # Start the scraper in a background thread.
    thread = threading.Thread(target=scraper.start)
    thread.start()
    return jsonify({'status': 'started', 'message': 'Scraper started.'})


@app.route('/progress')
def progress():
    return jsonify({'progress': scraper.progress})


@app.route('/download-excel')
def download_excel():
    try:
        df = scraper.get_dataframe()
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)
        output.seek(0)
        return send_file(
            output,
            as_attachment=True,
            download_name=f"{scraper.filenm}.xlsx",
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
