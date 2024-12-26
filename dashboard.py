import streamlit as st # type: ignore
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)


# Fungsi untuk memuat dataset
def load_data(dataset):
    try:
        return pd.read_csv(dataset)
    except FileNotFoundError:
        st.error(f"File {dataset} tidak ditemukan. Pastikan file berada di jalur yang benar.")
        return None

# Konfigurasi halaman Streamlit
st.set_page_config(page_title="Bike Sharing Dashboard", layout="wide")

# Dataset paths
hour_dataset = "Bike-sharing-dataset/hour.csv"
day_dataset = "Bike-sharing-dataset/day.csv"

# Load datasets
data_hour = load_data(hour_dataset)
data_day = load_data(day_dataset)

if data_hour is not None and data_day is not None:
    # Tambahkan kolom informasi untuk penggabungan
    data_hour['Dataset'] = 'Hour'
    data_day['Dataset'] = 'Day'

    # Gabungkan kedua dataset
    data = pd.concat([data_hour, data_day], ignore_index=True)

    # Pilihan rentang waktu
    st.sidebar.write("## Filter Rentang Waktu")
    if 'dteday' in data.columns:
        data['dteday'] = pd.to_datetime(data['dteday'])
        start_date = st.sidebar.date_input("Tanggal Mulai", value=data['dteday'].min().date())
        end_date = st.sidebar.date_input("Tanggal Selesai", value=data['dteday'].max().date())

        if start_date > end_date:
            st.sidebar.error("Tanggal Mulai harus lebih kecil atau sama dengan Tanggal Selesai")
        else:
            data = data[(data['dteday'] >= pd.Timestamp(start_date)) & (data['dteday'] <= pd.Timestamp(end_date))]

    # Mapping angka bulan ke musim
    def season(mnth):
        if mnth in [12, 1, 2]:
            return 'Winter'
        elif mnth in [3, 4, 5]:
            return 'Spring'
        elif mnth in [6, 7, 8]:
            return 'Summer'
        else:
            return 'Fall'

    data['season'] = data['mnth'].apply(season)

    # Menampilkan total sepeda per jam dan per hari
    total_per_hour = data.groupby('hr')['cnt'].sum()
    total_per_day = data.groupby('dteday')['cnt'].sum()

    st.write("# Ringkasan Penggunaan Sepeda")
    st.metric(label="Total Penggunaan Sepeda (Rentang Waktu)", value=data['cnt'].sum())

# Visualisasi penggunaan sepeda berdasarkan musim dan jam
st.write("## Pola Penggunaan Sepeda Berdasarkan Musim dan Jam")
plt.figure(figsize=(12, 6))
sns.barplot(x='hr', y='cnt', hue='season', data=data, errorbar=None)
plt.title('Penggunaan Sepeda Berdasarkan Jam dan Musim')
plt.xlabel('Jam')
plt.ylabel('Total Sepeda')
st.pyplot(plt)

# Visualisasi pola penggunaan sepeda berdasarkan hari dan musim
weekday_mapping = {
    0: 'Senin',
    1: 'Selasa',
    2: 'Rabu',
    3: 'Kamis',
    4: 'Jumat',
    5: 'Sabtu',
    6: 'Minggu'
}
data['weekday_name'] = data['weekday'].map(weekday_mapping)

st.write("## Pola Penggunaan Sepeda Berdasarkan Hari dan Musim")
plt.figure(figsize=(12, 6))
sns.barplot(x='weekday_name', y='cnt', hue='season', data=data, errorbar=None)
plt.title('Penggunaan Sepeda Berdasarkan Hari dan Musim')
plt.xlabel('Hari')
plt.ylabel('Total Sepeda')
st.pyplot(plt)

# Visualisasi rata-rata penggunaan sepeda berdasarkan musim
avg_bike_usage_per_season = data.groupby('season', as_index=False)['cnt'].mean()
st.write("## Rata-rata Penggunaan Sepeda per Musim")
plt.figure(figsize=(10, 6))
sns.barplot(x='season', y='cnt', data=avg_bike_usage_per_season, palette="coolwarm", errorbar=None, legend=False)
plt.title('Rata-rata Penggunaan Sepeda per Musim')
plt.xlabel('Musim')
plt.ylabel('Rata-rata Penggunaan Sepeda')
st.pyplot(plt)

# Menampilkan rata-rata penggunaan per musim dan musim dengan penggunaan terbanyak
st.write("### Rata-rata Penggunaan per Musim")
for index, row in avg_bike_usage_per_season.iterrows():
    st.write(f"- {row['season']}: {row['cnt']:.2f} sepeda rata-rata")

max_season = avg_bike_usage_per_season.loc[avg_bike_usage_per_season['cnt'].idxmax()]
st.write(f"### Musim dengan Penggunaan Terbanyak: {max_season['season']} ({max_season['cnt']:.2f} sepeda rata-rata)")

# Visualisasi penggunaan sepeda berdasarkan cuaca dan jam
weather_mapping = {
    1: 'Cerah = Clear, Few Clouds, Partly Cloudy',
    2: 'Berkabut = Mist, Cloudy, Broken Clouds',
    3: 'Ringan = Light Snow/Rain, Scattered Clouds',
    4: 'Ekstrem = Heavy Rain, Ice Pallets, Thunderstorm, Mist, Snow, Fog'
}
data['weather_label'] = data['weathersit'].map(weather_mapping)

st.write("## Penggunaan Sepeda Berdasarkan Cuaca dan Jam")
plt.figure(figsize=(12, 6))
sns.barplot(x='hr', y='cnt', hue='weather_label', data=data, errorbar=None)
plt.title('Penggunaan Sepeda Berdasarkan Cuaca dan Jam')
plt.xlabel('Jam')
plt.ylabel('Total Sepeda')
st.pyplot(plt)

# Visualisasi tren mingguan penggunaan sepeda berdasarkan cuaca
st.write("## Tren Penggunaan Sepeda Berdasarkan Cuaca")
avg_bike_usage_per_weather = data.groupby('weather_label', as_index=False)['cnt'].mean()
plt.figure(figsize=(10, 6))
sns.barplot(x='weather_label', y='cnt', data=avg_bike_usage_per_weather, palette='viridis', dodge=True, errorbar=None)
plt.title('Penggunaan Sepeda Berdasarkan Cuaca')
plt.xlabel('Cuaca')
plt.ylabel('Rata-rata Penggunaan Sepeda')
st.pyplot(plt)

# Menampilkan rata-rata penggunaan berdasarkan cuaca dan cuaca dengan penggunaan terbanyak
st.write("### Rata-rata Penggunaan per Cuaca")
for index, row in avg_bike_usage_per_weather.iterrows():
    st.write(f"- {row['weather_label']}: {row['cnt']:.2f} sepeda rata-rata")

max_weather = avg_bike_usage_per_weather.loc[avg_bike_usage_per_weather['cnt'].idxmax()]
st.write(f"### Cuaca dengan Penggunaan Terbanyak: {max_weather['weather_label']} ({max_weather['cnt']:.2f} sepeda rata-rata)")

# Footer
st.sidebar.markdown("---")
st.sidebar.write("Dibuat oleh: Ganis Dwiarum Prabandari (ganisdwiarumprabandari@gmail.com)")
