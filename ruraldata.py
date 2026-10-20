import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from streamlit_gsheets import GSheetsConnection

# 1. FIREBASE CONFIGURATION
FIREBASE_API_KEY = st.secrets["FIREBASE_API_KEY"]

# 2. PAGE CONFIGURATION
st.set_page_config(page_title="Data Korporat", page_icon="📊", layout="centered")

# 3. SESSION STATE (For Login)
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# 4. LOGIN SCREEN & ROUTING
if not st.session_state['logged_in']:
    # --- HIDE SIDEBAR FOR LOGGED-OUT USERS ---
    st.markdown(
        """
        <style>
            [data-testid="collapsedControl"] {display: none;}
            [data-testid="stSidebar"] {display: none;}
        </style>
        """,
        unsafe_allow_html=True,
    )

    # --- CENTERED LOGIN CARD ---
    # Create 3 columns [Left Space, Center Card, Right Space]
    col1, col2, col3 = st.columns([1, 1.2, 1])
    
    with col2:
        st.write("") # Adds vertical breathing room
        st.write("")
        
        # Display the MARA logo centered above the login box
        st.image("mara_logo.png", width=150)
        
        st.markdown("<h2 style='text-align: center; color: #262730;'>Portal Data Korporat</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #666;'>Sila log masuk untuk mengakses papan pemuka</p>", unsafe_allow_html=True)
        
        # --- THE ACTUAL LOGIN FORM ---
        with st.form("login_form", clear_on_submit=False):
            email = st.text_input("Emel Pengguna", placeholder="cth: staf@mara.gov.my")
            password = st.text_input("Kata Laluan", type="password", placeholder="••••••••")
            
            submit_button = st.form_submit_button("Log Masuk", type="primary", use_container_width=True)
            
            if submit_button:
                if email and password:
                    # Talk directly to the Firebase Auth server
                    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
                    payload = {"email": email, "password": password, "returnSecureToken": True}
                    
                    response = requests.post(url, json=payload)
                    
                    if response.status_code == 200:
                        st.session_state['logged_in'] = True
                        st.session_state['current_user'] = email  
                        st.rerun()
                    else:
                        error_data = response.json()
                        firebase_error = error_data.get("error", {}).get("message", "Unknown Error")
                        st.error(f"Ralat Firebase: {firebase_error}")
                else:
                    st.warning("Sila masukkan emel dan kata laluan.")

        # --- LUPA KATA LALUAN ---
        with st.expander("Lupa Kata Laluan?"):
            reset_email = st.text_input("Masukkan emel anda:", key="reset_email")
            
            if st.button("Hantar Pautan Reset", use_container_width=True):
                if reset_email:
                    reset_url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={FIREBASE_API_KEY}"
                    payload = {"requestType": "PASSWORD_RESET", "email": reset_email}
                    
                    response = requests.post(reset_url, json=payload)
                    
                    if response.status_code == 200:
                        st.success(f"✅ Pautan telah dihantar ke `{reset_email}`. Sila semak peti masuk anda.")
                    else:
                        st.error("Ralat: Emel tidak dijumpai atau tidak sah.")
                else:
                    st.warning("Sila masukkan emel terlebih dahulu.")

# 5. MAIN APP (ONLY VISIBLE IF LOGGED IN)
else:
    # SIDEBAR NAVIGATION
    st.sidebar.image("mara_logo.png", width=150)
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
    st.header(page)

    # --- SETUP GLOBAL SPREADSHEET CONNECTION & CACHING ---
    sheet_url = "https://docs.google.com/spreadsheets/d/15_qeN_tYUkPaV480_F7ENjTYFJ6vKeGcIDNKb8XEcGM/edit"

    @st.cache_data(ttl=600) # Caches the data for 600 seconds (10 minutes)
    def load_data(worksheet_name, usecols=None):
        conn = st.connection("gsheets", type=GSheetsConnection)
        return conn.read(spreadsheet=sheet_url, worksheet=worksheet_name, usecols=usecols)
        
    if page == "Ringkasan Data Korporat":
        # 1. Fetch user's name for the personalized greeting
        current_email = st.session_state.get('current_user', '')
        df_profil = load_data("Profil_Staf")
        user_row = df_profil[df_profil['Emel'] == current_email]
        
        # If the email is in the sheet, use their name. Otherwise, say "Pengguna" (User)
        nama_pengguna = user_row.iloc[0]['Nama'] if not user_row.empty else "Pengguna"
        
        # Display Welcome Message
        st.markdown(f"## 👋 Selamat Datang, {nama_pengguna}!")
        st.write("Berikut adalah ringkasan eksekutif bagi pangkalan data korporat MARA untuk tahun 2026.")
        st.divider()
        
        # 2. Fetch Master Metrics from our other tabs
        # Get Total Students from Pendidikan
        df_kpi = load_data("KPI_Pendidikan")
        kpi_data = df_kpi.set_index("Metrik")["Nilai"].to_dict()
        jumlah_pelajar = int(kpi_data.get('Jumlah Keseluruhan Pelajar', 0))
        
        # Get Total Financing from Keusahawanan
        df_pembiayaan = load_data("Pembiayaan_Perniagaan")
        jumlah_pembiayaan = df_pembiayaan['Jumlah Pembiayaan (RM Juta)'].sum()
        
        # 3. Display Master Metric Cards
        st.subheader("📊 Sorotan Utama")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(label="🎓 Keseluruhan Pelajar (IPMa & Tajaan)", value=f"{jumlah_pelajar:,}")
        with col2:
            st.metric(label="💰 Jumlah Pembiayaan Perniagaan", value=f"RM {jumlah_pembiayaan:.1f} Juta")
        with col3:
            st.metric(label="🏢 Pusat Pentadbiran Aktif", value="115") 
            
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
        st.subheader("Data Sumber Manusia (HR)")
        
        # --- PLOTLY INTERACTIVE CHARTS START HERE ---
        st.markdown("**Analitik Profil Staf Semasa**")
        df_profil_hr = load_data("Profil_Staf") 
        
        senarai_jabatan = df_profil_hr['Jabatan'].dropna().unique().tolist()
        pilihan_jabatan = st.multiselect(
            "Tapis Data Mengikut Jabatan:", 
            options=senarai_jabatan, 
            default=senarai_jabatan
        )
        
        df_profil_filtered = df_profil_hr[df_profil_hr['Jabatan'].isin(pilihan_jabatan)]
        
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            df_jabatan = df_profil_filtered['Jabatan'].value_counts().reset_index()
            df_jabatan.columns = ['Jabatan', 'Bilangan Staf']
            
            fig_jabatan = px.pie(
                df_jabatan, 
                names='Jabatan', 
                values='Bilangan Staf', 
                hole=0.5, 
                title="Taburan Staf Mengikut Jabatan",
                color_discrete_sequence=px.colors.sequential.Teal
            )
            fig_jabatan.update_traces(textposition='inside', textinfo='percent+label')
            fig_jabatan.update_layout(showlegend=False, margin=dict(t=40, b=0, l=0, r=0))
            st.plotly_chart(fig_jabatan, use_container_width=True)
            
        with chart_col2:
            df_jawatan = df_profil_filtered['Jawatan'].value_counts().reset_index()
            df_jawatan.columns = ['Jawatan', 'Bilangan Staf']
            
            fig_jawatan = px.pie(
                df_jawatan, 
                names='Jawatan', 
                values='Bilangan Staf', 
                hole=0.5,
                title="Taburan Staf Mengikut Jawatan",
                color_discrete_sequence=px.colors.sequential.Burgyl
            )
            fig_jawatan.update_traces(textposition='inside', textinfo='percent+label')
            fig_jawatan.update_layout(showlegend=False, margin=dict(t=40, b=0, l=0, r=0))
            st.plotly_chart(fig_jawatan, use_container_width=True)
            
        st.divider()
        # --- PLOTLY INTERACTIVE CHARTS END HERE ---

        # Create tabs to separate MARA internal staff, Subsidiary staff, and Training
        tab_pusat, tab_syarikat, tab_latihan = st.tabs([
            "🏢 Pusat Pentadbiran MARA", 
            "💼 Anak Syarikat MARA",
            "🎓 Pembangunan Kerjaya"
        ])
        
        with tab_pusat:
            st.markdown("**Kedudukan Pengisian Jawatan MARA**")
            
            df_hr = load_data("Khidmat_Pengurusan")
            
            jumlah_peruntukan = df_hr['Peruntukan Jawatan'].sum()
            jumlah_pengisian = df_hr['Pengisian Semasa'].sum()
            kekosongan = jumlah_peruntukan - jumlah_pengisian
            kadar_pengisian = (jumlah_pengisian / jumlah_peruntukan) * 100
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("📋 Peruntukan", f"{jumlah_peruntukan:,}")
            col2.metric("👥 Pengisian", f"{jumlah_pengisian:,}")
            col3.metric("📉 Kekosongan", f"{kekosongan:,}")
            col4.metric("📈 Kadar", f"{kadar_pengisian:.1f}%")
            
            st.divider()
            
            col_chart, col_table = st.columns([1, 1])
            with col_chart:
                df_chart_hr = df_hr.set_index("Pusat")
                st.bar_chart(df_chart_hr[["Peruntukan Jawatan", "Pengisian Semasa"]], color=["#262730", "#E3000F"])
                
            with col_table:
                st.dataframe(df_hr, hide_index=True, use_container_width=True)
                csv_hr = df_hr.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Muat Turun Data (Pusat)", data=csv_hr, file_name="Data_Perjawatan_MARA.csv", mime="text/csv")
                
        with tab_syarikat:
            st.markdown("**Pengisian Jawatan Anak Syarikat MARA**")
            
            df_pelaburan = load_data("Pelaburan")
            
            col_a, col_b = st.columns(2)
            col_a.metric("🏢 Jumlah Anak Syarikat (Direkodkan)", f"{len(df_pelaburan)}")
            col_b.metric("👥 Keseluruhan Tenaga Kerja", f"{df_pelaburan['Jumlah'].sum():,}")
            
            st.divider()
            
            df_chart_pelaburan = df_pelaburan.set_index("Syarikat")
            st.bar_chart(df_chart_pelaburan["Jumlah"], color="#1E88E5")
            st.dataframe(df_pelaburan, hide_index=True, use_container_width=True)

        with tab_latihan:
            st.markdown("**Pemantauan Latihan & Pembangunan Modal Insan (2026)**")
            
            data_latihan = {
                "Program Latihan": ["Kepimpinan Eksekutif", "Keselamatan Siber (STRIDE)", "Analitik Data (Python/Tableau)", "Pengurusan Kewangan", "Komunikasi Korporat"],
                "Jumlah Peserta": [25, 150, 45, 80, 60],
                "Bajet Digunakan (RM)": [50000, 15000, 25000, 10000, 12000],
                "Status": ["Selesai", "Sedang Berjalan", "Selesai", "Akan Datang", "Sedang Berjalan"]
            }
            df_latihan = pd.DataFrame(data_latihan)
            
            col_l1, col_l2, col_l3 = st.columns(3)
            col_l1.metric("📚 Jumlah Program", len(df_latihan))
            col_l2.metric("👥 Keseluruhan Peserta", df_latihan['Jumlah Peserta'].sum())
            col_l3.metric("💰 Jumlah Perbelanjaan", f"RM {df_latihan['Bajet Digunakan (RM)'].sum():,}")
            
            st.divider()
            
            fig_latihan = px.bar(
                df_latihan, 
                x="Program Latihan", 
                y="Jumlah Peserta", 
                color="Status",
                title="Penyertaan Staf Mengikut Program Latihan",
                color_discrete_map={"Selesai": "#2E7D32", "Sedang Berjalan": "#1976D2", "Akan Datang": "#FFA000"}
            )
            st.plotly_chart(fig_latihan, use_container_width=True)
            
            st.dataframe(df_latihan, hide_index=True, use_container_width=True)
            
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
        
        df_kpi = load_data("KPI_Pendidikan")
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
        
        df_institusi = load_data("Pendidikan", usecols=[0, 1, 2, 3, 4])
        df_chart = df_institusi.set_index("Institusi")
        
        st.bar_chart(df_chart[["Enrolmen 2026", "Fasiliti Akademik"]], color=["#FF4B4B", "#1E88E5"])

        # --- 4. DETAILED TABS (UI UPGRADE) ---
        st.subheader("Pecahan Terperinci Mengikut Bahagian")
        
        df_bpm = df_institusi[df_institusi['Institusi'] == 'MRSM']
        df_tvet = df_institusi[df_institusi['Institusi'].isin(["GIATMARA", "TVETMARA", "GMI", "UniKL"])]
        df_bpt = df_institusi[df_institusi['Institusi'].isin(["Kolej MARA", "KPM", "KPTM", "UPTM"])]
        df_bpp = load_data("Tajaan_BPP")

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
            st.markdown("#### Institusi Kemahiran & Teknikal (TVET)")
            
            # 1. Create the interactive dropdown filter
            senarai_institusi = df_tvet['Institusi'].unique().tolist()
            pilihan_tvet = st.multiselect(
                "Tapis Institusi TVET:", 
                options=senarai_institusi, 
                default=senarai_institusi
            )
            
            # 2. Filter the dataframe based on user selection
            df_tvet_filtered = df_tvet[df_tvet['Institusi'].isin(pilihan_tvet)]
            
            # 3. Calculate dynamic totals that change when the filter changes
            kapasiti_total = df_tvet_filtered['Fasiliti Akademik'].sum()
            enrolmen_total = df_tvet_filtered['Enrolmen 2026'].sum()
            st.markdown(f"**Jumlah Semasa:** Kapasiti {kapasiti_total:,} | Enrolmen {enrolmen_total:,}")
            
            # 4. Display the filtered table
            st.dataframe(df_tvet_filtered, hide_index=True, use_container_width=True)
            
            # 5. Make the download button export ONLY the filtered data
            csv_tvet = df_tvet_filtered.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Muat Turun Data TVET (Ditapis)",
                data=csv_tvet,
                file_name="Data_TVET_MARA_Tapis_2026.csv",
                mime="text/csv"
            )
            
        with tab3:
            st.markdown(f"**Jumlah Keseluruhan BPT:** Kapasiti {df_bpt['Fasiliti Akademik'].sum():,} | Enrolmen {df_bpt['Enrolmen 2026'].sum():,}")
            st.dataframe(df_bpt, hide_index=True, use_container_width=True)
            
            # Convert and create button for BPT
            csv_bpt = df_bpt.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Muat Turun Data BPT",
                data=csv_bpt,
                file_name="Data_BPT_MARA_2026.csv",
                mime="text/csv"
            )
            
        with tab4:
            st.markdown("**Pecahan Pelajar Tajaan Semasa**")
            st.dataframe(df_bpp, hide_index=True, use_container_width=True)
            
    elif page == "Sektor Pelaburan":
        st.subheader("Data Pelaburan & Komersial MARA")
        
        with st.expander("Ringkasan Syarikat MARA", expanded=True):
            st.info("Ruangan profil dan metrik kewangan syarikat-syarikat MARA (Akan Datang).")
            
        with st.expander("Ringkasan Pelaburan MARA"):
            st.info("Ruangan prestasi pelaburan, ROI, dan aset korporat.")
            
        with st.expander("Struktur Kumpulan Syarikat MARA"):
            st.info("Ruangan carta organisasi dan pegangan ekuiti anak syarikat.")
            
        with st.expander("Aktiviti Kawalan Kredit"):
            st.info("Ruangan data pemantauan kredit dan bayaran balik.")

    elif page == "Ringkasan Keseluruhan":
        with st.expander("Ringkasan Keseluruhan Penerima Kemudahan MARA Kumulatif", expanded=True):
            st.info("Ruangan untuk jadual dan carta kumulatif keseluruhan.")

    elif page == "Profil Pengguna":
        st.subheader("Maklumat Akaun")
        
        # Retrieve the email saved during login
        current_email = st.session_state.get('current_user', 'Tiada Data')
        
        # Pull the staff database directly from Google Sheets
        df_profil = load_data("Profil_Staf")
        user_row = df_profil[df_profil['Emel'] == current_email]
        
        if not user_row.empty:
            nama = user_row.iloc[0]['Nama']
            jawatan = user_row.iloc[0]['Jawatan']
            jabatan = user_row.iloc[0]['Jabatan']
            
            st.success("Profil berjaya dimuat turun dari pangkalan data.")
            
            # Create a 2-column layout (1 part for picture, 3 parts for text)
            col1, col2 = st.columns([1, 3])
            
            with col1:
                # Check if the user has a custom image URL in the database
                url_gambar = user_row.iloc[0].get('URL_Gambar', '')
                
                # If no custom image exists, generate the default blue avatar
                if pd.isna(url_gambar) or url_gambar == '':
                    avatar_url = f"https://ui-avatars.com/api/?name={nama.replace(' ', '+')}&size=200&background=1E88E5&color=fff&rounded=true"
                else:
                    avatar_url = url_gambar
                    
                st.image(avatar_url, width=150)
                
            with col2:
                st.markdown(f"## {nama}")
                st.markdown(f"📧 **Emel:** `{current_email}`")
                st.markdown(f"💼 **Jawatan:** {jawatan}")
                st.markdown(f"🏢 **Jabatan:** {jabatan}")
                
            st.divider()
            
            with st.expander("⚙️ Tetapan Lanjutan (Tukar Kata Laluan)"):
                st.info("Klik butang di bawah untuk menerima pautan tukar kata laluan melalui emel rasmi anda.")
                
                if st.button("Hantar Emel Tukar Kata Laluan", type="primary"):
                    # Call Firebase's Password Reset API
                    reset_url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={FIREBASE_API_KEY}"
                    payload = {"requestType": "PASSWORD_RESET", "email": current_email}
                    
                    response = requests.post(reset_url, json=payload)
                    
                    if response.status_code == 200:
                        st.success(f"✅ Pautan pertukaran kata laluan telah dihantar ke `{current_email}`. Sila semak peti masuk (atau folder spam) anda.")
                    else:
                        error_msg = response.json().get("error", {}).get("message", "Ralat tidak diketahui")
                        st.error(f"Gagal menghantar emel: {error_msg}")
                        
            with st.expander("🖼️ Kemas Kini Gambar Profil"):
                st.info("Muat naik gambar profil baharu (JPG/PNG).")
                uploaded_file = st.file_uploader("Pilih Gambar", type=["jpg", "png", "jpeg"])
                
                if uploaded_file is not None:
                    if st.button("Simpan Gambar", type="primary"):
                        
                        # 1. Supabase Credentials
                        SUPABASE_URL = "https://yafabimzeoriwrightzu.supabase.co"
                        SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
                        
                        # 2. Create a clean file name using the user's email
                        file_ext = uploaded_file.name.split(".")[-1]
                        file_name = f"{current_email.replace('@', '_')}.{file_ext}"
                        
                        # 3. Setup the API request to Supabase Storage
                        upload_url = f"{SUPABASE_URL}/storage/v1/object/avatars/{file_name}"
                        headers = {
                            "apikey": SUPABASE_KEY,
                            "Authorization": f"Bearer {SUPABASE_KEY}",
                            "Content-Type": uploaded_file.type,
                            "x-upsert": "true" 
                        }
                        
                        # 4. Upload the file
                        response = requests.post(upload_url, headers=headers, data=uploaded_file.getvalue())
                        
                        if response.status_code == 200:
                            # 5. Generate the public link
                            public_url = f"{SUPABASE_URL}/storage/v1/object/public/avatars/{file_name}"
                            
                            # 6. Save link to Google Sheets
                            conn = st.connection("gsheets", type=GSheetsConnection)
                            
                            # Paksa kolum menjadi teks (string)
                            df_profil['URL_Gambar'] = df_profil['URL_Gambar'].astype(str) 
                            df_profil.loc[df_profil['Emel'] == current_email, 'URL_Gambar'] = public_url
                            
                            # Masukkan URL penuh Google Sheets "Dashboard Data MARA" anda
                            sheet_url = "https://docs.google.com/spreadsheets/d/15_qeN_tYUkPaV480_F7ENjTYFJ6vKeGcIDNKb8XEcGM/edit?usp=sharing"
                            
                            conn.update(spreadsheet=sheet_url, worksheet="Profil_Staf", data=df_profil)
                            
                            st.cache_data.clear()
                            st.success("✅ Gambar profil berjaya dikemas kini! Sila muat semula (refresh) halaman.")
                        else:
                            st.error(f"Gagal memuat naik: {response.text}")
