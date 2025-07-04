# -*- coding: utf-8 -*-
"""radiative-cooling-simulation.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1enRGjfnrDZRa6-rZMLWa3nLi8z_ntATh
"""

# input parameters
T_initial = 600
T_ambient = 300
emissivity = 0.8
surface_area = 0.1
mass = 1.0
specific_heat = 500
total_time = 4000
time_step = 10

# Stefan-Boltzmann constant
sigma = 5.67e-8

# importing packages
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

"""The modeling of radiative heat transfer involves several key parameters:
- Emissivity (ε): Represents how effectively a surface emits thermal radiation compared to a black body.
  Higher emissivity values (closer to 1) indicate more effective radiative cooling.
- Surface area to mass ratio (A/m): Determines the cooling rate. Objects with higher surface area
  to mass ratios cool more rapidly due to increased radiative heat transfer per unit mass.
- Temperature difference (Ts⁴-T∞⁴): The fourth-power relationship causes dramatic increases in
  radiative heat transfer at higher temperatures, explaining why cooling is initially rapid.
"""

# define the ODE representing the energy balance
def temperature_derivative(t, T):
    q_rad = sigma * surface_area * emissivity * (T**4 - T_ambient**4)
    dT_dt = -q_rad / (mass * specific_heat)

    return dT_dt

# time points for solution
t_span = (0, total_time)
t_eval = np.arange(0, total_time + time_step, time_step)

# solve
solution = solve_ivp(
    temperature_derivative,
    t_span,
    [T_initial],
    method='RK45',
    t_eval=t_eval,
    rtol=1e-6
)

# extract solution
time = solution.t
temperature = solution.y[0]

"""The simulation reveals the distinctly non-linear cooling profile characteristic of radiative heat transfer:
1. Initial Rapid Cooling Phase: When the temperature difference is large, the T⁴ term dominates,
   resulting in rapid cooling during the early stages.
2. Diminishing Cooling Rate: As the object approaches ambient temperature, the cooling rate
   decreases dramatically due to the reduced temperature difference.
3. Asymptotic Behavior: The object never reaches exactly the ambient temperature in theory,
   though it approaches it asymptotically. In practice, other heat transfer mechanisms would
   eventually dominate at small temperature differences.
"""

# Saving original values
original_time = time.copy()
original_temperature = temperature.copy()

# calculate radiative heat transfer at each time point
radiative_heat_transfer = np.zeros_like(temperature)
for i, T in enumerate(temperature):
    radiative_heat_transfer[i] = sigma * surface_area * emissivity * (T**4 - T_ambient**4)

# calculate cooling rate (K/s) at each time point
cooling_rate = np.zeros_like(temperature)
cooling_rate[0:-1] = -np.diff(temperature) / np.diff(time)
cooling_rate[-1] = cooling_rate[-2]

# calculate time to reach specific temperatures
def time_to_reach_temperature(target_temp):
    if target_temp >= T_initial or target_temp <= T_ambient:
        return None

    for i, T in enumerate(temperature):
        if T <= target_temp:
            if i > 0:
                dt = time[i] - time[i-1]
                dT = temperature[i-1] - temperature[i]
                offset = (temperature[i-1] - target_temp) / dT * dt
                return time[i-1] + offset
            return time[i]

    return None

# calculate time to reach 90%, 50%, and 10% of cooling
cooling_range = T_initial - T_ambient
temp_90_percent = T_initial - 0.1 * cooling_range
temp_50_percent = T_initial - 0.5 * cooling_range
temp_10_percent = T_initial - 0.9 * cooling_range

time_90_percent = time_to_reach_temperature(temp_90_percent)
time_50_percent = time_to_reach_temperature(temp_50_percent)
time_10_percent = time_to_reach_temperature(temp_10_percent)

"""The cooling process exhibits distinct time scales that characterize the radiative heat transfer:
1. Initial Cooling Period (t₉₀): The time to cool by 10% represents the rapid initial response.
   This period is dominated by the T⁴ term and shows the highest heat transfer rates.
2. Half-Cooling Time (t₅₀): The time to reach the midpoint temperature provides a useful
   benchmark for comparing different cooling scenarios. It represents a balance between
   the initial rapid cooling and the later slow approach to ambient temperature.
3. Near-Equilibrium Time (t₁₀): The time to reach 90% of the cooling range indicates when
   the object is approaching thermal equilibrium with its surroundings. The cooling rate
   at this point is substantially reduced compared to the initial rate.

These characteristic times scale differently with changes in material properties and
environmental conditions, providing valuable insights for thermal management design.
"""

# plotting
plt.figure(figsize=(15, 10))

# temp vs time plot
plt.subplot(2, 2, 1)
plt.plot(time, temperature, 'b-', linewidth=2)
plt.axhline(y=T_ambient, color='r', linestyle='--', label=f'Ambient ({T_ambient} K)')
plt.xlabel('Time (s)')
plt.ylabel('Temperature (K)')
plt.title('Object Temperature vs. Time')
plt.grid(True)
plt.legend()

# radiative heat transfer vs time plot
plt.subplot(2, 2, 2)
plt.plot(time, radiative_heat_transfer, 'g-', linewidth=2)
plt.xlabel('Time (s)')
plt.ylabel('Radiative Heat Transfer (W)')
plt.title('Radiative Heat Transfer vs. Time')
plt.grid(True)

# cooling rate vs time plot
plt.subplot(2, 2, 3)
plt.plot(time, cooling_rate, 'm-', linewidth=2)
plt.xlabel('Time (s)')
plt.ylabel('Cooling Rate (K/s)')
plt.title('Cooling Rate vs. Time')
plt.grid(True)

# temperature vs radiative heat transfer
plt.subplot(2, 2, 4)
plt.plot(temperature, radiative_heat_transfer, 'r-', linewidth=2)
plt.xlabel('Temperature (K)')
plt.ylabel('Radiative Heat Transfer (W)')
plt.title('Radiative Heat Transfer vs. Temperature')
plt.grid(True)
plt.gca().invert_xaxis()

plt.tight_layout()

# metrics
print(f"Initial temperature: {T_initial} K")
print(f"Ambient temperature: {T_ambient} K")
print(f"Time to cool to 90% of initial temperature ({temp_90_percent:.1f} K): {time_90_percent:.1f} seconds")
print(f"Time to cool to 50% of temperature difference ({temp_50_percent:.1f} K): {time_50_percent:.1f} seconds")
print(f"Time to cool to 10% of temperature difference ({temp_10_percent:.1f} K): {time_10_percent:.1f} seconds")

# show the plot
plt.show()

"""The relationship between radiative heat transfer and temperature follows the Stefan-Boltzmann Law:
P = σAε(Ts⁴-T∞⁴)

Key observations from this relationship:
1. Power Sensitivity: A small change in temperature at high temperatures results in a much
   larger change in radiative power compared to the same temperature change at lower temperatures.
2. Engineering Implications: This non-linear relationship makes radiative cooling particularly
   effective for high-temperature applications, such as in spacecraft thermal management or
   industrial furnace cooling.
3. Diminishing Returns: As the object cools, the effectiveness of radiative cooling diminishes,
   which may necessitate supplementary cooling mechanisms in practical applications where
   rapid cooling to ambient temperature is required.
"""

# Simulating different materials in different environments, conditions by changing parameters
emissivities = [0.2, 0.4, 0.6, 0.8, 1.0]  # Range of emissivities
masses = [0.2, 0.4, 0.6, 0.8, 1.0] # Range of masses
specific_heats = [200, 300, 400, 500, 600] # Range of specific heats

# Modified equation
def temperature_derivative_2(t, T, mass_v, specific_heat_v, emissivity_v):
    dT_dt = -emissivity_v * sigma * surface_area * (T**4 - T_ambient**4) / (mass_v * specific_heat_v)
    return dT_dt

# Plotting and calculating ratios for changing emissivity
plt.figure(figsize=(10, 6))
for e in emissivities:
    solution = solve_ivp(
        temperature_derivative_2,
        t_span,
        [T_initial],
        args=(mass, specific_heat, e),
        method='RK45',
        t_eval=t_eval,
        rtol=1e-6
      )
    time = solution.t
    temperature = solution.y[0]
    time_50_percent = time_to_reach_temperature(temp_50_percent)
    print(f"Time to cool to 50% of temperature difference ({temp_50_percent:.1f} K) at emissivity {e:.1f}: {time_50_percent:.1f} seconds")
    plt.plot(solution.t, solution.y[0], label=f'Emissivity = {e}')

plt.xlabel('Time (s)')
plt.ylabel('Temperature (K)')
plt.title('Impact of Emissivity on Cooling')
plt.legend()
plt.grid(True)
plt.show()

# Plotting and calculating ratios for changing mass
plt.figure(figsize=(10, 6))
for m in masses:
    solution = solve_ivp(
        temperature_derivative_2,
        t_span,
        [T_initial],
        args=(m, specific_heat, emissivity),
        method='RK45',
        t_eval=t_eval,
        rtol=1e-6
      )
    time = solution.t
    temperature = solution.y[0]
    time_50_percent = time_to_reach_temperature(temp_50_percent)
    print(f"Time to cool to 50% of temperature difference ({temp_50_percent:.1f} K) at mass {m:.1f}: {time_50_percent:.1f} seconds")
    plt.plot(solution.t, solution.y[0], label=f'Mass = {m}')

plt.xlabel('Time (s)')
plt.ylabel('Temperature (K)')
plt.title('Impact of Mass on Cooling')
plt.legend()
plt.grid(True)
plt.show()

# Plotting and calculating ratios for changing specific heat
plt.figure(figsize=(10, 6))
for sh in specific_heats:
    solution = solve_ivp(
        temperature_derivative_2,
        t_span,
        [T_initial],
        args=(mass, sh, emissivity),
        method='RK45',
        t_eval=t_eval,
        rtol=1e-6
      )
    time = solution.t
    temperature = solution.y[0]
    time_50_percent = time_to_reach_temperature(temp_50_percent)
    print(f"Time to cool to 50% of temperature difference ({temp_50_percent:.1f} K) at specific heat {sh:.1f}: {time_50_percent:.1f} seconds")
    plt.plot(solution.t, solution.y[0], label=f'Specific heat = {sh}')

plt.xlabel('Time (s)')
plt.ylabel('Temperature (K)')
plt.title('Impact of Specific heat on Cooling')
plt.legend()
plt.grid(True)
plt.show()

# Simulating non-constant emissivity

# A simple emissivity - temperature function
def emissivityFunction(T):
    return 0.992 - 0.35 * np.exp(-0.0045 * (T - 300)) # Constraint: Average 0.8 in [300, 600]K

# Modified ODE to include variable emissivity
def temperature_derivative_3(t, T):
    dT_dt = -sigma * surface_area * emissivityFunction(T) * (T**4 - T_ambient**4) / (mass * specific_heat)
    return dT_dt

# Extract solution
solution = solve_ivp(
    temperature_derivative_3,
    t_span,
    [T_initial],
    method='RK45',
    t_eval = t_eval,
    rtol=1e-6
  )
time = solution.t
temperature = solution.y[0]

# Calculating metrics
time_90_percent = time_to_reach_temperature(temp_90_percent)
time_50_percent = time_to_reach_temperature(temp_50_percent)
time_10_percent = time_to_reach_temperature(temp_10_percent)
emissivity_values = [emissivityFunction(T) for T in temperature]

# Intersection of non-constant emissivty graph and constant emissivity. Give 2 values since the first one is (0, 600)
idx = np.argwhere(np.diff(np.sign(original_temperature - temperature))).flatten()

# Results, the differences is hard to see if the plot is small so this part will be bigger

plt.figure(figsize=(25, 10))

# Time - Temperature
plt.subplot(1, 2, 1)
plt.plot(solution.t, solution.y[0], label = 'Non-constant emissivity')
plt.plot(original_time, original_temperature, label = 'Constant emissivity')
plt.plot(time[idx[1]], temperature[idx[1]], 'ro', label = 'Intersection')
plt.xlabel('Time (s)')
plt.ylabel('Temperature (K)')
plt.title('Impact of Non-constant Emissivity on Cooling')
plt.legend()
plt.grid(True)


# Emissivity - Temperature
plt.subplot(1, 2, 2)
plt.plot(emissivity_values, temperature, label = 'Emissivity - Temperature')
plt.xlabel('Emissivity')
plt.ylabel('Temperature (K)')
plt.title('Emissivity vs. Temperature')
plt.grid(True)
plt.gca().invert_xaxis()


print(f"Time to cool to 90% of initial temperature ({temp_90_percent:.1f} K): {time_90_percent:.1f} seconds")
print(f"Time to cool to 50% of temperature difference ({temp_50_percent:.1f} K): {time_50_percent:.1f} seconds")
print(f"Time to cool to 10% of temperature difference ({temp_10_percent:.1f} K): {time_10_percent:.1f} seconds")
print(f"Non-constant emissivity and the original object cool to the same temperature at {temperature[idx[1]]:.1f} K, after {time[idx[1]]:.1f} seconds.")

plt.show()