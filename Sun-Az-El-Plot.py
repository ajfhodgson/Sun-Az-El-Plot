# Output a csv file containing azimuths at which the sun rises above and falls below 
# a series of elevations, for every day of the year.

import pvlib
import pandas as pd

# Define the location
latitude = 52.0
longitude = 0.0
tz = 'Europe/London'
tz = 'UTC' # avoid discontinuities as DST starts/stops

# Function to find the first time the sun's elevation crosses 10 degrees
def get_azimuth_at_elev(elev_degs, date, latitude, longitude, tz):
    times = pd.date_range(start=date, end=date + pd.Timedelta(days=1), freq='T', tz=tz)
    solpos = pvlib.solarposition.get_solarposition(times, latitude, longitude)
    elev_above_elev_degs = solpos[solpos['apparent_elevation'] >= elev_degs]
    if not elev_above_elev_degs.empty:
        first_time = elev_above_elev_degs.index[0]
        last_time = elev_above_elev_degs.index[-1]
        first_azimuth = solpos.loc[first_time, 'azimuth']
        last_azimuth =  solpos.loc[last_time, 'azimuth']
        return first_time, first_azimuth, last_time, last_azimuth
    else:
        return None, None, None, None

# Iterate over each day of the year and calculate the azimuth at 10 degrees elevation
dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D', tz=tz)

with open("Sun-Az-El-Plot.csv", "w") as outfile:
    outfile.write(f"Date,Elev,AM/PM,Azim\n")

    for date in dates:
        line = f"{str(date)[0:10]}, "
        for elev_degs in [0, 10, 20, 30, 40, 50, 60, 70, 80] :
            first_time, first_azimuth, last_time, last_azimuth = get_azimuth_at_elev(elev_degs, date, latitude, longitude, tz)
            if first_time and first_azimuth and last_time and last_azimuth:
                outfile.write(f"{str(date)[0:10]},{first_time.strftime('%H:%M')},{elev_degs:4.0f},AM,{first_azimuth:03.0f}\n")
                outfile.write(f"{str(date)[0:10]},{last_time.strftime('%H:%M')},{elev_degs:4.0f},PM,{last_azimuth:03.0f}\n")
                line += f"{elev_degs:4.0f}, {str(first_time)[11:16]}, {first_azimuth:03.0f}, {str(last_time)[11:16]}, {last_azimuth:03.0f},"
        print (line)
print ("Fine.")


