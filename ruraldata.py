import streamlit as st
import pandas as pd
import requests

# 1. FIREBASE CONFIGURATION (Only the API Key is needed for login!)
FIREBASE_API_KEY = "AIzaSyA5zBYaiDGBkqRKxcTk4-tXHEqnJ8B8cFU"

# 2. PAGE CONFIGURATION
st.set_page_config(page_title="Data Korporat", page_icon="📊", layout="centered")

# 3. SESSION STATE (For Login)
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# 4. LOGIN SCREEN
def login_screen():
    st.title("📊 Sistem Data Korporat")
    st.write("Sila log masuk untuk mengakses dashboard.")
    
    email = st.text_input("Emel")
    password = st.text_input("Kata Laluan", type="password")
    
    if st.button("Log Masuk", type="primary", use_container_width=True):
        if email and password:
            # Talk directly to the Firebase Auth server
            url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
            payload = {"email": email, "password": password, "returnSecureToken": True}
            
            response = requests.post(url, json=payload)
            
            # 200 means the server confirmed the login is correct
            if response.status_code == 200:
                st.session_state['logged_in'] = True
                st.session_state['current_user'] = email  
                st.rerun()
            else:
                # DEBUG: Show the exact error from Firebase
                error_data = response.json()
                firebase_error = error_data.get("error", {}).get("message", "Unknown Error")
                st.error(f"Ralat Firebase: {firebase_error}")
        else:
            st.warning("Sila masukkan emel dan kata laluan.")

# 5. MAIN APP ROUTING & LAYOUT
if not st.session_state['logged_in']:
    login_screen()
else:
    # SIDEBAR NAVIGATION
    st.sidebar.title("Navigasi Menu")
    
    menu_options = [
        "Ringkasan Data Korporat",
        "Lampiran Pelaporan Data Korporat",
        "Sektor Khidmat Pengurusan",
        "Sektor Keusahawanan",
        "Sektor Pendidikan",
        "Sektor Pelaburan",
        "Ringkasan Keseluruhan",
        "Profil Pengguna"
    ]
    
    page = st.sidebar.radio("Pilih Sektor:", menu_options)
    
    st.sidebar.divider()
    if st.sidebar.button("Log Keluar"):
        st.session_state['logged_in'] = False
        st.rerun()

    # PAGE CONTENT ROUTING
    st.title(page)

    if page == "Ringkasan Data Korporat":
        with st.expander("Info Korporat MARA", expanded=True):
            st.info("Ruangan untuk visualisasi Info Korporat MARA.")
        with st.expander("Dashboard Data Korporat"):
            st.info("Ruangan untuk metrik utama Dashboard.")

    elif page == "Lampiran Pelaporan Data Korporat":
        with st.expander("Ringkasan Eksekutif Data Korporat", expanded=True):
            st.write("Khidmat Pengurusan, Usahawan, Pendidikan & Pelaburan")
            st.info("Ruangan untuk Ringkasan Eksekutif.")
        with st.expander("Petunjuk Prestasi Utama (KPI)"):
            st.info("Ruangan untuk graf dan jadual KPI.")

    elif page == "Sektor Khidmat Pengurusan":
        with st.expander("Pusat - Pusat Pentadbiran MARA", expanded=True):
            st.info("Ruangan untuk senarai dan data Pusat Pentadbiran.")
        with st.expander("Kedudukan Pengisian Jawatan"):
            st.info("Ruangan untuk statistik perjawatan.")
        with st.expander("Program Pembangunan Kerjaya"):
            st.info("Ruangan untuk data program kerjaya.")

    elif page == "Sektor Keusahawanan":
        with st.expander("Ringkasan Penerima Kemudahan Keusahawanan, Pembiayaan dan Penyewa MARA", expanded=True):
            st.info("Ruangan untuk statistik keseluruhan penerima kemudahan.")
            
        with st.expander("Program Pembangunan Usahawan"):
            st.info("Ruangan data Pembangunan Usahawan.")
            
        with st.expander("Program Infrastruktur Komersial"):
            st.info("Ruangan data Infrastruktur Komersial.")
            
        with st.expander("Pembiayaan Perniagaan", expanded=True):
            st.subheader("Trend Pembiayaan Perniagaan (2026)")
            
            # 1. Generate Mock Data
            mock_data = {
                "Bulan": ["Jan", "Feb", "Mac", "Apr", "Mei", "Jun"],
                "Jumlah Pembiayaan (RM Juta)": [12.5, 14.2, 11.8, 15.0, 16.5, 18.2],
                "Syarikat Diluluskan": [45, 52, 40, 60, 65, 72]
            }
            df = pd.DataFrame(mock_data)
            df.set_index("Bulan", inplace=True)
            
            # 2. Display Interactive Bar Chart
            st.bar_chart(df["Jumlah Pembiayaan (RM Juta)"], color="#FF4B4B")
            
            # 3. Display the Raw Data Table
            st.write("**Jadual Data Terperinci**")
            st.dataframe(df, use_container_width=True)

    elif page == "Sektor Pendidikan":
        st.write("**Ringkasan Maklumat Pelajar di bawah Sektor Pendidikan MARA (IPMa) - Setakat 31 Julai 2026**")
        
        # 1. High-Level KPIs
        st.subheader("Prestasi Keseluruhan (IPMa & Tajaan)")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(label="Enrolmen IPMa 2026", value="165,828")
        with col2:
            st.metric(label="Kapasiti Fasiliti Akademik", value="159,870")
        with col3:
            st.metric(label="Pelajar Tajaan Semasa (BPP)", value="76,067")
        with col4:
            st.metric(label="Jumlah Keseluruhan Pelajar", value="241,895")
            
        st.divider()

        # 2. Main Data Table for the Interactive Chart
        data_institusi = {
            "Institusi": ["MRSM", "GIATMARA", "TVETMARA", "GMI", "UniKL", "Kolej MARA", "KPM", "KPTM", "UPTM"],
            "Enrolmen 2026": [34544, 15217, 17854, 2779, 34935, 1559, 5718, 25360, 8689],
            "Fasiliti Akademik": [39750, 10699, 21258, 5000, 25000, 3755, 6606, 22900, 5800]
        }
        df_institusi = pd.DataFrame(data_institusi)
        
        # 3. Interactive Chart
        st.subheader("Perbandingan Enrolmen 2026 vs Fasiliti Akademik")
        df_chart = df_institusi.set_index("Institusi")
        st.bar_chart(df_chart[["Enrolmen 2026", "Fasiliti Akademik"]], color=["#FF4B4B", "#1E88E5"])

        # 4. Detailed Expanders
        st.subheader("Pecahan Terperinci Mengikut Bahagian")
        
        with st.expander("Pendidikan Menengah (BPM)"):
            st.write("**Maktab Rendah Sains MARA (MRSM)**")
            st.write("- Kapasiti Akademik: 39,750 | Enrolmen 2026: 34,544")
            st.write("- Pelajar Baharu: 9,843 | Pelajar Tamat 2026: 0")
            
        with st.expander("Kemahiran dan Teknikal (TVET)"):
            st.write("**Jumlah Keseluruhan BKT:** Kapasiti Akademik 81,059 | Enrolmen 89,958")
            st.table(pd.DataFrame({
                "Pusat": ["GIATMARA", "TVETMARA", "GMI", "UniKL"],
                "Kapasiti Akademik": [10699, 21258, 5000, 25000],
                "Enrolmen 2026": [15217, 17854, 2779, 34935]
            }))
            
        with st.expander("Pendidikan Tinggi (BPT)"):
            st.write("**Jumlah Keseluruhan BPT:** Kapasiti Akademik 39,061 | Enrolmen 41,326")
            st.table(pd.DataFrame({
                "Pusat": ["Kolej MARA (KM)", "Kolej Profesional MARA (KPM)", "Kolej Poly-Tech MARA (KPTM)", "UPTM"],
                "Kapasiti Akademik": [3755, 6606, 22900, 5800],
                "Enrolmen 2026": [1559, 5718, 25360, 8689]
            }))
            
        with st.expander("Penganjuran Pelajaran (BPP)"):
            st.write("**Pecahan Pelajar Tajaan Semasa**")
            st.table(pd.DataFrame({
                "Kategori": ["IPMa", "Dalam Negara (Bukan IPMa)", "Luar Negara"],
                "Tajaan Baharu": [7497, 237, 640],
                "Pelajar Semasa": [48263, 24259, 3545]
            }))
    elif page == "Sektor Pelaburan":
        with st.expander("Ringkasan Syarikat MARA", expanded=True):
            st.info("Ruangan profil syarikat-syarikat MARA.")
        with st.expander("Ringkasan Pelaburan MARA"):
            st.info("Ruangan metrik pelaburan.")
        with st.expander("Struktur Kumpulan Syarikat MARA"):
            st.info("Ruangan carta organisasi/struktur syarikat.")
        with st.expander("Aktiviti Kawalan Kredit"):
            st.info("Ruangan data kawalan kredit.")

    elif page == "Ringkasan Keseluruhan":
        with st.expander("Ringkasan Keseluruhan Penerima Kemudahan MARA Kumulatif", expanded=True):
            st.info("Ruangan untuk jadual dan carta kumulatif keseluruhan.")

    elif page == "Profil Pengguna":
        st.subheader("Maklumat Akaun")
        
        # Retrieve the email saved during login
        current_email = st.session_state.get('current_user', 'Tiada Data')
        
        # Mock database linking emails to profile information
        user_profiles = {
            "pengarah@mara.gov.my": {"nama": "Pengarah MARA", "jawatan": "Pengarah Eksekutif", "jabatan": "Pengurusan Tertinggi"},
            "pegawai@mara.gov.my": {"nama": "Pegawai Data", "jawatan": "Pegawai Analisis", "jabatan": "Sektor Keusahawanan"},
            "huda@ruraldata.com": {"nama": "Nur Huda Batrisyia", "jawatan": "Pembangun Sistem / Admin", "jabatan": "Jabatan IT"}
        }
        
        # Display the profile card
        if current_email in user_profiles:
            profile = user_profiles[current_email]
            st.success("Profil berjaya dimuat turun.")
            st.write(f"**Nama:** {profile['nama']}")
            st.write(f"**Emel:** {current_email}")
            st.write(f"**Jawatan:** {profile['jawatan']}")
            st.write(f"**Jabatan:** {profile['jabatan']}")
        else:
            st.write(f"**Emel:** {current_email}")
            st.write("Maklumat profil tambahan tidak dijumpai.")
