import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from pvlib import location, irradiance

# Define the site location
latitude = -10.701  # Replace with your location's latitude
longitude = -37.249  # Replace with your location's longitude
tz = 'America/Bahia'
site = location.Location(latitude, longitude, tz=tz)

def calculate_daily_irradiation(site, date, tilt, surface_azimuth):
    # Convert date string to datetime object
    date = pd.Timestamp(date)
    times = pd.date_range(start=date, end=(date + pd.Timedelta(days=1)), freq='h', tz=site.tz)
    
    # Generate clear-sky data and calculate solar position
    clearsky = site.get_clearsky(times)
    solar_position = site.get_solarposition(times)
    
    # Calculate plane of array (POA) irradiance
    poa_irradiance = irradiance.get_total_irradiance(
        surface_tilt=tilt,
        surface_azimuth=surface_azimuth,
        dni=clearsky['dni'],
        ghi=clearsky['ghi'],
        dhi=clearsky['dhi'],
        solar_zenith=solar_position['apparent_zenith'],
        solar_azimuth=solar_position['azimuth']
    )

    # Simulate dynamic shading (e.g., simulate cloud coverage throughout the day)
    shading_factor = 1 - (0.25 * np.sin(np.linspace(0, 2 * np.pi, len(times))))  # Dynamic shading factor
    poa_irradiance['poa_direct'] *= shading_factor
    clearsky['ghi'] *= shading_factor

    # Integrate GHI and POA over the day (sum up 10-minute intervals)
    daily_ghi = clearsky['ghi'].sum()  
    daily_poa = poa_irradiance['poa_direct'].sum()   
    
    return daily_ghi, daily_poa

def calculate_monthly_irradiation(year, month, tilt, surface_azimuth):
    start_date = pd.Timestamp(f"{year}-{month:02d}-01")
    end_date = start_date + pd.offsets.MonthEnd(0)
    days_in_month = end_date.day
    
    ghi_values = []
    poa_values = []
    
    for day in range(1, days_in_month + 1):
        date = f"{year}-{month:02d}-{day:02d}"
        daily_ghi, daily_poa = calculate_daily_irradiation(site, date, tilt, surface_azimuth)
        ghi_values.append(daily_ghi)
        poa_values.append(daily_poa)
    
    # Average over the month
    monthly_avg_ghi = sum(ghi_values) / days_in_month
    monthly_avg_poa = sum(poa_values) / days_in_month
    
    return monthly_avg_ghi / 1000, monthly_avg_poa / 1000

# Simulate all months
tilt = 11
surface_azimuth = 0
year = 2024

results = {"Month": [], "GHI (kWh/m²)": [], "POA (kWh/m²)": []}
for month in range(1, 13):
    monthly_ghi, monthly_poa = calculate_monthly_irradiation(year, month, tilt, surface_azimuth)
    results["Month"].append(month)
    results["GHI (kWh/m²)"].append(monthly_ghi)
    results["POA (kWh/m²)"].append(monthly_poa)

results_df = pd.DataFrame(results)

# Print results
print("Irradiação Mensal (kWh/m²):")
print(results_df)

# Plot results
results_df.plot(kind="bar", x="Month", y=["GHI (kWh/m²)", "POA (kWh/m²)"], figsize=(10, 6), color=["#1f77b4", "#ff7f0e"])
plt.title("Irradiação Mensal para GHI e POA", fontsize=16, fontweight='bold')
plt.ylabel("Irradiação (kWh/m² * dia)")
plt.xlabel("Mês")
plt.xticks(ticks=range(12), labels=["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"],rotation=45)
plt.grid(axis="y", linestyle="--", alpha=0.7)
plt.tight_layout()
plt.savefig("Monthly_Irradiation.png", dpi=300)

results = {"Month": [], "POA (kWh/m²)": []}
for month in range(1, 13):
    monthly_ghi, monthly_poa = calculate_monthly_irradiation(year, month, tilt, surface_azimuth)
    results["Month"].append(month)
    results["POA (kWh/m²)"].append(monthly_poa)

results_df = pd.DataFrame(results)

# Print results
print("\nMedia Anual (kWh/m²):", results_df["POA (kWh/m²)"].sum() / 12)
delta_poa_index = results_df["POA (kWh/m²)"].max() - results_df["POA (kWh/m²)"].min()
print("Variação Mensal Média (kWh/m²):", delta_poa_index)

# Plot results
results_df.plot(kind="line", x="Month", y="POA (kWh/m²)", figsize=(10, 6), color="#5f4bb6", marker='o', legend=False)
plt.title("Irradiação Direta na Superfície do Painel", fontsize=16, fontweight='bold')
plt.ylabel("Irradiação (kWh/m² * dia)")
plt.xlabel("Mês")
plt.xticks(ticks=range(12), labels=["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"], rotation=45)
plt.grid(axis="y", linestyle="--", alpha=0.7)

# Set aspect ratio to make it more square-like
plt.gca().set_aspect(2.5, adjustable='datalim')

plt.tight_layout()
plt.savefig("Monthly_Irradiation_POA.png", dpi=300)