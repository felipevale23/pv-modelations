from pvlib import location
from pvlib import irradiance
import pandas as pd
from matplotlib import pyplot as plt

# Dados do local
latitude = -10.701  # Latitude (São Paulo, por exemplo)
longitude = -37.249  # Longitude
tz = 'America/Bahia'

# Create location object to store lat, lon, timezone
site = location.Location(latitude, longitude, tz=tz)

# Calculate clear-sky GHI and transpose to plane of array
# Define a function so that we can re-use the sequence of operations with
# different locations
def get_irradiance(site_location, date, tilt, surface_azimuth):
    # Creates one day's worth of 10 min intervals
    times = pd.date_range(date, freq='10min', periods=6*24, tz=site_location.tz)
    # Generate clearsky data using the Ineichen model, which is the default
    # The get_clearsky method returns a dataframe with values for GHI, DNI,
    # and DHI
    clearsky = site_location.get_clearsky(times)
    # Get solar azimuth and zenith to pass to the transposition function
    solar_position = site_location.get_solarposition(times=times)
    # Use the get_total_irradiance function to transpose the GHI to POA
    POA_irradiance = irradiance.get_total_irradiance(
        surface_tilt=tilt,
        surface_azimuth=surface_azimuth,
        dni=clearsky['dni'],
        ghi=clearsky['ghi'],
        dhi=clearsky['dhi'],
        solar_zenith=solar_position['apparent_zenith'],
        solar_azimuth=solar_position['azimuth'])
    # Return DataFrame with only GHI and POA
    return pd.DataFrame({'GHI': clearsky['ghi'],
        'POA': POA_irradiance['poa_global']})


# Get irradiance data for summer and winter solstice, assuming 11 degree tilt
# and a north facing array
summer_irradiance = get_irradiance(site, '06-20-2024', 11, 0)
winter_irradiance = get_irradiance(site, '12-21-2024', 11, 0)

# Print the highest GHI and POA values for summer and winter
print("Verão:")
print(f"Irradiância Max. GHI: {summer_irradiance['GHI'].max()} W/m^2")
print(f"Irradiância Max. POA: {summer_irradiance['POA'].max()} W/m^2")

print("\nInverno:")
print(f"Irradiância Max. GHI: {winter_irradiance['GHI'].max()} W/m^2")
print(f"Irradiância Max. POA: {winter_irradiance['POA'].max()} W/m^2")

# Enhanced Plot: GHI vs. POA for Winter and Summer with Highlighted POA Peaks
fig, (ax1, ax2) = plt.subplots(1, 2, sharey=True, figsize=(14, 6))  # Adjust size for readability

# Summer plot
summer_irradiance['GHI'].plot(ax=ax1, label='Global Horizontal (GHI)', color='#1f77b4', linewidth=2)
summer_irradiance['POA'].plot(ax=ax1, label='Plano do Painel (POA)', color='#ff7f0e', linewidth=2)

# Highlight highest POA value for summer
summer_max_poa_idx = summer_irradiance['POA'].idxmax()
summer_max_poa = summer_irradiance.loc[summer_max_poa_idx, 'POA']
ax1.scatter(summer_max_poa_idx, summer_max_poa, color='black', label='Máximo POA', zorder=5)
ax1.annotate(f'{summer_max_poa:.1f} W/m²', (summer_max_poa_idx, summer_max_poa), 
             textcoords="offset points", xytext=(0, 10), ha='center', fontsize=10, color='black')

# Winter plot
winter_irradiance['GHI'].plot(ax=ax2, label='Global Horizontal (GHI)', color='#1f77b4', linewidth=2)
winter_irradiance['POA'].plot(ax=ax2, label='Plano do Painel (POA)', color='#ff7f0e', linewidth=2)

# Highlight highest POA value for winter
winter_max_poa_idx = winter_irradiance['POA'].idxmax()
winter_max_poa = winter_irradiance.loc[winter_max_poa_idx, 'POA']
ax2.scatter(winter_max_poa_idx, winter_max_poa, color='black', label='Máximo POA', zorder=5)
ax2.annotate(f'{winter_max_poa:.1f} W/m²', (winter_max_poa_idx, winter_max_poa), 
             textcoords="offset points", xytext=(0, -40), ha='center', fontsize=10, color='black')

# Titles and labels
ax1.set_title('Irradiância Durante o Solstício de Verão', fontsize=14, fontweight='bold')
ax2.set_title('Irradiância Durante o Solstício de Inverno', fontsize=14, fontweight='bold')
ax1.set_xlabel('Hora do Dia (Verão)', fontsize=12)
ax2.set_xlabel('Hora do Dia (Inverno)', fontsize=12)
ax1.set_ylabel('Irradiância ($W/m^2$)', fontsize=12)

# Customize legends
ax1.legend(fontsize=10, loc='upper right', frameon=True, shadow=True, fancybox=True)
ax2.legend(fontsize=10, loc='upper right', frameon=True, shadow=True, fancybox=True)

# Add gridlines
ax1.grid(True, linestyle='--', alpha=0.6)
ax2.grid(True, linestyle='--', alpha=0.6)

# Overall title
fig.suptitle('Comparação de Irradiância em Verão e Inverno', fontsize=16, fontweight='bold', y=1.02)

# Tweak layout and save
plt.tight_layout()
plt.savefig("Irradiance_Plot.png", dpi=300, bbox_inches='tight')  # Save with better margins