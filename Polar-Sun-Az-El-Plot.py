# Use plot lib to draw a radial plot of solar azimuth and elevation
# for all days of the year, at [10] minute intervals 
# Draw a dot for each time/date on a polar chart, reflecting the azimuth (azim 0 = North at x=0, y=1)
# and elevation (elev -90 at r=0, elev 0 at r=0.5, elev 90  at r=1.0)
# There should be a thick black circle drawn at elev = 0
# The colour of each dot should be detemined by the month: 
# Jan red, Feb orange, Mar yellow, Apr green, May blue, June purple
# Jul purple, Aug blue, Sep green, Oct yellow, Nov Orange, Dec Red
# Omit the dots on the hour, to leave gaps in the lines of dot marking the hours

import matplotlib.pyplot as plt
import pvlib
import pandas as pd
import numpy as np

# Define the location
latitude = 52.0
longitude = 0.0
tz = 'Europe/London'
tz = 'UTC'  # avoid discontinuities as DST starts/stops

# Initialize lists to store all data
all_azimuths = []
all_elevations = []
all_months = []
all_times = []

# Iterate over each day of the year and calculate the az/el at 15 minute intervals
dates = pd.date_range(start='2025-01-01', end='2025-12-31', freq='D', tz=tz)

for date in dates:
    times = pd.date_range(start=date, end=date + pd.Timedelta(days=1), freq='15min', tz=tz)
    solpos = pvlib.solarposition.get_solarposition(times, latitude, longitude)
    
    # Store the data
    azimuths = solpos['azimuth'].values
    elevs = solpos['apparent_elevation'].values
    months = [date.month] * len(times)
    
    all_azimuths.extend(azimuths)
    all_elevations.extend(elevs)
    all_months.extend(months)
    all_times.extend(times)

# Convert to numpy arrays for easier manipulation
all_azimuths = np.array(all_azimuths)
all_elevations = np.array(all_elevations)
all_months = np.array(all_months)
all_times = pd.to_datetime(all_times)

# Create a DataFrame for CSV export
df_export = pd.DataFrame({
    'Date': all_times.date,
    'Time': all_times.time,
    'Azimuth': all_azimuths,
    'Elevation': all_elevations
})
df_export.to_csv("Polar-Sun-Az-El-Plot-Data.csv", index=False)

# Create masks for hourly and non-hourly points
hour_mask = all_times.minute == 0  # Points on the hour
non_hour_mask = all_times.minute != 0  # Points not on the hour

# Separate the data
hourly_azimuths = all_azimuths[hour_mask]
hourly_elevations = all_elevations[hour_mask]
hourly_months = all_months[hour_mask]
hourly_times = all_times[hour_mask]

filtered_azimuths = all_azimuths[non_hour_mask]
filtered_elevations = all_elevations[non_hour_mask]
filtered_months = all_months[non_hour_mask]

# Define colors for each month
month_colors = {
    1: 'red',      # Jan
    2: 'orange',   # Feb
    3: 'yellow',   # Mar
    4: 'green',    # Apr
    5: 'blue',     # May
    6: 'purple',   # Jun
    7: 'red',      # Jul
    8: 'orange',   # Aug
    9: 'yellow',   # Sep
    10: 'green',   # Oct
    11: 'blue',    # Nov
    12: 'purple'   # Dec
}

# Create the polar plot
fig, ax = plt.subplots(figsize=(12, 12), subplot_kw=dict(projection='polar'))

# Convert azimuth to radians for matplotlib polar plot  
# set_theta_zero_location('S') puts South at top
azimuth_rad = np.radians(filtered_azimuths)
hourly_azimuth_rad = np.radians(hourly_azimuths)

# Define scaling parameters for radial distance
min_elev = np.floor(np.min(all_elevations) / 10) * 10  # Round down to nearest 10°
min_radius = 0    # Corresponding minimum radius
max_elev = np.ceil(np.max(all_elevations) / 10) * 10   # Round up to nearest 10°
max_radius = 1.0  # Corresponding maximum radius

# Convert elevation to radial distance using linear scaling
radial_distance = min_radius + (filtered_elevations - min_elev) * (max_radius - min_radius) / (max_elev - min_elev)
hourly_radial_distance = min_radius + (hourly_elevations - min_elev) * (max_radius - min_radius) / (max_elev - min_elev)

# Plot non-hourly points for each month with appropriate colors
for month in range(1, 13):
    month_mask = filtered_months == month
    if np.any(month_mask):
        # Split into above and below horizon
        above_horizon = (filtered_elevations >= 0) & month_mask
        below_horizon = (filtered_elevations < 0) & month_mask
        
        # Plot above horizon points in month colors
        if np.any(above_horizon):
            ax.scatter(azimuth_rad[above_horizon], radial_distance[above_horizon], 
                      c=month_colors[month], s=1.0, alpha=0.7, label=f'Month {month}')
        
        # Plot below horizon points in grey
        if np.any(below_horizon):
            ax.scatter(azimuth_rad[below_horizon], radial_distance[below_horizon], 
                      c='grey', s=1.0, alpha=0.3)

# Plot hourly points (larger dots)
for month in range(1, 13):
    month_mask = hourly_months == month
    if np.any(month_mask):
        # Split into above and below horizon
        above_horizon = (hourly_elevations >= 0) & month_mask
        below_horizon = (hourly_elevations < 0) & month_mask
        
        # Plot above horizon hourly points in month colors (larger)
        if np.any(above_horizon):
            ax.scatter(hourly_azimuth_rad[above_horizon], hourly_radial_distance[above_horizon], 
                      c=month_colors[month], s=7.0, alpha=0.9)
        
        # Plot below horizon hourly points in grey (larger)
        if np.any(below_horizon):
            ax.scatter(hourly_azimuth_rad[below_horizon], hourly_radial_distance[below_horizon], 
                      c='grey', s=5.0, alpha=0.5)

# Draw thick black circle at elevation 0 (r=0.5)
theta_circle = np.linspace(0, 2*np.pi, 100)
r_circle = np.full_like(theta_circle, 0.5)
ax.plot(theta_circle, r_circle, 'k-', linewidth=3, label='Horizon (elev=0°)')

# Customize the plot
ax.set_theta_zero_location('S')  # Set South/180°/pi radians at 12 O'Clock (top of plot)
ax.set_theta_direction(-1)       # Clockwise direction
ax.set_thetagrids(range(0, 360, 15))  # Azimuth gridlines every 15 degrees
ax.set_ylim(0, 1)
ax.set_title('Solar Az/Els Throughout the Year', 
             pad=20, fontsize=14)

# Add radial labels for elevation
elevation_ticks = np.linspace(min_elev, max_elev, 5)  # 5 evenly spaced ticks
radius_ticks = np.linspace(min_radius, max_radius, 5)
ax.set_yticks(radius_ticks)
ax.set_yticklabels([f'{elev:.0f}°' for elev in elevation_ticks])

# Add hour labels just outside the highest elevation for each hour
# Find the maximum elevation for each hour across all days
hourly_max_elevations = {} # 0..23 array
hourly_label_az_els = {}

for hour in range(24):
    hour_mask = hourly_times.hour == hour # mask selecting all points in the year for this hour
    if np.any(hour_mask):
        this_hour_elevations = hourly_elevations[hour_mask]
        if len(this_hour_elevations) > 0:
            max_elev_idx = np.argmax(this_hour_elevations)
            this_hour_max_elev = this_hour_elevations[max_elev_idx]
            if this_hour_max_elev > 0:  # Only label hours when sun is above horizon
                hourly_max_elevations[hour] = this_hour_max_elev
                # Get the corresponding azimuth for the max elevation
                hour_azimuths = hourly_azimuths[hour_mask]
                this_hour_max_elev_azimuth = hour_azimuths[max_elev_idx]
                hourly_label_az_els[hour] = (this_hour_max_elev_azimuth, this_hour_max_elev)

# Add text labels for each hour at maximum elevation position
for hour, (this_hour_max_elev_azimuth, this_hour_max_elev) in hourly_label_az_els.items():
    # Convert to plot coordinates
    theta = np.radians(this_hour_max_elev_azimuth)
    r = min_radius + (this_hour_max_elev - min_elev) * (max_radius - min_radius) / (max_elev - min_elev)
    
    # Place label slightly outside the maximum elevation point
    label_r = r + 0.05  # Much smaller offset
    ax.text(theta, label_r, str(hour), fontsize=8, ha='center', va='center',
            bbox=dict(boxstyle='circle,pad=0.2', facecolor='white', alpha=0.8, edgecolor='black'))

# Add legend
# ax.legend(bbox_to_anchor=(1.1, 1), loc='upper left')

plt.tight_layout()
plt.show()
plt.savefig('solar_position_radial_plot.png', dpi=600)

print("Solar position radial plot created successfully!")