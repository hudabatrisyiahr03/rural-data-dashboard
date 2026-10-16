import streamlit as st
import pandas as pd
import requests
from streamlit_gsheets import GSheetsConnection

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

    # --- SETUP GLOBAL SPREADSHEET CONNECTION ---
    # We put this here so EVERY page can use 'conn' and 'sheet_url'
    conn = st.connection("gsheets", type=GSheetsConnection)
    sheet_url = "https://docs.google.com/spreadsheets/d/15_qeN_tYUkPaV480_F7ENjTYFJ6vKeGcIDNKb8XEcGM/edit"


    if page == "Ringkasan Data Korporat":
        # 1. Fetch user's name for the personalized greeting
        current_email = st.session_state.get('current_user', '')
        df_profil = conn.read(spreadsheet=sheet_url, worksheet="Profil_Staf", ttl=0)
        user_row = df_profil[df_profil['Emel'] == current_email]
        
        # If the email is in the sheet, use their name. Otherwise, say "Pengguna" (User)
        nama_pengguna = user_row.iloc[0]['Nama'] if not user_row.empty else "Pengguna"
        
        # Display Welcome Message
        st.markdown(f"## 👋 Selamat Datang, {nama_pengguna}!")
        st.write("Berikut adalah ringkasan eksekutif bagi pangkalan data korporat MARA untuk tahun 2026.")
        st.divider()
        
        # 2. Fetch Master Metrics from our other tabs
        # Get Total Students from Pendidikan
        df_kpi = conn.read(spreadsheet=sheet_url, worksheet="KPI_Pendidikan", ttl=0)
        kpi_data = df_kpi.set_index("Metrik")["Nilai"].to_dict()
        jumlah_pelajar = int(kpi_data.get('Jumlah Keseluruhan Pelajar', 0))
        
        # Get Total Financing from Keusahawanan (automatically adds up the whole column!)
        df_pembiayaan = conn.read(spreadsheet=sheet_url, worksheet="Pembiayaan_Perniagaan", ttl=0)
        jumlah_pembiayaan = df_pembiayaan['Jumlah Pembiayaan (RM Juta)'].sum()
        
        # 3. Display Master Metric Cards
        st.subheader("📊 Sorotan Utama")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(label="🎓 Keseluruhan Pelajar (IPMa & Tajaan)", value=f"{jumlah_pelajar:,}")
        with col2:
            st.metric(label="💰 Jumlah Pembiayaan Perniagaan", value=f"RM {jumlah_pembiayaan:.1f} Juta")
        with col3:
            st.metric(label="🏢 Pusat Pentadbiran Aktif", value="115") # We can make this dynamic later!
            
        st.divider()
        
        # 4. Quick Info
        with st.expander("📌 Info Korporat MARA", expanded=True):
            st.info("Papan pemuka ini memantau metrik utama merentas semua sektor MARA secara masa nyata (real-time) melalui pangkalan data awan (cloud database).")

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
        
        # --- 2. HIGH-LEVEL KPIs ---
        st.subheader("Prestasi Keseluruhan (IPMa & Tajaan)")
        
        df_kpi = conn.read(spreadsheet=sheet_url, worksheet="KPI_Pendidikan", ttl=0)
        kpi_data = df_kpi.set_index("Metrik")["Nilai"].to_dict()

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(label="Enrolmen IPMa 2026", value=f"{int(kpi_data['Enrolmen IPMa 2026']):,}")
        with col2:
            st.metric(label="Kapasiti Fasiliti Akademik", value=f"{int(kpi_data['Kapasiti Fasiliti Akademik']):,}")
        with col3:
            st.metric(label="Pelajar Tajaan Semasa (BPP)", value=f"{int(kpi_data['Pelajar Tajaan Semasa (BPP)']):,}")
        with col4:
            st.metric(label="Jumlah Keseluruhan Pelajar", value=f"{int(kpi_data['Jumlah Keseluruhan Pelajar']):,}")
            
        st.divider()

        # --- 3. INTERACTIVE CHART ---
        st.subheader("Perbandingan Enrolmen 2026 vs Fasiliti Akademik")
        
        # CHANGED: usecols=[0, 1, 2, 3, 4] so it reads all 5 columns from the sheet
        df_institusi = conn.read(spreadsheet=sheet_url, worksheet="Pendidikan", usecols=[0, 1, 2, 3, 4], ttl=0)
        df_chart = df_institusi.set_index("Institusi")
        
        st.bar_chart(df_chart[["Enrolmen 2026", "Fasiliti Akademik"]], color=["#FF4B4B", "#1E88E5"])

        # --- 4. DETAILED TABS (UI UPGRADE) ---
        st.subheader("Pecahan Terperinci Mengikut Bahagian")
        
        df_bpm = df_institusi[df_institusi['Institusi'] == 'MRSM']
        df_tvet = df_institusi[df_institusi['Institusi'].isin(["GIATMARA", "TVETMARA", "GMI", "UniKL"])]
        df_bpt = df_institusi[df_institusi['Institusi'].isin(["Kolej MARA", "KPM", "KPTM", "UPTM"])]
        df_bpp = conn.read(spreadsheet=sheet_url, worksheet="Tajaan_BPP", ttl=0)

        # Create horizontal tabs instead of vertical expanders!
        tab1, tab2, tab3, tab4 = st.tabs([
            "🏫 Pendidikan Menengah (BPM)", 
            "⚙️ Kemahiran & Teknikal (TVET)", 
            "🎓 Pendidikan Tinggi (BPT)", 
            "🌍 Penganjuran Pelajaran (BPP)"
        ])

        with tab1:
            st.markdown("#### Maktab Rendah Sains MARA (MRSM)")
            if not df_bpm.empty:
                kap_mrsm = int(df_bpm.iloc[0]['Fasiliti Akademik'])
                enrol_mrsm = int(df_bpm.iloc[0]['Enrolmen 2026'])
                baharu_mrsm = int(df_bpm.iloc[0]['Pelajar Baharu'])
                tamat_mrsm = int(df_bpm.iloc[0]['Pelajar Tamat 2026'])
                
                # Use columns inside the tab for a cleaner layout
                col_a, col_b = st.columns(2)
                col_a.info(f"**Kapasiti Akademik:** {kap_mrsm:,}")
                col_a.success(f"**Enrolmen 2026:** {enrol_mrsm:,}")
                col_b.warning(f"**Pelajar Baharu:** {baharu_mrsm:,}")
                col_b.error(f"**Pelajar Tamat 2026:** {tamat_mrsm:,}")
            
        with tab2:
            st.markdown(f"**Jumlah Keseluruhan BKT:** Kapasiti {df_tvet['Fasiliti Akademik'].sum():,} | Enrolmen {df_tvet['Enrolmen 2026'].sum():,}")
            st.dataframe(df_tvet, hide_index=True, use_container_width=True)
            
        with tab3:
            st.markdown(f"**Jumlah Keseluruhan BPT:** Kapasiti {df_bpt['Fasiliti Akademik'].sum():,} | Enrolmen {df_bpt['Enrolmen 2026'].sum():,}")
            st.dataframe(df_bpt, hide_index=True, use_container_width=True)
            
        with tab4:
            st.markdown("**Pecahan Pelajar Tajaan Semasa**")
            st.dataframe(df_bpp, hide_index=True, use_container_width=True)
            
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
        
        # Pull the staff database directly from Google Sheets
        df_profil = conn.read(spreadsheet=sheet_url, worksheet="Profil_Staf", ttl=0)
        user_row = df_profil[df_profil['Emel'] == current_email]
        
        if not user_row.empty:
            nama = user_row.iloc[0]['Nama']
            jawatan = user_row.iloc[0]['Jawatan']
            jabatan = user_row.iloc[0]['Jabatan']
            
            st.success("Profil berjaya dimuat turun dari pangkalan data.")
            
            # Create a 2-column layout (1 part for picture, 3 parts for text)
            col1, col2 = st.columns([1, 3])
            
            with col1:
                # Automatically generate a profile picture based on the user's name
                avatar_url = f"https://ui-avatars.com/api/?name={nama.replace(' ', '+')}&size=200&background=1E88E5&color=fff&rounded=true"
                st.image(avatar_url, use_container_width=True)
                
            with col2:
                st.markdown(f"## {nama}")
                st.markdown(f"📧 **Emel:** `{current_email}`")
                st.markdown(f"💼 **Jawatan:** {jawatan}")
                st.markdown(f"🏢 **Jabatan:** {jabatan}")
                
            st.divider()
            
            with st.expander("Tetapan Lanjutan"):
                st.info("Di sini kita boleh tambah fungsi tukar kata laluan atau kemas kini gambar pada masa akan datang.")
        else:
            st.write(f"**Emel:** {current_email}")
            st.warning("Maklumat profil tambahan tidak dijumpai dalam pangkalan data.")
