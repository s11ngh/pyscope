from flask import Flask, render_template, request, jsonify, current_app
from flask_cors import CORS  # Add this import
from astroplan import FixedTarget, Observer, Transitioner
from astroplan.scheduling import Schedule, ObservingBlock
from astroplan.plots import plot_schedule_airmass, plot_sky
from astroplan.constraints import AtNightConstraint
from astropy.time import Time, TimeDelta
from astropy import units as u
import matplotlib.pyplot as plt
import numpy as np
import io
import base64
import logging
import sys
import os
import matplotlib
matplotlib.use('Agg')  # Add this line at the top after imports
plt.switch_backend('Agg')

# Add the parent directory to sys.path to import SimpleScheduler
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)
from hardcode import SimpleScheduler  # Import from your local hardcode.py

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

def build_schedule():
    """Build a proper schedule using astroplan"""
    if not blocks:
        return None
    try:
        # Create observer and constraints
        observer = Observer.at_site('apo')
        constraints = [AtNightConstraint()]
        # Create schedule timeframe (from now to 24 hours)
        start_time = Time.now()
        end_time = start_time + 24 * u.hour
        schedule = Schedule(start_time, end_time)
        # Setup transitioner for telescope movements
        transitioner = Transitioner(slew_rate=2 * u.deg/u.second)
        # Sort blocks by priority (lower number means higher priority)
        sorted_blocks = sorted(blocks, key=lambda b: b.priority)
        # Create and run scheduler
        scheduler = SimpleScheduler(
            observer=observer,
            constraints=constraints,
            transitioner=transitioner
        )
        scheduler(sorted_blocks, schedule)
        # Extract scheduled blocks from schedule slots
        scheduled_blocks = [slot.block for slot in schedule.slots if getattr(slot, "block", None) is not None]
        return scheduled_blocks, schedule.start_time
    except Exception as e:
        current_app.logger.error(f"Error building schedule: {str(e)}")
        return None

def build_individual_schedule(single_block):
    """Build a schedule for a single target"""
    try:
        observer = Observer.at_site('apo')
        constraints = [AtNightConstraint()]
        start_time = Time.now()
        end_time = start_time + 24 * u.hour
        schedule = Schedule(start_time, end_time)
        transitioner = Transitioner(slew_rate=2 * u.deg/u.second)
        
        scheduler = SimpleScheduler(
            observer=observer,
            constraints=constraints,
            transitioner=transitioner
        )
        scheduler([single_block], schedule)
        scheduled_blocks = [slot.block for slot in schedule.slots if getattr(slot, "block", None) is not None]
        return scheduled_blocks, schedule.start_time
    except Exception as e:
        current_app.logger.error(f"Error building individual schedule: {str(e)}")
        return None

def generate_schedule_plot():
    """Generate schedule visualizations for individual targets and combined schedule"""
    try:
        # Generate individual schedules
        individual_schedules = []
        for block in blocks:
            result = build_individual_schedule(block)
            if result:
                scheduled_blocks, start_time = result
                # Filter out transition blocks
                scheduled_blocks = [b for b in scheduled_blocks if hasattr(b, 'target')]
                individual_schedules.append({
                    'target': block.target.name,
                    'blocks': scheduled_blocks,
                    'start_time': start_time
                })

        # Generate combined schedule
        combined_result = build_schedule()
        if combined_result is None:
            return jsonify({'error': 'No valid schedule could be created'})
        combined_blocks, combined_start = combined_result
        # Filter out transition blocks from combined schedule
        combined_blocks = [b for b in combined_blocks if hasattr(b, 'target')]
        if not combined_blocks:
            return jsonify({'error': 'No valid schedule blocks found'})

        # Create subplots - one for each individual schedule plus the combined schedule
        n_plots = len(blocks) + 1
        fig = plt.figure(figsize=(12, n_plots * 3))
        
        # Plot individual schedules
        for i, schedule in enumerate(individual_schedules):
            ax = plt.subplot(n_plots, 1, i + 1)
            scheduled_target_blocks = schedule['blocks']
            start_time = schedule['start_time']
            
            for j, block in enumerate(scheduled_target_blocks):
                if hasattr(block, 'start_time'):  # Check if block has start_time
                    start = (block.start_time - start_time).to(u.minute).value
                    duration = block.duration.to(u.minute).value
                    ax.broken_barh([(start, duration)], (0.1, 0.8), 
                                 facecolors='tab:blue')
                    ax.text(start + duration/2, 0.5, 
                           f'{block.target.name}\n(P{block.priority})',
                           va="center", ha="center", color="white", fontsize=9)
            
            ax.set_xlabel("Minutes from start")
            ax.set_yticks([])
            ax.set_title(f"Individual Schedule - {schedule['target']}")
            ax.grid(True, alpha=0.3)

        # Plot combined schedule at the bottom
        ax = plt.subplot(n_plots, 1, n_plots)
        valid_blocks = [(i, block) for i, block in enumerate(combined_blocks) 
                       if hasattr(block, 'start_time')]
        
        for i, block in valid_blocks:
            start = (block.start_time - combined_start).to(u.minute).value
            duration = block.duration.to(u.minute).value
            ax.broken_barh([(start, duration)], (i - 0.4, 0.8), 
                         facecolors='tab:blue')
            ax.text(start + duration/2, i, 
                   f'{block.target.name}\n(P{block.priority})',
                   va="center", ha="center", color="white", fontsize=9)
        
        ax.set_xlabel("Minutes from start")
        ax.set_ylabel("Block")
        ax.set_yticks(range(len(valid_blocks)))
        ax.set_title("Combined Schedule")
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        result = convert_plot_to_base64()
        plt.close(fig)
        return result
    except Exception as e:
        current_app.logger.error(f"Error generating schedule plots: {str(e)}")
        return jsonify({'error': f'Error generating schedule plots: {str(e)}'})

def generate_sky_plot():
    """Generate sky plot with proper target paths"""
    try:
        observer = Observer.at_site('apo')
        now = Time.now()
        sunset = observer.sun_set_time(now, which='next')
        sunrise = observer.sun_rise_time(sunset, which='next')
        time_range = Time([sunset, sunrise])
        fig = plt.figure(figsize=(10, 10))
        ax = plt.subplot(111, projection='polar')
        colors = plt.cm.rainbow(np.linspace(0, 1, len(blocks)))
        for block, color in zip(blocks, colors):
            plot_sky(block.target, observer, time_range,
                     ax=ax,
                     style_kwargs={'color': color,
                                   'label': f"{block.target.name} (P{block.priority})",
                                   'alpha': 0.8})
        ax.set_title(f"Sky Plot - {sunset.datetime.date()}")
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        result = convert_plot_to_base64()
        plt.close(fig)
        return result
    except Exception as e:
        current_app.logger.error(f"Error generating sky plot: {str(e)}")
        return jsonify({'error': f'Error generating sky plot: {str(e)}'})

def generate_airmass_plot():
    """Generate airmass plot with proper time range"""
    try:
        observer = Observer.at_site('apo')
        now = Time.now()
        sunset = observer.sun_set_time(now, which='next')
        sunrise = observer.sun_rise_time(sunset, which='next')
        
        # Ensure sunset and sunrise are valid times
        if sunset is None or sunrise is None:
            current_app.logger.error("Could not determine sunset or sunrise times.")
            return jsonify({'error': 'Could not determine sunset or sunrise times.'})
        
        # Create a time grid from sunset to sunrise
        time_grid = sunset + (sunrise - sunset) * np.linspace(0, 1, 100)
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # For each block, plot its airmass
        for block in blocks:
            try:
                # Calculate airmass values for the target over the time grid
                airmass = observer.altaz(time_grid, block.target).secz
                
                # Plot the airmass values
                ax.plot(time_grid.plot_date, airmass,
                        label=f"{block.target.name} (P{block.priority})")
            
            except Exception as e:
                current_app.logger.error(f"Error plotting airmass for {block.target.name}: {str(e)}")
        
        ax.set_title(f"Airmass Plot - {sunset.datetime.date()}")
        ax.set_xlabel('Time (UTC)')
        ax.set_ylabel('Airmass')
        ax.grid(True, alpha=0.3)
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        # Format the x-axis to display dates properly
        ax.xaxis_date()
        fig.autofmt_xdate()
        
        plt.tight_layout()
        result = convert_plot_to_base64()
        plt.close(fig)
        return result
    
    except Exception as e:
        current_app.logger.error(f"Error generating airmass plot: {str(e)}")
        return jsonify({'error': f'Error generating airmass plot: {str(e)}'})

def convert_plot_to_base64():
    """Convert matplotlib plot to base64 string"""
    try:
        img = io.BytesIO()
        plt.savefig(img, format='png', bbox_inches='tight', dpi=100)
        img.seek(0)
        return base64.b64encode(img.getvalue()).decode()
    except Exception as e:
        current_app.logger.error(f"Error converting plot to base64: {str(e)}")
        raise

@app.route('/plot/<plot_type>')
def generate_plot(plot_type):
    if not blocks:
        return jsonify({'error': 'No blocks defined'})
    try:
        plt.close('all')  # Close any existing plots
        if plot_type == 'schedule':
            return generate_schedule_plot()
        elif plot_type == 'sky':
            return generate_sky_plot()
        elif plot_type == 'airmass':
            return generate_airmass_plot()
        return jsonify({'error': 'Invalid plot type'})
    except Exception as e:
        current_app.logger.error(f"Error generating {plot_type} plot: {str(e)}")
        return jsonify({'error': f'Error generating plot: {str(e)}'})

if __name__ == '__main__':
    app.run(debug=True)