import streamlit as st
import google.generative_ai as genai

# 1. Konfiguracja strony
st.set_page_config(page_title="Moja Aplikacja AI")
st.title("🤖 Asystent AI")

# 2. Pobieranie klucza z "Sejf" Streamlita (o tym w Kroku 4)
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("Brakuje klucza API! Ustaw go w zakładce Secrets na Streamlit Cloud.")
    st.stop()

# 3. Konfiguracja modelu
# Jeśli masz specjalne instrukcje z AI Studio, wklej je w 'system_instruction'
model = genai.GenerativeModel(
    'gemini-1.5-flash',
    system_instruction="Jesteś pomocnym asystentem. Odpowiadaj zwięźle." 
)

# 4. Interfejs użytkownika
user_input = st.chat_input("Wpisz swoje pytanie tutaj...")

# Historia czatu na ekranie
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. Logika działania po wpisaniu tekstu
if user_input:
    # Pokaż wiadomość użytkownika
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Wygeneruj odpowiedź
    try:
        response = model.generate_content(user_input)
        bot_reply = response.text
        
        # Pokaż odpowiedź bota
        st.session_state.messages.append({"role": "assistant", "content": bot_reply})
        with st.chat_message("assistant"):
            st.markdown(bot_reply)
            
    except Exception as e:
        st.error(f"Wystąpił błąd: {e}")
