import streamlit as st
import pandas as pd

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="Data Korporat", page_icon="📊", layout="centered")

# 2. SESSION STATE (For Login)
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# 3. LOGIN SCREEN
def login_screen():
    st.title("📊 Sistem Data Korporat")
    st.write("Sila log masuk untuk mengakses dashboard.")
    
    email = st.text_input("Emel")
    password = st.text_input("Kata Laluan", type="password")
    
    if st.button("Log Masuk", type="primary", use_container_width=True):
        if "staff_passwords" in st.secrets:
            if email in st.secrets["staff_passwords"] and st.secrets["staff_passwords"][email] == password:
                st.session_state['logged_in'] = True
                st.session_state['current_user'] = email  # <--- ADD THIS LINE
                st.rerun()
            else:
                st.error("Emel atau Kata Laluan tidak sah. Sila cuba lagi.")
        else:
            st.error("Ralat sistem: Konfigurasi log masuk tidak dijumpai.")

# 4. MAIN APP ROUTING & LAYOUT
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
        st.write("**Ringkasan Maklumat Pelajar di bawah Sektor Pendidikan MARA (IPMa)**")
        
        st.subheader("Pendidikan Menengah")
        with st.expander("Bahagian Pendidikan Menengah"):
            st.info("Ruangan data sekolah menengah MARA.")
            
        st.subheader("Pendidikan Kemahiran")
        with st.expander("Bahagian Kemahiran dan Teknikal"):
            st.info("Ruangan data BKT.")
        with st.expander("UniKL & GMI"):
            st.info("Ruangan data pendaftaran & profil pelajar UniKL dan GMI.")
        with st.expander("GIATMARA"):
            st.info("Ruangan data pelatih GIATMARA.")
            
        st.subheader("Pendidikan Tinggi")
        with st.expander("KM/KPM/KPTM/UPTM"):
            st.info("Ruangan data KM/KPM/KPTM/UPTM.")
        with st.expander("Program Pendidikan Tinggi MARA"):
            st.info("Ruangan data Program Pendidikan Tinggi.")
            
        st.subheader("Penganjuran Pelajaran")
        with st.expander("Program Penganjuran Pelajaran MARA"):
            st.info("Ruangan data penajaan pelajar.")

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
