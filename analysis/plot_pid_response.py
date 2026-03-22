#!/usr/bin/env python3
"""Plot PID velocity response from a ROS 2 bag file.

Usage:
    python3 plot_pid_response.py <path_to_bag>

Plots:
    - Top: cmd_vel and odom linear.x velocity vs time
    - Bottom: error (cmd_vel - odom) vs time

Output: PNG saved alongside the bag file with the same stem name.
"""

import sys
import os
import pathlib

import rclpy.serialization
import rosbag2_py
from rosidl_runtime_py.utilities import get_message
import numpy as np
import matplotlib.pyplot as plt


def read_topic(reader, topic_name, msg_type_str):
    """Return list of (timestamp_sec, msg) for a given topic."""
    msg_type = get_message(msg_type_str)
    records = []
    reader.seek(0)
    while reader.has_next():
        topic, data, timestamp_ns = reader.read_next()
        if topic == topic_name:
            msg = rclpy.serialization.deserialize_message(data, msg_type)
            records.append((timestamp_ns * 1e-9, msg))
    return records


def extract_linear_x(records):
    times = np.array([t for t, _ in records])
    velocities = np.array([msg.twist.linear.x if hasattr(msg, 'twist') else msg.linear.x
                           for _, msg in records])
    return times, velocities


def load_bag(bag_path):
    storage_options = rosbag2_py.StorageOptions(uri=bag_path, storage_id='mcap')
    converter_options = rosbag2_py.ConverterOptions(
        input_serialization_format='cdr',
        output_serialization_format='cdr',
    )
    reader = rosbag2_py.SequentialReader()
    reader.open(storage_options, converter_options)

    topic_types = {t.name: t.type for t in reader.get_all_topics_and_types()}
    return reader, topic_types


def interpolate_to_common_time(t1, v1, t2, v2):
    """Interpolate v2 onto t1's time base."""
    t_min = max(t1[0], t2[0])
    t_max = min(t1[-1], t2[-1])
    mask1 = (t1 >= t_min) & (t1 <= t_max)
    t_common = t1[mask1]
    v1_common = v1[mask1]
    v2_common = np.interp(t_common, t2, v2)
    return t_common, v1_common, v2_common


def main():
    if len(sys.argv) < 2:
        print("Usage: plot_pid_response.py <path_to_bag>")
        sys.exit(1)

    bag_path = sys.argv[1]
    bag_path = str(pathlib.Path(bag_path).resolve())

    reader, topic_types = load_bag(bag_path)

    if '/odom' not in topic_types:
        print("ERROR: /odom topic not found in bag.")
        print("Available topics:", list(topic_types.keys()))
        sys.exit(1)
    if '/cmd_vel' not in topic_types:
        print("ERROR: /cmd_vel topic not found in bag.")
        print("Available topics:", list(topic_types.keys()))
        sys.exit(1)

    odom_records = read_topic(reader, '/odom', topic_types['/odom'])
    cmd_records = read_topic(reader, '/cmd_vel', topic_types['/cmd_vel'])

    if not odom_records:
        print("ERROR: no /odom messages found.")
        sys.exit(1)
    if not cmd_records:
        print("ERROR: no /cmd_vel messages found.")
        sys.exit(1)

    HALF_WHEEL_BASE = 0.17  # WHEEL_BASE / 2.0 = 0.34 / 2.0

    # odom uses nav_msgs/Odometry: msg.twist.twist.linear.x / angular.z
    t_odom = np.array([t for t, _ in odom_records])
    v_odom = np.array([msg.twist.twist.linear.x for _, msg in odom_records])
    vel_a = np.array([msg.twist.twist.linear.x + msg.twist.twist.angular.z * HALF_WHEEL_BASE
                      for _, msg in odom_records])
    vel_b = np.array([msg.twist.twist.linear.x - msg.twist.twist.angular.z * HALF_WHEEL_BASE
                      for _, msg in odom_records])

    # cmd_vel uses geometry_msgs/Twist: msg.linear.x — convert PWM duty → m/s
    CMD_VEL_SCALE = 0.2933  # 0.088 / 0.3
    v_cmd = np.ones(len(t_odom)) * 0.5 * CMD_VEL_SCALE
    t_cmd = t_odom

    # Normalise time to zero
    t0 = min(t_odom[0], t_cmd[0])
    t_odom -= t0
    t_cmd -= t0

    # Export CSV — interpolate cmd_vel onto odom time base for aligned columns
    v_cmd_on_odom = np.interp(t_odom, t_cmd, v_cmd, left=np.nan, right=np.nan)
    csv_path = pathlib.Path(bag_path).with_suffix('.csv')
    if pathlib.Path(bag_path).is_dir():
        csv_path = pathlib.Path(bag_path).parent / (pathlib.Path(bag_path).name + '.csv')
    csv_data = np.column_stack([t_odom, vel_a, vel_b, v_cmd_on_odom])
    np.savetxt(csv_path, csv_data, delimiter=',', header='time,vel_a,vel_b,cmd_vel', comments='')
    print(f"Saved: {csv_path}")

    # Interpolate onto odom time base for error calculation (use mean of motor velocities)
    v_odom_mean = (vel_a + vel_b) / 2.0
    t_common, v_odom_common, v_cmd_common = interpolate_to_common_time(
        t_odom, v_odom_mean, t_cmd, v_cmd
    )
    error = v_cmd_common - v_odom_common

    # Plot
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 7), sharex=True)
    fig.suptitle(f"PID Velocity Response — {pathlib.Path(bag_path).name}", fontsize=13)

    ax1.plot(t_cmd, v_cmd, label='cmd_vel (m/s)', color='steelblue', linewidth=1.5)
    ax1.plot(t_odom, vel_a, label='motor A (m/s)', color='tomato', linewidth=1.5)
    ax1.plot(t_odom, vel_b, label='motor B (m/s)', color='mediumseagreen', linewidth=1.5)
    ax1.set_ylabel('m/s')
    ax1.legend()
    ax1.grid(True, alpha=0.4)

    ax2.plot(t_common, error, label='error (cmd − odom)', color='darkorange', linewidth=1.2)
    ax2.axhline(0, color='black', linewidth=0.8, linestyle='--')
    ax2.set_ylabel('Error (m/s)')
    ax2.set_xlabel('Time (s)')
    ax2.legend()
    ax2.grid(True, alpha=0.4)

    plt.tight_layout()

    out_path = pathlib.Path(bag_path).with_suffix('.png')
    # If bag_path is a directory (common for rosbag2), use its name
    if pathlib.Path(bag_path).is_dir():
        out_path = pathlib.Path(bag_path).parent / (pathlib.Path(bag_path).name + '.png')

    plt.savefig(out_path, dpi=150)
    print(f"Saved: {out_path}")


if __name__ == '__main__':
    main()
