import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pvlib import irradiance
from pvlib.location import Location
from pvlib.solarposition import get_solarposition

# Definir localização
latitude = -10.701    # Latitude (Graus)
longitude = -37.249   # Longitude (Graus)
tz = 'America/Bahia'
elevation = 15        # metros

# Criar objeto de localização
site = Location(latitude, longitude, tz=tz, altitude=elevation)

# Simular sombreamento em intervalos aleatórios
def apply_random_shading(times, factor=0.5, num_intervals=5):
    shading_factor = np.ones(len(times))  # Sem sombra por padrão
    unique_days = times.normalize().unique()
    
    for day in unique_days:
        daily_mask = times.normalize() == day
        hours = np.random.choice(range(5, 19), num_intervals, replace=False)  # Escolher horários aleatórios entre 6h e 18h
        for hour in hours:
            hourly_mask = (times.hour == hour) & daily_mask
            shading_factor[hourly_mask] = factor  # Reduz a irradiância nesse horário
    
    return shading_factor

# Simulate all months
tilt = 11
surface_azimuth = 0
year = 2024

results = { "Month": [], "POA (kWh/m²)": [] }

# Criar uma grade de tempo para o ano inteiro
times = pd.date_range(start='2024-01-01', end='2024-12-31', freq='h', tz=tz)

# Obter a posição solar
solar_position = get_solarposition(times, latitude, longitude, elevation)

clearsky = site.get_clearsky(times)

# Aplica o fator de sombreamento específico.
shading_factor = apply_random_shading(times)
clearsky['ghi'] *= shading_factor

poa = irradiance.get_total_irradiance(
    surface_tilt=tilt,
    surface_azimuth=surface_azimuth,
    dni=clearsky['dni'],
    ghi=clearsky['ghi'],
    dhi=clearsky['dhi'],
    solar_zenith=solar_position['apparent_zenith'],
    solar_azimuth=solar_position['azimuth'])

# Aplicar o fator de sombreamento
poa['poa_direct'] *= shading_factor
poa['poa_global'] *= shading_factor

# Criar um DataFrame com os dados
irradiance_df = pd.DataFrame({
    'GHI': clearsky['ghi'],  # Irradiância global horizontal
    'POA': poa['poa_global']  # Irradiância no plano inclinado
})

# Calcular irradiação mensal (kWh/m²)
monthly_irradiation = irradiance_df.resample('ME').sum() / 1000

# Exibir resultados
print("Irradiação Mensal Total (kWh/m²):")
print(monthly_irradiation[['GHI', 'POA']])

# Criar coluna com o número de dias em cada mês
monthly_irradiation['Days'] = monthly_irradiation.index.days_in_month

# Calcular irradiação média diária (kWh/m²/dia)
monthly_irradiation_daily = monthly_irradiation[['GHI', 'POA']].div(monthly_irradiation['Days'], axis=0)

# Adicionar coluna de mês para plotagem
monthly_irradiation_daily['Month'] = range(1, 13)

print("\nIrradiação Média Diária (kWh/m²/dia):")
print(monthly_irradiation_daily)

# Print results
print("\nMedia Anual (kWh/m² * dia) (POA):", monthly_irradiation_daily["POA"].sum() / 12)
delta_poa_index = monthly_irradiation_daily["POA"].max() - monthly_irradiation_daily["POA"].min()
print("Variação Mensal Média (kWh/m² * dia):", delta_poa_index)
print("\n")
print("Máxima:", monthly_irradiation_daily["POA"].max())
print("Mínima (kWh/m² * dia):", monthly_irradiation_daily["POA"].min())
print("\n")

print("\nMedia Anual (kWh/m² * dia) (GHI):", monthly_irradiation_daily["GHI"].sum() / 12)
delta_poa_index = monthly_irradiation_daily["GHI"].max() - monthly_irradiation_daily["GHI"].min()
print("Variação Mensal Média (kWh/m² * dia) [GHI]:", delta_poa_index)
print("\n")
print("Máxima (GHI):", monthly_irradiation_daily["GHI"].max())
print("Mínima (GHI) :", monthly_irradiation_daily["GHI"].min())
print("\n")

fator_geracao = 31.81176

# Exibir resultados
print("Geração Mensal Total (kWh):")
print(monthly_irradiation[['POA']] * fator_geracao)
print("Geração Média no ano (kWh):", (monthly_irradiation[['POA']].sum() * fator_geracao) / 12)
print("\n")

# 🔥 **Plotando POA e GHI no mesmo gráfico**
fig, ax = plt.subplots(figsize=(10, 6))

# Plotar POA
ax.plot(monthly_irradiation_daily['Month'], monthly_irradiation_daily['POA'], color="#5f4bb6", marker='o', linewidth=2, label="POA (Plano Inclinado)")

# Plotar GHI
ax.plot(monthly_irradiation_daily['Month'], monthly_irradiation_daily['GHI'], color="#ff914d", marker='s', linewidth=2, linestyle="--", label="GHI (Horizontal)")

# Configurações do gráfico
plt.title("Irradiação Média Diária Mensal (kWh/m² * dia)", fontsize=16, fontweight='bold')
plt.ylabel("Irradiação (kWh/m² * dia)")
plt.xlabel("Mês")
plt.xticks(ticks=range(1, 13), labels=["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"], rotation=45)
plt.grid(axis="y", linestyle="--", alpha=0.7)
plt.legend()

# Ajustar proporção do gráfico
plt.gca().set_aspect(2.5, adjustable='datalim')

plt.tight_layout()
plt.savefig("Irradiacao_Mensal_Diaria.png", dpi=300)

# Plot results
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(monthly_irradiation_daily['Month'], monthly_irradiation_daily['POA'], color="#5f4bb6", marker='o', linewidth=2)

plt.title("Irradiação Direta na Superfície do Painel", fontsize=16, fontweight='bold')
plt.ylabel("Irradiação (kWh/m² * dia)")
plt.xlabel("Mês")
plt.xticks(ticks=range(1, 13), labels=["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"], rotation=45)
plt.grid(axis="y", linestyle="--", alpha=0.7)

# Ajustar proporção do gráfico
plt.gca().set_aspect(2.5, adjustable='datalim')

plt.tight_layout()
plt.savefig("Monthly_Irradiation_POA2.png", dpi=300)

# Calcular a irradiância máxima para cada mês
max_irradiance_per_month = irradiance_df.groupby(irradiance_df.index.month)['POA'].max()

for month, max_irr in max_irradiance_per_month.items():
    print(f'Mês {month}: Irradiância Máx. = {max_irr:.2f} W/m²')

# Calcular a média horária para cada mês
monthly_avg_irradiance = irradiance_df.groupby([irradiance_df.index.month, irradiance_df.index.hour]).mean()

# Criar um gráfico separado para cada mês
fig, axes = plt.subplots(nrows=4, ncols=3, figsize=(12, 10), sharex=True, sharey=True)
axes = axes.flatten()

# Nomes dos meses em português
month_names = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']

for month in range(1, 13):
    ax = axes[month - 1]
    ax.plot(range(24), monthly_avg_irradiance.loc[month]['POA'], color='orange')
    ax.set_title(month_names[month - 1])
    ax.grid(True)
    
fig.text(0, 0.5, 'Irradiância Média Mensal (W/m²)', va='center', rotation='vertical', fontsize=12, fontweight='bold')
fig.tight_layout()

plt.savefig("Daily_Irradiance.png", dpi=300)