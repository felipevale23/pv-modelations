import pandas as pd
from pvlib import location
from pvlib.bifacial.pvfactors import pvfactors_timeseries
import matplotlib.pyplot as plt
import warnings

# supressing shapely warnings that occur on import of pvfactors
warnings.filterwarnings(action='ignore', module='pvfactors')

# Dados do local
latitude = -10.701  # Latitude (São Paulo, por exemplo)
longitude = -37.249  # Longitude
elevation = 100  # Elevation in meters above sea level (adjust as needed)
tz = 'America/Bahia'

times = pd.date_range('2021-06-21', '2021-06-22', freq='1min', tz=tz)

# Including elevation in the location
loc = location.Location(latitude=latitude, longitude=longitude, tz=times.tz, altitude=elevation)

sp = loc.get_solarposition(times)
cs = loc.get_clearsky(times, model='ineichen')

print(cs)

print(sp[['apparent_zenith', 'azimuth']])

# Example array geometry 
pvrow_height = 2
pvrow_width = 4
pitch = 10
gcr = pvrow_width / pitch
axis_azimuth = 270  # Tracking east-west
albedo = 0.45  # Ground reflectivity

# Adjusted for north-facing array in Northeast Brazil
irrad = pvfactors_timeseries(
    solar_azimuth=sp['azimuth'],
    solar_zenith=sp['apparent_zenith'],
    surface_azimuth=0,  # north-facing array
    surface_tilt=11,  # Tilt angle, adjust as needed for location
    axis_azimuth=270,  # 90 degrees off from surface_azimuth. 270 is correct for tracking
    timestamps=times,
    dni=cs['dni'],
    dhi=cs['dhi'],
    gcr=gcr,
    pvrow_height=pvrow_height,
    pvrow_width=pvrow_width,
    albedo=albedo,
    n_pvrows=3,
    index_observed_pvrow=1
)

# turn into pandas DataFrame
irrad = pd.concat(irrad, axis=1)

# Exibindo resultados
print(irrad)  # Potência máxima gerada em cada hora

print(irrad[['total_inc_back', 'total_abs_back']].describe())

irrad[['total_inc_back', 'total_abs_back']].plot()

plt.ylabel('Irradiance [W m$^{-2}$]')

plt.savefig("Irradiance.png", dpi=300)  # Saves as PNG with 300 DPI