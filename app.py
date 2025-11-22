import streamlit as st
import google.generativeai as genai
from PIL import Image
import json
import os
import re

# --- KONFIGURACJA STRONY ---
st.set_page_config(
    page_title="AutoWise",
    page_icon="🔧",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- STYLIZACJA CSS (ABY WYGLĄDAŁO JAK NA ZDJĘCIU) ---
st.markdown("""
<style>
    /* Ciemne tło i niebieskie akcenty */
    .stApp {
        background-color: #0E1117;
        color: #E0E0E0;
    }
    h1, h2, h3 {
        color: #3B82F6 !important; /* Niebieski AutoWise */
    }
    /* Stylizacja przycisków Radio (kafelki) */
    div[role="radiogroup"] > label {
        background-color: #1E293B;
        border: 1px solid #334155;
        padding: 10px;
        border-radius: 8px;
        margin-bottom: 5px;
    }
    div[role="radiogroup"] > label:hover {
        border-color: #3B82F6;
        color: #3B82F6;
    }
    /* Przycisk główny */
    button[kind="primary"] {
        background-color: #2563EB;
        border: none;
        transition: 0.3s;
    }
    button[kind="primary"]:hover {
        background-color: #1D4ED8;
    }
    /* Wyniki w ramkach */
    div[data-testid="stExpander"] {
        background-color: #161B22;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- POBRANIE KLUCZA API ---
try:
    # Próba pobrania z secrets (Streamlit Cloud) lub zmiennych środowiskowych
    api_key = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        st.error("⚠️ Brak klucza API! Ustaw GOOGLE_API_KEY w 'Advanced settings' na Streamlit.")
        st.stop()
    genai.configure(api_key=api_key)
except Exception as e:
    st.error(f"Błąd konfiguracji API: {e}")
    st.stop()

# --- SŁOWNIK TŁUMACZEŃ (Z TWOJEGO KODU) ---
TRANSLATIONS = {
    "pl": {
        "title": "AutoWise",
        "subtitle_diag": "Zaawansowana Diagnostyka Pojazdowa",
        "subtitle_tune": "Inżynieria Motorsportu & Tuning",
        "tab_diag": "Diagnostyka",
        "tab_tune": "Tuning",
        "vehicle": "Pojazd",
        "engine": "Silnik",
        "desc_label_diag": "Opis Usterki",
        "desc_label_tune": "Cele / Budżet",
        "placeholder_diag": "Opisz problem. Staraj się jak najdokładniej opisać usterkę i wszystko co jej towarzyszy (dźwięki, wibracje).",
        "placeholder_tune": "Np. Silnik 2.0 TDI, celuję w 200KM+. Budżet 5000 zł.",
        "analyze_btn_diag": "Rozpocznij Diagnozę",
        "analyze_btn_tune": "Generuj Plan Tuningu",
        "upload_label": "Dodaj zdjęcie (opcjonalnie)",
        "analyzing": "Analiza techniczna...",
        "refine_label": "Doprecyzuj / Dodaj szczegóły",
        "refine_btn": "Aktualizuj",
        "result_severity": "Powaga",
        "result_safety": "Bezpieczeństwo",
        "result_causes": "Potencjalne Przyczyny",
        "result_tip": "Porada Eksperta",
        "tune_power": "Przyrost Mocy",
        "tune_cost": "Szacowany Koszt",
        "tune_rel": "Wpływ na Trwałość",
        "tune_parts": "Rekomendowane Części",
        "tune_pros": "Zalety",
        "tune_cons": "Wady i Ryzyka",
        "vehicles": {"Car": "Samochód", "Motorcycle": "Motocykl", "Truck": "Ciężarówka", "Other": "Inny"},
        "engines": {"Petrol": "Benzyna", "Diesel": "Diesel", "LPG": "LPG", "Hybrid": "Hybryda", "Electric": "Elektryczny"},
        "off_topic": "Pytanie nie jest związane z motoryzacją. Proszę zapytać ponownie."
    },
    "en": {
        "title": "AutoWise",
        "subtitle_diag": "Advanced Vehicle Diagnostics",
        "subtitle_tune": "Motorsport Engineering & Tuning",
        "tab_diag": "Diagnostics",
        "tab_tune": "Tuning",
        "vehicle": "Vehicle",
        "engine": "Engine",
        "desc_label_diag": "Fault Description",
        "desc_label_tune": "Goals / Budget",
        "placeholder_diag": "Describe the problem accurately (sounds, vibrations, context).",
        "placeholder_tune": "E.g. 2.0 TDI engine, aiming for 200HP+. Budget $1500.",
        "analyze_btn_diag": "Start Diagnosis",
        "analyze_btn_tune": "Generate Tuning Plan",
        "upload_label": "Add photo (optional)",
        "analyzing": "Technical Analysis...",
        "refine_label": "Refine / Add Details",
        "refine_btn": "Update",
        "result_severity": "Severity",
        "result_safety": "Safety",
        "result_causes": "Potential Causes",
        "result_tip": "Expert Tip",
        "tune_power": "Power Gain",
        "tune_cost": "Est. Cost",
        "tune_rel": "Durability Impact",
        "tune_parts": "Recommended Parts",
        "tune_pros": "Pros",
        "tune_cons": "Cons",
        "vehicles": {"Car": "Car", "Motorcycle": "Motorcycle", "Truck": "Truck", "Other": "Other"},
        "engines": {"Petrol": "Petrol", "Diesel": "Diesel", "LPG": "LPG", "Hybrid": "Hybrid", "Electric": "Electric"},
        "off_topic": "The question is not related to automotive topics. Please ask again."
    },
    "de": {
        "title": "AutoWise",
        "subtitle_diag": "Erweiterte Fahrzeugdiagnose",
        "subtitle_tune": "Motorsporttechnik & Tuning",
        "tab_diag": "Diagnose",
        "tab_tune": "Tuning",
        "vehicle": "Fahrzeug",
        "engine": "Motor",
        "desc_label_diag": "Fehlerbeschreibung",
        "desc_label_tune": "Ziele / Budget",
        "placeholder_diag": "Beschreiben Sie das Problem so genau wie möglich.",
        "placeholder_tune": "Z.B. 2.0 TDI Motor, Ziel 200PS+. Budget 1500€.",
        "analyze_btn_diag": "Diagnose starten",
        "analyze_btn_tune": "Tuning-Plan erstellen",
        "upload_label": "Foto hinzufügen (optional)",
        "analyzing": "Technische Analyse...",
        "refine_label": "Präzisieren / Details hinzufügen",
        "refine_btn": "Aktualisieren",
        "result_severity": "Schweregrad",
        "result_safety": "Sicherheit",
        "result_causes": "Mögliche Ursachen",
        "result_tip": "Experten-Tipp",
        "tune_power": "Leistungssteigerung",
        "tune_cost": "Geschätzte Kosten",
        "tune_rel": "Einfluss auf Haltbarkeit",
        "tune_parts": "Empfohlene Teile",
        "tune_pros": "Vorteile",
        "tune_cons": "Nachteile",
        "vehicles": {"Car": "Auto", "Motorcycle": "Motorrad", "Truck": "LKW", "Other": "Andere"},
        "engines": {"Petrol": "Benzin", "Diesel": "Diesel", "LPG": "LPG", "Hybrid": "Hybrid", "Electric": "Elektrisch"},
        "off_topic": "Die Frage bezieht sich nicht auf Kraftfahrzeuge. Bitte fragen Sie erneut."
    }
}

# --- FUNKCJE POMOCNICZE ---

def clean_json_text(text):
    """Czyści tekst z markdowna (```json ... ```) przed parsowaniem"""
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```', '', text)
    return text.strip()

def get_gemini_model():
    return genai.GenerativeModel('gemini-1.5-flash')

def analyze_request(mode, vehicle, engine, desc, lang, image=None, context_history=""):
    model = get_gemini_model()
    lang_name = {"pl": "POLISH", "en": "ENGLISH", "de": "GERMAN"}[lang]
    t = TRANSLATIONS[lang]

    base_instruction = f"""
    You are a WORLD-CLASS AUTOMOTIVE ENGINEER named AutoWise.
    Output Language: {lang_name}.
    IMPORTANT: Return ONLY valid JSON code. No markdown formatting.
    
    CRITICAL RULE: If the user asks about NON-AUTOMOTIVE topics (cooking, weather, politics), 
    return this JSON: {{"summary": "{t['off_topic']}"}} and nothing else.
    """

    if mode == "Diagnosis":
        system_instruction = base_instruction + f"""
        Focus on mechanical diagnosis for a {vehicle} with {engine} engine.
        Return JSON structure:
        {{
            "summary": "Short technical summary",
            "severity": "Low/Medium/High/Critical (translated)",
            "safetyWarning": "Safety advice",
            "potentialCauses": [
                {{
                    "name": "Part name",
                    "description": "Short technical description",
                    "solution": "How to fix",
                    "likelihood": 80,
                    "estimatedCost": "Cost estimate in local currency",
                    "difficulty": "Easy/Medium/Hard (translated)"
                }}
            ],
            "maintenanceTip": "One pro tip"
        }}
        """
    else: # Tuning
        system_instruction = base_instruction + f"""
        Focus on tuning/modification for a {vehicle} with {engine} engine.
        Return JSON structure:
        {{
            "summary": "Tuning plan summary",
            "expectedPowerIncrease": "e.g. +30HP",
            "drivingCharacteristics": "Handling changes",
            "estimatedTotalCost": "Total cost",
            "reliabilityImpact": "Impact description",
            "partsRecommendation": [
                {{
                    "name": "Part Name",
                    "type": "Type",
                    "description": "Why this part",
                    "estimatedPrice": "Price",
                    "powerGain": "Gain"
                }}
            ],
            "pros": ["Pro 1", "Pro 2"],
            "cons": ["Con 1", "Con 2"]
        }}
        """

    prompt = f"""
    Context/History: {context_history}
    Vehicle: {vehicle}
    Engine: {engine}
    User Input: {desc}
    """

    content = [prompt]
    if image:
        content.append(image)

    try:
        response = model.generate_content(
            contents=content,
            generation_config=genai.GenerationConfig(
                temperature=0.4,
            ),
            # Przekazujemy instrukcję systemową tutaj w nowszej wersji SDK, 
            # ale dla bezpieczeństwa kompatybilności można ją wpleść w prompt jeśli configure() to obsługuje.
            # Tutaj używamy podejścia bezpośredniego w prompt jeśli model to 'gemini-1.5-flash'
        )
        
        # Hack: Czasem instrukcja systemowa lepiej działa jako pierwszy content w liście wiadomości
        # Ale tutaj użyjemy prostego promptu z instrukcją.
        full_response = model.generate_content(
            [system_instruction, prompt, image] if image else [system_instruction, prompt]
        )
        
        cleaned_text = clean_json_text(full_response.text)
        return json.loads(cleaned_text)
        
    except Exception as e:
        st.error(f"Błąd AI: {e}")
        return None

# --- INTERFEJS UŻYTKOWNIKA ---

# Sidebar settings
with st.sidebar:
    st.header("Ustawienia / Settings")
    lang_code = st.selectbox("Język / Language", ["pl", "en", "de"], format_func=lambda x: x.upper())

t = TRANSLATIONS[lang_code]

# Header
col1, col2 = st.columns([1, 5])
with col1:
    st.markdown("# 🔧")
with col2:
    st.title("AutoWise")
    
    # Customowe wyświetlanie trybów jako Radio (będzie wyglądać jak kafelki dzięki CSS)
    mode_selection = st.radio("Tryb / Mode", ["Diagnosis", "Tuning"], horizontal=True, 
                    format_func=lambda x: t["tab_diag"] if x == "Diagnosis" else t["tab_tune"],
                    label_visibility="collapsed")

st.markdown(f"### *{t['subtitle_diag'] if mode_selection == 'Diagnosis' else t['subtitle_tune']}*")
st.divider()

# Formularz
col_v, col_e = st.columns(2)
with col_v:
    st.markdown(f"**{t['vehicle']}**")
    vehicle_type = st.selectbox("Wybierz pojazd", list(t["vehicles"].keys()), format_func=lambda x: t["vehicles"][x], label_visibility="collapsed")
with col_e:
    st.markdown(f"**{t['engine']}**")
    engine_type = st.selectbox("Wybierz silnik", list(t["engines"].keys()), format_func=lambda x: t["engines"][x], label_visibility="collapsed")

st.markdown(f"**{t['desc_label_diag'] if mode_selection == 'Diagnosis' else t['desc_label_tune']}**")
description = st.text_area(
    "Opis",
    placeholder=t["placeholder_diag"] if mode_selection == "Diagnosis" else t["placeholder_tune"],
    height=120,
    label_visibility="collapsed"
)

uploaded_file = st.file_uploader(t["upload_label"], type=["jpg", "jpeg", "png", "webp"])
image_data = None
if uploaded_file:
    image_data = Image.open(uploaded_file)
    st.image(image_data, caption="Podgląd / Preview", width=200)

# Stan aplikacji
if "result" not in st.session_state:
    st.session_state.result = None
if "history" not in st.session_state:
    st.session_state.history = ""

# Przycisk Główny
analyze_btn_text = t["analyze_btn_diag"] if mode_selection == "Diagnosis" else t["analyze_btn_tune"]
if st.button(analyze_btn_text, type="primary", use_container_width=True):
    if not description and not image_data:
        st.warning("⚠️ Opisz problem lub dodaj zdjęcie.")
    else:
        with st.spinner(t["analyzing"]):
            st.session_state.history = description
            response = analyze_request(mode_selection, vehicle_type, engine_type, description, lang_code, image_data)
            st.session_state.result = response

# Wyświetlanie Wyników
if st.session_state.result:
    res = st.session_state.result
    
    st.divider()
    
    # Obsługa błędu JSON lub Off-topic
    if not res:
        st.error("Błąd przetwarzania danych. Spróbuj ponownie.")
    elif "potentialCauses" not in res and "partsRecommendation" not in res:
         st.warning(res.get("summary", "Unknown response"))
    
    # Wyniki Diagnostyki
    elif mode_selection == "Diagnosis":
        sev_color = "red" if res.get("severity") in ["Critical", "Krytyczny", "Kritisch"] else "orange"
        st.subheader(f"🔍 {t['result_severity']}: :{sev_color}[{res.get('severity')}]")
        
        if res.get('safetyWarning'):
            st.error(f"**{t['result_safety']}:** {res.get('safetyWarning')}")
            
        st.markdown(f"### {res.get('summary')}")
        
        st.markdown(f"#### {t['result_causes']}")
        for cause in res.get("potentialCauses", []):
            with st.expander(f"{cause['name']} ({cause.get('likelihood', '?')}%)"):
                st.markdown(f"**Opis:** {cause.get('description', '-')}")
                st.markdown(f"**🔧 Rozwiązanie:** {cause.get('solution', '-')}")
                col_c1, col_c2 = st.columns(2)
                col_c1.metric("Koszt", cause.get('estimatedCost', '-'))
                col_c2.metric("Trudność", cause.get('difficulty', '-'))
        
        st.success(f"💡 **{t['result_tip']}:** {res.get('maintenanceTip')}")

    # Wyniki Tuningu
    elif mode_selection == "Tuning":
        st.subheader(f"⚡ {res.get('summary')}")
        
        c1, c2, c3 = st.columns(3)
        c1.metric(t["tune_power"], res.get("expectedPowerIncrease", "-"))
        c2.metric(t["tune_cost"], res.get("estimatedTotalCost", "-"))
        c3.metric(t["tune_rel"], res.get("reliabilityImpact", "-"))
        
        st.markdown(f"🏎️ **Wrażenia:** *{res.get('drivingCharacteristics')}*")
        
        st.markdown(f"#### {t['tune_parts']}")
        for part in res.get("partsRecommendation", []):
            with st.container():
                st.markdown(f"**{part['name']}** ({part.get('type', '-')})")
                st.caption(f"{part.get('description', '-')}")
                sc1, sc2 = st.columns(2)
                sc1.markdown(f"💰 {part.get('estimatedPrice', '-')}")
                sc2.markdown(f"📈 {part.get('powerGain', '-')}")
                st.divider()
        
        col_p, col_c = st.columns(2)
        with col_p:
            st.markdown(f"**👍 {t['tune_pros']}**")
            for p in res.get("pros", []):
                st.markdown(f"- {p}")
        with col_c:
            st.markdown(f"**👎 {t['tune_cons']}**")
            for c in res.get("cons", []):
                st.markdown(f"- {c}")

    # Sekcja Doprecyzowania
    st.divider()
    with st.form("refine_form"):
        st.markdown(f"### {t['refine_label']}")
        refine_text = st.text_input("Szczegóły", placeholder="Np. zapomniałem dodać, że silnik gaśnie na zimno...")
        if st.form_submit_button(t["refine_btn"]):
            with st.spinner(t["analyzing"]):
                new_history = f"{st.session_state.history}\nUser update: {refine_text}"
                st.session_state.history = new_history
                response = analyze_request(mode_selection, vehicle_type, engine_type, refine_text, lang_code, image_data, context_history=new_history)
                st.session_state.result = response
                st.rerun()

# Footer
st.markdown("---")
st.caption("© 2024 AutoWise. Powered by Google Gemini AI.")
