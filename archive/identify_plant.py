"""
identify_plant.py — Fit a first-order transfer function to a motor step response.

Usage:
    python identify_plant.py <csv_file>

CSV columns: time, vel_a, vel_b, cmd_vel
Model: y(t) = K * (1 - exp(-t / tau))
"""

import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from pathlib import Path


STEP_THRESHOLD = 0.005  # vel_a threshold to detect step start (m/s)


def first_order_step(t, K, tau):
    return K * (1.0 - np.exp(-t / tau))


def main():
    if len(sys.argv) != 2:
        print(f"Usage: python {Path(__file__).name} <csv_file>")
        sys.exit(1)

    csv_path = Path(sys.argv[1])
    if not csv_path.exists():
        print(f"Error: file not found: {csv_path}")
        sys.exit(1)

    df = pd.read_csv(csv_path)

    required = {"time", "vel_a", "vel_b", "cmd_vel"}
    missing = required - set(df.columns)
    if missing:
        print(f"Error: CSV missing columns: {missing}")
        sys.exit(1)

    # Find step start index
    step_indices = np.where(df["vel_a"].values > STEP_THRESHOLD)[0]
    if len(step_indices) == 0:
        print(f"Error: vel_a never exceeds threshold {STEP_THRESHOLD}. Check data.")
        sys.exit(1)

    step_start = step_indices[0]
    print(f"Step start detected at index {step_start} (time={df['time'].iloc[step_start]:.4f} s)")

    # Trim and rezero time
    df = df.iloc[step_start:].copy()
    df["time"] = df["time"] - df["time"].iloc[0]

    t = df["time"].values
    y = df["vel_a"].values

    # Initial guesses: K ~ steady-state value, tau ~ time to 63% of K
    K0 = y[-1] if y[-1] > 0 else y.max()
    tau0 = t[np.argmin(np.abs(y - 0.63 * K0))] if K0 > 0 else 1.0
    p0 = [K0, max(tau0, 1e-3)]

    try:
        popt, pcov = curve_fit(first_order_step, t, y, p0=p0, maxfev=10000)
    except RuntimeError as e:
        print(f"curve_fit failed: {e}")
        sys.exit(1)

    K, tau = popt
    perr = np.sqrt(np.diag(pcov))

    print(f"\nFirst-order fit results:")
    print(f"  K   (DC gain)       = {K:.6f}  ± {perr[0]:.6f}")
    print(f"  tau (time constant) = {tau:.6f} s ± {perr[1]:.6f} s")

    # Plot
    t_fit = np.linspace(t[0], t[-1], 500)
    y_fit = first_order_step(t_fit, K, tau)

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(t, y, label="vel_a (measured)", color="steelblue", linewidth=1.5)
    ax.plot(t_fit, y_fit, label=f"fit: K={K:.4f}, τ={tau:.4f}s",
            color="tomato", linewidth=2, linestyle="--")
    ax.axhline(K, color="gray", linewidth=0.8, linestyle=":")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Velocity (m/s)")
    ax.set_title(f"Plant Identification — {csv_path.name}")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()

    out_path = csv_path.with_name(csv_path.stem + "_plant_fit.png")
    fig.savefig(out_path, dpi=150)
    print(f"\nPlot saved to: {out_path}")
    plt.show()


if __name__ == "__main__":
    main()
