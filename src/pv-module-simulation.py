import matplotlib.pyplot as plt
import pvlib
import pandas as pd
import numpy as np

# Dados do local
latitude = -10.701  # Latitude (São Paulo, por exemplo)
longitude = -37.249  # Longitude
tz = 'America/Bahia'

# Criar um local
site = pvlib.location.Location(latitude, longitude, tz=tz)

# Calcular a faixa de tempo para 1 dia, com intervalo de 5 minutos
times = pd.date_range('2025-01-24', periods=24, freq='h', tz=tz)

# Calcular o ângulo solar e a irradiância
solar_position = site.get_solarposition(times)

# Simular irradiância baseada no ângulo solar (simplificação)
irradiance = 888 * np.cos(np.radians(solar_position['apparent_zenith']))  # Irradiância em W/m²

temperature = pd.Series([25] * len(times), index=times)  # Temperatura em °C (valor fixo para simplificação)

# Parâmetros do módulo fotovoltaico
module_parameters = {
    'Name': 'Bluesun_455Wp',
    'BIPV': 'N',
    'Date': '1/1/2020',
    'T_NOCT': 45,  # Temperatura de operação no ambiente (NOCT)
    'Pmax': 455,  # Potência máxima em Watts
    'Vmp': 35.0,  # Tensão em MPPT (valor estimado)
    'Vmpo': 35.0,  # Tensão em MPPT (valor estimado)
    'Imp': 13.0,  # Corrente em MPPT (valor estimado)
    'Voc': 44.5,  # Tensão de circuito aberto
    'Voco': 44.5,  # Tensão de circuito aberto em STC
    'Isc': 14.2,  # Corrente de curto-circuito
    'Alpha_sc': 0.0038,  # Coeficiente térmico de corrente (estimado)
    'Beta_oc': -0.120,  # Coeficiente térmico de tensão (estimado)
    'Gamma_r': -0.35,  # Coeficiente de potência (estimado)
    'Bvmpo': -0.1,  # Dependência térmica da tensão no ponto de máxima potência
    'Mbvmp': -0.005,  # Ajuste para a tensão em função da irradiância
    'Bvoco': -0.2,  # Dependência térmica da tensão de circuito aberto
    'Mbvoc': -0.01,  # Ajuste para Voc em função da irradiância
    'N': 1,  # Número de diodos de junção ideal
    'Cells_in_Series': 72,  # Número de células conectadas em série
    'Isco': 14.2,  # Corrente de curto-circuito de referência
    'Aisc': 0.0038,  # Coeficiente de ajuste térmico para Isc
    'Impo': 13.0,  # Corrente de máxima potência
    'Aimp': 0.0038,  # Coeficiente de ajuste térmico para Imp
    # Coeficientes de ajuste SAPM
    'C0': 1.0,  # Coeficiente para cálculo da corrente
    'C1': 0.0,  # Coeficiente quadrático para corrente
    'C2': 0.0,  # Coeficiente cúbico para corrente
    'C3': 0.0,  # Coeficiente quartico para corrente
    'C4': 1.0,  # Coeficiente para ajuste da tensão
    'C5': 0.0,  # Coeficiente quadrático para ajuste de tensão
    'C6': 0.0,  # Coeficiente quadrático para ajuste de tensão
    'C7': 0.0,  # Coeficiente quadrático para ajuste de tensão
    'IXO': 0.5,  # Corrente de operação em função da irradiância (valor padrão)
    'IXXO': 0.5,  # Corrente de operação em função da irradiância (valor padrão)
}

# Modelo para a célula solar
temperature_model_parameters = pvlib.temperature.TEMPERATURE_MODEL_PARAMETERS['sapm']['open_rack_glass_glass']

# Calculando a temperatura da célula
cell_temperature = pvlib.temperature.sapm_cell(
    poa_global=irradiance,
    temp_air=temperature,
    wind_speed=1.0,
    **temperature_model_parameters
)

# Calculando a potência gerada
effective_irradiance = irradiance  # Assumindo nenhuma perda adicional
output = pvlib.pvsystem.sapm(
    effective_irradiance,
    cell_temperature,
    module_parameters
)

# Exibindo resultados
print(output[['p_mp']])  # Potência máxima gerada em cada hora

# Calculate the energy produced by the module (in watt-hours)
energy_produced = output['p_mp'].sum()  # Sum of power over time

# Convert energy from watt-hours to kilowatt-hours
energy_produced_kWh = energy_produced / 1000

print(f"Total energy produced: {energy_produced_kWh:.2f} kWh")

# Plotting the power output
plt.figure(figsize=(10, 6))
plt.plot(output.index, output['p_mp'], label='Maximum Power Output (W)', color='b', marker='o')

# Adding labels and title
plt.title('Máxima Potência do Módulo Fotovoltáico', fontsize=14)
plt.xlabel('Tempo', fontsize=12)
plt.ylabel('Potência (W)', fontsize=12)

# Rotating x-axis labels for better visibility
plt.xticks(rotation=45)

# Adding a grid
plt.grid(True)

# Displaying the legend
plt.legend()

# Showing the plot
plt.tight_layout()
plt.savefig("outputpowersimulation.png", dpi=300)  # Saves as PNG with 300 DPI