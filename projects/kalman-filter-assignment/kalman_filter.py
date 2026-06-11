"""
AI for Robotics - Assignment 3 (CLO 3)
Kalman Filter Implementation and Analysis
Mobile robot position estimation on a straight path
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

np.random.seed(42)

# ----------------------------------------------------------------
# Simulation Parameters
# ----------------------------------------------------------------
dt   = 0.1   # time step (s)
T    = 50    # total time steps
t    = np.arange(T) * dt

a_true  = 0.5   # true constant acceleration (m/s^2)
x0_pos  = 0.0   # initial position (m)
v0      = 1.0   # initial velocity (m/s)

true_pos = x0_pos + v0 * t + 0.5 * a_true * t**2

# ----------------------------------------------------------------
# State Space Matrices
# State: [position, velocity]^T
# ----------------------------------------------------------------
A = np.array([[1.0, dt ],
              [0.0, 1.0]])

B = np.array([[0.5 * dt**2],
              [dt          ]])

H = np.array([[1.0, 0.0]])   # only position is measured

# Baseline noise covariances
Q_base = 0.1 * np.eye(2)
R_base = np.array([[1.0]])

# Control input (known constant acceleration)
u = np.ones((1, T)) * a_true

# ----------------------------------------------------------------
# Generate noisy measurements (baseline R)
# ----------------------------------------------------------------
meas_std    = float(np.sqrt(R_base[0, 0]))
measurements = true_pos + np.random.normal(0, meas_std, T)


# ----------------------------------------------------------------
# Kalman Filter
# ----------------------------------------------------------------
def kalman_filter(z, A, B, H, Q, R, u=None):
    """
    Run a discrete Kalman filter.

    Returns
    -------
    x_est   : (n, T) posterior state estimates
    P_est   : (n, n, T) posterior covariances
    x_pred  : (n, T) prior state predictions
    P_pred  : (n, n, T) prior covariances
    K_hist  : (n, m, T) Kalman gains
    innov   : (m, T) innovations (residuals)
    """
    T_steps = len(z)
    n = A.shape[0]
    m = H.shape[0]

    if u is None:
        u = np.zeros((B.shape[1], T_steps))

    x_est  = np.zeros((n, T_steps))
    P_est  = np.zeros((n, n, T_steps))
    x_pred = np.zeros((n, T_steps))
    P_pred = np.zeros((n, n, T_steps))
    K_hist = np.zeros((n, m, T_steps))
    innov  = np.zeros((m, T_steps))

    x = np.array([[0.0], [0.0]])
    P = 10.0 * np.eye(n)

    for k in range(T_steps):
        uk = u[:, k:k+1]
        zk = np.array([[z[k]]])

        # ---- Prediction ----
        x_minus = A @ x + B @ uk
        P_minus = A @ P @ A.T + Q

        # ---- Correction ----
        S = H @ P_minus @ H.T + R
        K = P_minus @ H.T @ np.linalg.inv(S)
        e = zk - H @ x_minus           # innovation
        x = x_minus + K @ e
        P = (np.eye(n) - K @ H) @ P_minus

        x_pred[:, k] = x_minus.flatten()
        P_pred[:, :, k] = P_minus
        x_est[:, k]  = x.flatten()
        P_est[:, :, k] = P
        K_hist[:, :, k] = K
        innov[:, k]  = e.flatten()

    return x_est, P_est, x_pred, P_pred, K_hist, innov


# ----------------------------------------------------------------
# Baseline run
# ----------------------------------------------------------------
x_est, P_est, x_pred, P_pred, K_hist, innov = kalman_filter(
    measurements, A, B, H, Q_base, R_base, u
)

# RMSE
rmse_meas = np.sqrt(np.mean((measurements - true_pos)**2))
rmse_kf   = np.sqrt(np.mean((x_est[0] - true_pos)**2))
print(f"RMSE - Noisy measurements : {rmse_meas:.4f} m")
print(f"RMSE - Kalman estimate    : {rmse_kf:.4f} m")
print(f"Noise reduction           : {(1 - rmse_kf / rmse_meas)*100:.1f}%")
print(f"Final P[0,0]              : {P_est[0,0,-1]:.6f}")
print(f"Final P[1,1]              : {P_est[1,1,-1]:.6f}")
print(f"Final K[0]                : {K_hist[0,0,-1]:.6f}")
print(f"Final K[1]                : {K_hist[1,0,-1]:.6f}")

out = "projects/kalman-filter-assignment"


# ================================================================
# Plot 1 — True position, noisy measurements, KF estimate
# ================================================================
fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(t, true_pos, 'g-', lw=2, label='True Position', zorder=4)
ax.plot(t, measurements, 'r.', alpha=0.55, ms=5, label='Noisy Measurements', zorder=2)
ax.plot(t, x_est[0], 'b-', lw=2, label='Kalman Estimate', zorder=5)
ax.fill_between(t,
                x_est[0] - 2*np.sqrt(P_est[0, 0, :]),
                x_est[0] + 2*np.sqrt(P_est[0, 0, :]),
                alpha=0.18, color='blue', label='+/-2 sigma Confidence')
ax.set_xlabel('Time (s)')
ax.set_ylabel('Position (m)')
ax.set_title('Robot Position: True vs Noisy Measurements vs Kalman Estimate')
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(out, 'plot1_position_estimate.png'), dpi=150, bbox_inches='tight')
plt.close()
print("Saved plot1_position_estimate.png")


# ================================================================
# Plot 2 — Covariance evolution (posterior + prior)
# ================================================================
fig, axes = plt.subplots(1, 2, figsize=(13, 4))

axes[0].plot(t, P_est[0, 0, :],  'b-',  lw=2,   label='Posterior P[0,0]')
axes[0].plot(t, P_pred[0, 0, :], 'b--', lw=1.5, alpha=0.7, label='Prior P-[0,0]')
axes[0].set_xlabel('Time (s)')
axes[0].set_ylabel('Covariance (m^2)')
axes[0].set_title('Position Variance over Time')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

axes[1].plot(t, P_est[1, 1, :],  'r-',  lw=2,   label='Posterior P[1,1]')
axes[1].plot(t, P_pred[1, 1, :], 'r--', lw=1.5, alpha=0.7, label='Prior P-[1,1]')
axes[1].set_xlabel('Time (s)')
axes[1].set_ylabel('Covariance ((m/s)^2)')
axes[1].set_title('Velocity Variance over Time')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

plt.suptitle('Covariance Evolution (Q=0.1, R=1.0)', y=1.02)
plt.tight_layout()
plt.savefig(os.path.join(out, 'plot2_covariance_evolution.png'), dpi=150, bbox_inches='tight')
plt.close()
print("Saved plot2_covariance_evolution.png")


# ================================================================
# Plot 3 — Kalman Gain at each iteration
# ================================================================
fig, axes = plt.subplots(1, 2, figsize=(13, 4))

axes[0].plot(t, K_hist[0, 0, :], 'b-', lw=2)
axes[0].set_xlabel('Time (s)')
axes[0].set_ylabel('Gain K[0]')
axes[0].set_title('Kalman Gain for Position State')
axes[0].grid(True, alpha=0.3)

axes[1].plot(t, K_hist[1, 0, :], 'r-', lw=2)
axes[1].set_xlabel('Time (s)')
axes[1].set_ylabel('Gain K[1]')
axes[1].set_title('Kalman Gain for Velocity State')
axes[1].grid(True, alpha=0.3)

plt.suptitle('Kalman Gain Evolution over Time', y=1.02)
plt.tight_layout()
plt.savefig(os.path.join(out, 'plot3_kalman_gain.png'), dpi=150, bbox_inches='tight')
plt.close()
print("Saved plot3_kalman_gain.png")


# ================================================================
# Plot 4 — Effect of varying Q
# ================================================================
Q_values = [0.01, 0.1, 1.0, 10.0]
colors_q  = ['blue', 'green', 'orange', 'red']

fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(t, true_pos,    'k-',  lw=2.5, label='True Position', zorder=5)
ax.plot(t, measurements, '.', color='lightgray', ms=4, alpha=0.6, label='Measurements')

for Qv, col in zip(Q_values, colors_q):
    Q_test = Qv * np.eye(2)
    xe, *_ = kalman_filter(measurements, A, B, H, Q_test, R_base, u)
    ax.plot(t, xe[0], color=col, lw=1.8, label=f'Q={Qv}')

ax.set_xlabel('Time (s)')
ax.set_ylabel('Position (m)')
ax.set_title('Effect of Process Noise Covariance Q on Kalman Estimate (R=1.0 fixed)')
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(out, 'plot4_effect_of_Q.png'), dpi=150, bbox_inches='tight')
plt.close()
print("Saved plot4_effect_of_Q.png")


# ================================================================
# Plot 5 — Effect of varying R
# ================================================================
R_values  = [0.1, 1.0, 10.0, 100.0]
colors_r  = ['blue', 'green', 'orange', 'red']

fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(t, true_pos,    'k-',  lw=2.5, label='True Position', zorder=5)
ax.plot(t, measurements, '.', color='lightgray', ms=4, alpha=0.6, label='Measurements')

for Rv, col in zip(R_values, colors_r):
    R_test = np.array([[Rv]])
    xe, *_ = kalman_filter(measurements, A, B, H, Q_base, R_test, u)
    ax.plot(t, xe[0], color=col, lw=1.8, label=f'R={Rv}')

ax.set_xlabel('Time (s)')
ax.set_ylabel('Position (m)')
ax.set_title('Effect of Measurement Noise Covariance R on Kalman Estimate (Q=0.1 fixed)')
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(out, 'plot5_effect_of_R.png'), dpi=150, bbox_inches='tight')
plt.close()
print("Saved plot5_effect_of_R.png")


# ================================================================
# Plot 6 — Innovation (residual) over time
# ================================================================
innov_std = np.sqrt(float(R_base[0, 0]) + P_pred[0, 0, :])   # S = H P- H' + R

fig, ax = plt.subplots(figsize=(12, 4))
ax.plot(t, innov[0], color='purple', lw=1.8, label='Innovation (residual)')
ax.axhline(0, color='k', ls='--', lw=1)
ax.fill_between(t, -2*innov_std, 2*innov_std,
                alpha=0.15, color='purple', label='+/-2 sigma Innovation bound')
ax.set_xlabel('Time (s)')
ax.set_ylabel('Innovation (m)')
ax.set_title('Innovation (Residual) z_k - H x-_k over Time')
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(out, 'plot6_innovation.png'), dpi=150, bbox_inches='tight')
plt.close()
print("Saved plot6_innovation.png")

print("\nAll 6 plots saved successfully.")
