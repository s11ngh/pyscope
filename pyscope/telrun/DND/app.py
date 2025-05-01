from flask import Flask, render_template, request, jsonify, current_app
from flask_cors import CORS  # Add this import
from astroplan import FixedTarget, Observer, Transitioner
from astroplan.scheduling import ObservingBlock
from astropy.time import Time, TimeDelta
from astropy import units as u
import matplotlib.pyplot as plt
import numpy as np
import io
import base64
import logging

app = Flask(__name__)
CORS(app)  # Enable CORS

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    return response

# Add logging configuration
logging.basicConfig(level=logging.DEBUG)

# Global variables
blocks = []
SUGGESTED_TARGETS = ["Deneb", "M13", "Sirius", "algol", "vega"]

@app.route('/')
def index():
    current_app.logger.debug('Rendering index page')
    return render_template('index.html', targets=SUGGESTED_TARGETS)

@app.route('/add_target', methods=['POST'])
def add_target():
    try:
        data = request.json
        target_name = data['target']
        exp_minutes = float(data['exposure'])
        priority = int(data['priority'])

        if exp_minutes < 1 or exp_minutes > 120:
            return jsonify({'error': 'Exposure time must be between 1 and 120 minutes'})
        if priority < 1 or priority > 10:
            return jsonify({'error': 'Priority must be between 1 and 10'})

        target = FixedTarget.from_name(target_name)
        block = ObservingBlock(target, exp_minutes*u.minute, priority=priority)
        blocks.append(block)
        
        return jsonify({
            'status': 'success',
            'message': f'Added target {target_name}'
        })
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/remove_target', methods=['POST'])
def remove_target():
    try:
        idx = int(request.json['index'])
        if 0 <= idx < len(blocks):
            removed = blocks.pop(idx)
            return jsonify({
                'status': 'success',
                'message': f'Removed {removed.target.name}'
            })
        return jsonify({'error': 'Invalid index'})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/list_blocks')
def list_blocks():
    return jsonify([{
        'index': i,
        'target': block.target.name,
        'exposure': block.duration.to(u.minute).value,
        'priority': block.priority
    } for i, block in enumerate(blocks)])

@app.route('/plot/<plot_type>')
def generate_plot(plot_type):
    if not blocks:
        return jsonify({'error': 'No blocks defined'})

    plt.figure(figsize=(10, 6))
    
    if plot_type == 'schedule':
        return generate_schedule_plot()
    elif plot_type == 'sky':
        return generate_sky_plot()
    elif plot_type == 'airmass':
        return generate_airmass_plot()
    
    return jsonify({'error': 'Invalid plot type'})

def generate_schedule_plot():
    sorted_blocks = sorted(blocks, key=lambda b: b.priority)
    start_time = Time.now()
    current_time = start_time
    
    fig, ax = plt.subplots(figsize=(12, len(sorted_blocks) * 0.7 + 1))
    for i, block in enumerate(sorted_blocks):
        duration = block.duration.to(u.minute).value
        ax.broken_barh([(0, duration)], (i - 0.4, 0.8), facecolors='tab:blue')
        ax.text(duration/2, i, f'{block.target.name}\n(P{block.priority})',
                va="center", ha="center", color="white", fontsize=9)
    
    ax.set_xlabel("Minutes from start")
    ax.set_ylabel("Target")
    ax.set_title("Observing Schedule")
    
    return convert_plot_to_base64()

def generate_sky_plot():
    observer = Observer.at_site('apo')
    time_range = Time([Time.now(), Time.now() + 1*u.hour])
    
    colors = ['red', 'blue', 'green', 'purple', 'orange']
    for idx, block in enumerate(blocks):
        plot_sky(block.target, observer, time_range,
                style_kwargs={'color': colors[idx % len(colors)],
                            'label': f"{block.target.name} (P{block.priority})"})
    
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.title("Sky Plot of Targets")
    
    return convert_plot_to_base64()

def generate_airmass_plot():
    observer = Observer.at_site('apo')
    time_grid = Time.now() + (u.minute * np.array([5 * i for i in range(25)]))
    
    for block in blocks:
        try:
            plot_schedule_airmass([block], observer, time_grid,
                                style_kwargs={'label': f"{block.target.name} (P{block.priority})"})
        except Exception as e:
            print(f"Error plotting airmass for {block.target.name}: {e}")
    
    plt.legend()
    plt.title("Airmass Plot")
    
    return convert_plot_to_base64()

def convert_plot_to_base64():
    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    plt.close()
    return base64.b64encode(img.getvalue()).decode()

if __name__ == '__main__':
    app.run(debug=True)