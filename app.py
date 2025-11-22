import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- KONFIGURACJA STRONY ---
st.set_page_config(
    page_title="AutoWise",
    page_icon="🔧",
    layout="centered"
)

# --- POBRANIE KLUCZA API ---
# Upewnij się, że w Advanced Settings na Streamlit Cloud masz wpisany klucz: GOOGLE_API_KEY = "..."
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception as e:
    st.error("⚠️ Brak klucza API! Ustaw GOOGLE_API_KEY w 'Advanced settings' swojej aplikacji na Streamlit.")
    st.stop()

# --- INSTRUKCJA DLA SZTUCZNEJ INTELIGENCJI ---
# To jest "mózg" Twojej aplikacji stworzony na podstawie Twoich promptów
system_instruction = """
Jesteś AutoWise - zaawansowanym asystentem AI wyspecjalizowanym w motoryzacji.
Twoim zadaniem jest pomaganie w diagnozowaniu usterek mechanicznych w samochodach, motocyklach, ciężarówkach i innych pojazdach spalinowych, hybrydowych oraz elektrycznych.

ZASADY DZIAŁANIA:
1. TEMATYKA: Odpowiadaj TYLKO na pytania związane z motoryzacją. Jeśli użytkownik zapyta o coś niezwiązanego (np. o pogodę, przepis na ciasto), odpowiedz uprzejmie: "Pytanie nie jest związane z motoryzacją, spytaj ponownie o kwestie samochodu lub mechaniki."
2. DIAGNOZA: Gdy użytkownik opisuje problem, podaj potencjalne przyczyny i rozwiązania. Zachęcaj do podania szczegółów (model, rocznik, dźwięki).
3. TUNING: Jeśli użytkownik pyta o modyfikacje, oszacuj koszty, wpływ na jazdę i żywotność pojazdu. Sugeruj konkretne części (np. typ turbosprężarki) pasujące do silnika.
4. ZDJĘCIA: Jeśli otrzymasz zdjęcie, rozpoznaj część samochodową i spróbuj zdiagnozować problem na podstawie jej wyglądu.
5. JĘZYK: Dostosuj język odpowiedzi do wyboru użytkownika (Polski, Angielski, Niemiecki).
"""

# --- KONFIGURACJA MODELU ---
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=system_instruction
)

# --- INTERFEJS UŻYTKOWNIKA (SIDEBAR) ---
with st.sidebar:
    st.header("⚙️ Ustawienia AutoWise")
    language = st.selectbox("Wybierz język / Select Language:", ["Polski", "English", "Deutsch"])
    mode = st.radio("Tryb pracy:", ["Diagnostyka i Naprawa", "Tuning i Modyfikacje"])
    st.info("💡 Wskazówka: Opisz usterkę jak najdokładniej, podając okoliczności jej wystąpienia.")

st.title("🔧 AutoWise")
st.caption("Twój inteligentny mechanik samochodowy")

# --- HISTORIA CZATU ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Witaj w AutoWise! Opisz problem ze swoim pojazdem lub prześlij zdjęcie części, a postaram się pomóc."}
    ]

# Wyświetlanie historii wiadomości
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- OBSŁUGA ZDJĘĆ ---
uploaded_file = st.file_uploader("Dodaj zdjęcie uszkodzonej części (opcjonalnie)", type=["jpg", "jpeg", "png"])

# --- POLE DO WPISYWANIA ---
# Tekst zachęty zdefiniowany w Twoich wymaganiach
user_input = st.chat_input("Opisz objawy lub zrób zdjęcie uszkodzonej części. AutoWise rozpozna element i zdiagnozuje problem...")

if user_input or uploaded_file:
    # Jeśli użytkownik wysłał zdjęcie, ale nie napisał tekstu, dodajemy domyślny tekst
    if uploaded_file and not user_input:
        user_input = "Przesyłam zdjęcie części do analizy. Co to jest i czy wygląda na uszkodzone?"

    if user_input:
        # 1. Dodaj wiadomość użytkownika do historii
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)
            if uploaded_file:
                image = Image.open(uploaded_file)
                st.image(image, caption="Przesłane zdjęcie", use_column_width=True)

        # 2. Wyślij zapytanie do Gemini
        with st.chat_message("assistant"):
            with st.spinner("AutoWise analizuje problem..."):
                try:
                    # Budowanie kontekstu dla modelu
                    context_text = f"Język odpowiedzi: {language}. Tryb: {mode}. Pytanie użytkownika: {user_input}"
                    
                    if uploaded_file:
                        image = Image.open(uploaded_file)
                        response = model.generate_content([context_text, image])
                    else:
                        # Przekazujemy też historię rozmowy dla kontekstu
                        chat = model.start_chat(history=[]) 
                        # (Uproszczenie: w pełnej wersji można tu przekazać st.session_state.messages, 
                        # ale dla prostoty wysyłamy bieżące zapytanie z instrukcją systemową)
                        response = model.generate_content(context_text)

                    st.markdown(response.text)
                    
                    # 3. Zapisz odpowiedź AI w historii
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                
                except Exception as e:
                    st.error(f"Wystąpił błąd: {e}")
