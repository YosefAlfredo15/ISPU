from flask import Flask, request, render_template
import requests
import logging
from geopy.geocoders import Nominatim
from tensorflow.keras.models import load_model

app = Flask(__name__)

# Set API key
WEATHERBIT_KEY = "be54fb81fcd348cd9043b6feca859baf"

# Path ke model LSTM untuk prediksi kualitas udara
MODEL_PATH = "Model/lstm_6_3_e50/ispu-prediction-model-kel4.h5"  # Sesuaikan dengan path Anda

# Daftar kota dengan koordinatnya
CITY_COORDINATES = {
    "jakarta": (-6.2088, 106.8456),
    "surabaya": (-7.2575, 112.7521),
    "semarang": (-6.9932, 110.4203),
    "serang": (-6.1104, 106.1639),
    "bengkulu": (-3.8006, 102.2561),
    "jambi": (-1.6108, 103.6131),
    "tanjungpinang": (0.9227, 104.4500),
    "pangkalpinang": (-2.1291, 106.1133),
    "banda aceh": (5.5466, 95.3191),
    "bandung": (-6.9175, 107.6191)
}

# Memuat model LSTM
try:
    lstm_model = load_model(MODEL_PATH)
    logging.info("Model LSTM berhasil dimuat")
except Exception as e:
    logging.error(f"Error saat memuat model LSTM: {e}")
    # Atur agar aplikasi tidak dapat dijalankan jika model tidak dapat dimuat
    raise SystemExit("Aplikasi tidak dapat dijalankan karena model tidak dapat dimuat")

logging.basicConfig(level=logging.DEBUG)

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        if 'city' in request.form:
            city = request.form["city"].lower()  # Menggunakan lower() untuk case insensitive
            if city in CITY_COORDINATES:
                latitude, longitude = CITY_COORDINATES[city]
                return get_air_quality(latitude=latitude, longitude=longitude, city=city)
            else:
                logging.warning(f"Kota '{city}' tidak ditemukan dalam daftar, default ke Surabaya")
                return get_air_quality(latitude=-7.2575, longitude=112.7521, city="Surabaya")
        elif 'latitude' in request.form and 'longitude' in request.form:
            latitude = request.form["latitude"]
            longitude = request.form["longitude"]
            return get_air_quality(latitude=latitude, longitude=longitude)
        elif 'current_location' in request.form and request.form['current_location'] == 'true':
            return get_current_location_air_quality()
    return render_template('index.html')

def get_air_quality(latitude=None, longitude=None, city=None):
    try:
        if latitude is None or longitude is None:
            raise ValueError("Latitude dan Longitude tidak boleh kosong")

        # Endpoint untuk mendapatkan kualitas udara saat ini
        url = f"https://api.weatherbit.io/v2.0/current/airquality?lat={latitude}&lon={longitude}&key={WEATHERBIT_KEY}"
 
        # Mengirimkan permintaan HTTP GET
        response = requests.get(url)
        
        # Memeriksa apakah permintaan berhasil (status code 200 adalah sukses)
        if response.status_code == 200:
            data = response.json()
            air_quality = data['data'][0]  # Asumsi API mengembalikan daftar dengan satu elemen
            # Render template dengan data air_quality
            return render_template('air_quality.html', air_quality=air_quality, city=city)
        else:
            logging.error(f"Gagal mendapatkan data kualitas udara: {response.status_code}")
            return render_template('air_quality.html', error="Gagal mendapatkan data kualitas udara")
    except Exception as e:
        logging.error(f"Error di endpoint get_air_quality: {e}")
        return render_template('air_quality.html', error=str(e))

def get_current_location_air_quality():
    try:
        # Implementasi untuk mendapatkan lokasi saat ini dari pengguna dan mengirimkannya
        # Misalnya, dapat menggunakan permintaan AJAX dari JavaScript di sisi klien untuk mengirim lokasi saat ini
        # dan menangani di sini
        # Contoh sederhana (perlu ditingkatkan dengan logika yang sesuai):
        latitude, longitude = -7.2575, 112.7521  # Contoh menggunakan Surabaya sebagai lokasi saat ini
        return get_air_quality(latitude=latitude, longitude=longitude, city="Surabaya")
    except Exception as e:
        logging.error(f"Error di endpoint get_current_location_air_quality: {e}")
        return render_template('air_quality.html', error=str(e))
    
@app.context_processor
def utility_processor():
    def get_quality_class(aqi):
        if aqi <= 50:
            return 'baik'
        elif aqi <= 100:
            return 'sedang'
        elif aqi <= 150:
            return 'tidak-sehat'
        else:
            return 'sangat-tidak-sehat'

    def get_quality_text(aqi):
        if aqi <= 50:
            return 'Baik'
        elif aqi <= 100:
            return 'Sedang'
        elif aqi <= 150:
            return 'Tidak Sehat'
        else:
            return 'Sangat Tidak Sehat'

    return dict(get_quality_class=get_quality_class, get_quality_text=get_quality_text)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
