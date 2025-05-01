from astroplan import FixedTarget, Observer, Transitioner
from astroplan.scheduling import ObservingBlock, Schedule
from astroplan.plots import plot_sky, plot_schedule_airmass
from astropy.time import Time, TimeDelta
from astropy import units as u
import matplotlib.pyplot as plt
import numpy as np

# Suggested targets (user can still enter custom names)
SUGGESTED_TARGETS = ["Deneb", "M13", "Sirius", "algol", "vega"]

# Global list of observing blocks.
blocks = []

def add_target():
    print("\n--- Add Target ---")
    print("Suggested targets: " + ", ".join(SUGGESTED_TARGETS))
    print("Note: Exposure time scale: 1-120 minutes; Priority scale: 1 (highest) to 10 (lowest).")
    target_name = input("Enter target name: ").strip()
    if not target_name:
        print("No target entered, aborting add.")
        return
    try:
        target = FixedTarget.from_name(target_name)
    except Exception as e:
        print("Error finding target '{}': {}".format(target_name, e))
        return
    try:
        exp_minutes = float(input("Enter exposure time in minutes (recommended between 1 and 120): "))
        if exp_minutes < 1 or exp_minutes > 120:
            print("Exposure time out of range. Defaulting to 20 minutes.")
            exp_minutes = 20
    except Exception:
        print("Invalid exposure, defaulting to 20 minutes.")
        exp_minutes = 20
    try:
        priority = int(input("Enter priority (1-10, where 1 is highest): "))
        if priority < 1 or priority > 10:
            print("Priority out of range (should be 1 to 10). Defaulting to 5.")
            priority = 5
    except Exception:
        print("Invalid priority, defaulting to 5.")
        priority = 5

    block = ObservingBlock(target, exp_minutes*u.minute, priority=priority)
    blocks.append(block)
    print("Added block for target '{}' with {} minutes exposure and priority {}."
          .format(target_name, exp_minutes, priority))

def remove_target():
    print("\n--- Remove Target ---")
    if not blocks:
        print("No blocks to remove.")
        return
    list_blocks()
    try:
        idx = int(input("Enter the index number of the target to remove (starting at 0): "))
        if idx < 0 or idx >= len(blocks):
            print("Index out of range.")
            return
    except Exception:
        print("Invalid input.")
        return
    removed = blocks.pop(idx)
    print("Removed block for target '{}'.".format(removed.target.name))

def list_blocks():
    print("\n--- Current Observing Blocks ---")
    if not blocks:
        print("No blocks in the list.")
        return
    for i, blk in enumerate(blocks):
        print("[{}]: Target: {}, Exposure: {} minutes, Priority: {}"
              .format(i, blk.target.name, blk.duration.to(u.minute).value, blk.priority))

def build_schedule():
    if not blocks:
        print("No blocks defined.")
        return None
    # Sort blocks by priority (lower number means higher priority)
    sorted_blocks = sorted(blocks, key=lambda b: b.priority)
    start_time = Time.now()
    gap_time = TimeDelta(1*u.minute)
    scheduled_items = []
    current_time = start_time
    for blk in sorted_blocks:
        scheduled_item = {
            "target": blk.target.name,
            "start_time": current_time,
            "end_time": current_time + blk.duration,
            "duration": blk.duration,
            "priority": blk.priority
        }
        scheduled_items.append(scheduled_item)
        current_time = scheduled_item["end_time"] + gap_time
    return scheduled_items

def show_schedule(scheduled_items):
    if not scheduled_items:
        print("No schedule to show.")
        return
    print("\n--- Schedule ---")
    for i, item in enumerate(scheduled_items):
        print("[{}]: Target: {}, Start: {}, End: {}, Priority: {}"
              .format(i, item["target"], item["start_time"].iso, item["end_time"].iso, item["priority"]))

def plot_schedule(scheduled_items):
    if not scheduled_items:
        print("No schedule to plot.")
        return
    # Gantt chart for schedule
    fig, ax = plt.subplots(figsize=(12, len(scheduled_items) * 0.7 + 1))
    base_time = scheduled_items[0]["start_time"]
    for i, item in enumerate(scheduled_items):
        start = (item["start_time"] - base_time).sec / 60.0  # in minutes
        duration = item["duration"].to(u.minute).value
        ax.broken_barh([(start, duration)], (i - 0.4, 0.8), facecolors='tab:blue')
        ax.text(start + duration/2, i, f'{item["target"]}\n(P{item["priority"]})',
                va="center", ha="center", color="white", fontsize=9)
    ax.set_xlabel("Minutes from schedule start")
    ax.set_ylabel("Block index")
    ax.set_yticks(range(len(scheduled_items)))
    ax.set_title("Observing Schedule - Gantt Chart")
    plt.tight_layout()
    plt.show()

def plot_sky_targets():
    if not blocks:
        print("No blocks to plot on sky.")
        return
    # Create an Observer (default site: 'apo')
    observer = Observer.at_site('apo')
    # Time range: now until one hour later
    time_range = Time([Time.now(), Time.now() + 1*u.hour])
    plt.figure(figsize=(8, 8))
    colors = ['red', 'blue', 'green', 'purple', 'orange']
    for idx, blk in enumerate(blocks):
        plot_sky(blk.target, observer, time_range,
                 style_kwargs={'color': colors[idx % len(colors)],
                               'label': f"{blk.target.name} (P{blk.priority})"})
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.title("Sky Plot of Observing Blocks")
    plt.tight_layout()
    plt.show()

def plot_airmass():
    # This sample function uses astroplan's airmass plotting (if available)
    if not blocks:
        print("No blocks to plot airmass for.")
        return
    observer = Observer.at_site('apo')
    # Define a time grid: now to two hours later in 5 minute intervals
    time_grid = Time.now() + (u.minute * np.array([5 * i for i in range(25)]))
    plt.figure(figsize=(10, 6))
    for blk in blocks:
        try:
            # We use astroplan's plot_schedule_airmass if available.
            plot_schedule_airmass([blk], observer, time_grid,
                                  style_kwargs={'label': f"{blk.target.name} (P{blk.priority})"})
        except Exception as e:
            print("Error plotting airmass for {}: {}".format(blk.target.name, e))
    plt.legend()
    plt.title("Airmass Plot for Observing Blocks")
    plt.xlabel("Time")
    plt.ylabel("Airmass")
    plt.tight_layout()
    plt.show()

def main_menu():
    menu = """
===== Pyscope Observing Blocks Editor =====
1. Add Target (Exposure: 1-120 minutes, Priority: 1-10)
2. Remove Target
3. List Observing Blocks
4. Build & Show Schedule
5. Plot Schedule (Gantt Chart)
6. Plot Sky Targets
7. Plot Airmass Graph
8. Exit
Enter your choice (1-8): """
    while True:
        choice = input(menu).strip()
        if choice == "1":
            add_target()
        elif choice == "2":
            remove_target()
        elif choice == "3":
            list_blocks()
        elif choice == "4":
            schedule = build_schedule()
            if schedule:
                show_schedule(schedule)
        elif choice == "5":
            schedule = build_schedule()
            if schedule:
                plot_schedule(schedule)
        elif choice == "6":
            plot_sky_targets()
        elif choice == "7":
            plot_airmass()
        elif choice == "8":
            print("Exiting.")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    print("Welcome to the Pyscope Observing Blocks Editor (Enhanced DND version)")
    main_menu()