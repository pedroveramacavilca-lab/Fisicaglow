import streamlit as st
import google.generativeai as genai
import json
import random

# ============================================================
# CONFIGURACIÓN INICIAL
# ============================================================
st.set_page_config(page_title="PhysiQ", page_icon="⚡", layout="centered")

# Cada usuario ingresa su propia API key de Gemini al entrar.
# Se guarda SOLO en st.session_state (memoria de esa sesión del navegador),
# nunca se escribe en el código ni se comparte entre usuarios ni queda en el servidor.
if "gemini_api_key" not in st.session_state:
    st.session_state.gemini_api_key = None

model = None
IA_DISPONIBLE = False

if st.session_state.gemini_api_key:
    try:
        genai.configure(api_key=st.session_state.gemini_api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")
        IA_DISPONIBLE = True
    except Exception:
        IA_DISPONIBLE = False

# ============================================================
# BANCO DE PREGUNTAS (fijas, sin IA)
# ============================================================
TOPICS = ["Mecánica", "Termodinámica", "Electromagnetismo"]

QUESTIONS = {
    "Mecánica": [
        {"t": "Un bloque se mueve a velocidad constante de 3 m/s. ¿Cuál es la fuerza neta?",
         "f": None, "o": ["15 N", "0 N", "5 N", "9.8 N"], "c": 1,
         "e": "Por la 1ª ley de Newton, velocidad constante implica fuerza neta = 0. No hay aceleración, así que ΣF = ma = 0."},
        {"t": "Proyectil lanzado horizontalmente desde 20 m de altura. ¿Cuánto tarda en caer? (g = 10 m/s²)",
         "f": "h = ½ g t²", "o": ["1 s", "2 s", "4 s", "√2 s"], "c": 1,
         "e": "t = √(2h/g) = √(2×20/10) = √4 = 2 s. La componente horizontal no afecta la caída vertical."},
        {"t": "¿Energía cinética de un objeto de 2 kg moviéndose a 6 m/s?",
         "f": "Ec = ½ m v²", "o": ["12 J", "36 J", "72 J", "6 J"], "c": 1,
         "e": "Ec = ½ × 2 × 36 = 36 J. La energía cinética depende del cuadrado de la velocidad."},
        {"t": "Resorte con k = 200 N/m comprimido 0.1 m. ¿Energía potencial elástica?",
         "f": "Ep = ½ k x²", "o": ["20 J", "1 J", "10 J", "2 J"], "c": 1,
         "e": "Ep = ½ × 200 × 0.01 = 1 J. La energía crece con el cuadrado del desplazamiento."},
        {"t": "¿Aceleración de un objeto de 10 kg con fuerza neta de 50 N?",
         "f": "F = ma", "o": ["500 m/s²", "0.2 m/s²", "5 m/s²", "10 m/s²"], "c": 2,
         "e": "a = F/m = 50/10 = 5 m/s². Segunda ley de Newton: la aceleración es proporcional a la fuerza."},
    ],
    "Termodinámica": [
        {"t": "¿Cuál es el enunciado correcto de la primera ley de la termodinámica?",
         "f": "ΔU = Q - W", "o": ["La energía no se crea ni destruye", "El calor fluye del frío al caliente", "La entropía siempre disminuye", "La temperatura siempre aumenta"], "c": 0,
         "e": "La 1ª ley es conservación de energía. ΔU = Q - W: cambio en energía interna = calor absorbido − trabajo realizado por el sistema."},
        {"t": "Un gas ideal se expande isotérmicamente. ¿Cómo varía su energía interna?",
         "f": None, "o": ["Aumenta", "Disminuye", "Se mantiene constante", "Se vuelve cero"], "c": 2,
         "e": "En un proceso isotérmico la temperatura no cambia. Para un gas ideal, U depende solo de T, así que ΔU = 0."},
        {"t": "¿Qué tipo de proceso ocurre sin intercambio de calor con el entorno?",
         "f": "Q = 0", "o": ["Isotérmico", "Isobárico", "Adiabático", "Isocórico"], "c": 2,
         "e": "Proceso adiabático: no hay transferencia de calor (Q = 0). Todo el trabajo se hace a expensas de la energía interna."},
        {"t": "Un motor térmico opera entre 500 K y 300 K. ¿Cuál es su eficiencia máxima de Carnot?",
         "f": "η = 1 - Tc/Th", "o": ["40%", "60%", "30%", "50%"], "c": 0,
         "e": "η = 1 − 300/500 = 1 − 0.6 = 0.4 = 40%. La eficiencia de Carnot es la máxima teórica posible entre esas temperaturas."},
        {"t": "¿Qué magnitud mide el desorden o la aleatoriedad de un sistema termodinámico?",
         "f": None, "o": ["Entalpía", "Energía libre", "Entropía", "Trabajo"], "c": 2,
         "e": "La entropía (S) mide el grado de desorden del sistema. La 2ª ley establece que en procesos espontáneos la entropía total no disminuye."},
    ],
    "Electromagnetismo": [
        {"t": "¿De qué depende la fuerza entre dos cargas eléctricas según la ley de Coulomb?",
         "f": "F = k q₁q₂ / r²", "o": ["Solo de las masas", "Producto de cargas y distancia al cuadrado", "Solo de la distancia", "De la temperatura"], "c": 1,
         "e": "F es proporcional al producto de las cargas e inversamente proporcional a r². Duplicar la distancia reduce la fuerza 4 veces."},
        {"t": "¿Cuál es la unidad del campo eléctrico en el sistema SI?",
         "f": "E = F/q", "o": ["Tesla (T)", "Coulomb (C)", "Newton/Coulomb (N/C)", "Voltio (V)"], "c": 2,
         "e": "El campo eléctrico E = F/q tiene unidades de N/C, equivalente también a V/m."},
        {"t": "Un conductor en equilibrio electrostático. ¿Dónde se ubica la carga libre?",
         "f": None, "o": ["En el centro", "Uniformemente distribuida", "Solo en la superficie", "En los bordes internos"], "c": 2,
         "e": "En equilibrio electrostático, las cargas libres se distribuyen en la superficie del conductor. El campo interior es cero."},
        {"t": "La ley de Faraday establece que una FEM inducida se genera cuando:",
         "f": "ε = -dΦ/dt", "o": ["El campo eléctrico es constante", "El flujo magnético varía en el tiempo", "La corriente es continua", "La resistencia aumenta"], "c": 1,
         "e": "ε = −dΦ/dt: la FEM inducida es proporcional a la variación temporal del flujo magnético. Base del funcionamiento de generadores."},
        {"t": "¿Qué expresa la ley de Ohm?",
         "f": "V = IR", "o": ["La resistencia depende de la temperatura", "El voltaje es producto de corriente y resistencia", "La corriente siempre es constante", "La potencia es igual a la corriente al cuadrado"], "c": 1,
         "e": "V = IR: el voltaje entre dos puntos es igual al producto de la corriente por la resistencia. Válida para resistores lineales."},
    ],
}

# ============================================================
# ESTADO DE SESIÓN (se reinicia si el usuario refresca la página)
# ============================================================
def init_state():
    defaults = {
        "topic": "Mecánica",
        "q_idx": 0,
        "xp": 0,
        "lives": 5,
        "streak": 1,
        "round_correct": 0,
        "round_xp": 0,
        "answered": False,
        "selected_option": None,
        "current_q": None,
        "ai_question_active": False,
        "chat_history": [],
        "last_wrong_q": None,
        "show_results": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

    if st.session_state.current_q is None:
        st.session_state.current_q = QUESTIONS[st.session_state.topic][0]


init_state()

# ============================================================
# PANTALLA DE BIENVENIDA: pedir API key antes de usar la app
# ============================================================
if not st.session_state.gemini_api_key:
    st.markdown("## ⚡ PhysiQ")
    st.caption("Aprende física universitaria como si fuera un juego, con un tutor de IA")
    st.divider()

    st.markdown("### 🔑 Ingresa tu API key de Gemini para empezar")
    st.write(
        "PhysiQ usa el tutor de inteligencia artificial de Google Gemini. "
        "Para usarlo necesitas tu propia API key gratuita (no se comparte con nadie "
        "ni se guarda en ningún servidor, solo se usa durante tu sesión)."
    )

    with st.expander("¿No tienes una API key? Consíguela gratis en 1 minuto"):
        st.markdown(
            """
            1. Ve a **[aistudio.google.com](https://aistudio.google.com)** e inicia sesión con tu cuenta de Google
            2. En el menú izquierdo, clic en **"Get API key"**
            3. Clic en **"Create API key"**
            4. Copia la clave (empieza con `AIza...`) y pégala abajo

            No necesitas tarjeta de crédito, el plan gratuito es suficiente para usar esta app.
            """
        )

    key_input = st.text_input("Tu API key de Gemini", type="password", placeholder="AIza...")

    col_a, col_b = st.columns([1, 3])
    with col_a:
        entrar = st.button("Entrar →", type="primary", use_container_width=True)

    if entrar:
        if not key_input.strip():
            st.error("Por favor ingresa una API key válida.")
        else:
            with st.spinner("Verificando tu API key..."):
                try:
                    genai.configure(api_key=key_input.strip())
                    test_model = genai.GenerativeModel("gemini-2.5-flash")
                    test_model.generate_content("Responde solo con: OK")
                    st.session_state.gemini_api_key = key_input.strip()
                    st.rerun()
                except Exception as e:
                    st.error(f"La API key no es válida o hubo un error de conexión: {e}")

    st.stop()

# ============================================================
# FUNCIONES DE IA (Gemini)
# ============================================================
def generar_pregunta_ia(topic):
    prompt = f"""Eres un generador de preguntas de física universitaria.
Genera UNA pregunta de examen de dificultad moderada sobre el tema: {topic}.
Usa valores numéricos concretos cuando sea posible.
Responde SOLO con un JSON válido, sin texto adicional ni backticks, con este formato exacto:
{{"pregunta": "...", "formula": "..." o null, "opciones": ["A", "B", "C", "D"], "correcta": 0, "explicacion": "..."}}
El campo "correcta" es el índice (0 a 3) de la opción correcta.
La explicación debe ser educativa y concisa (2-3 oraciones)."""
    try:
        response = model.generate_content(prompt)
        raw = response.text.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        data = json.loads(raw)
        return {
            "t": data["pregunta"],
            "f": data.get("formula"),
            "o": data["opciones"],
            "c": data["correcta"],
            "e": data["explicacion"],
        }
    except Exception as e:
        st.error(f"No se pudo generar la pregunta con IA: {e}")
        return None


def preguntar_tutor(mensaje, topic, pregunta_actual, wrong_q=None):
    contexto_error = ""
    if wrong_q:
        contexto_error = f'El estudiante respondió incorrectamente esta pregunta: "{wrong_q["t"]}". Ayúdale a entenderla sin revelar directamente cuál es la opción correcta de forma explícita si aún no la sabe.'

    prompt = f"""Eres PhysiQ, un tutor experto en física universitaria, amigable y conciso.
Tema actual del estudiante: {topic}.
Pregunta activa: "{pregunta_actual['t']}"
{contexto_error}

Responde en español, en máximo 3-4 oraciones, usando analogías cotidianas cuando ayude.
No reveles directamente la respuesta de la pregunta activa.

Pregunta del estudiante: {mensaje}"""
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error al conectar con el tutor IA: {e}"


# ============================================================
# ESTILOS
# ============================================================
st.markdown("""
<style>
.stApp { max-width: 700px; margin: 0 auto; }
.stat-box { text-align: center; padding: 8px; border-radius: 10px; background: #f0f2f6; }
.topic-pill { display: inline-block; padding: 4px 12px; background: #E6F1FB; color: #185FA5;
              border-radius: 20px; font-size: 13px; font-weight: 600; margin-bottom: 8px; }
.formula-box { background: #f0f2f6; padding: 10px; border-radius: 8px; text-align: center;
               font-family: monospace; margin: 10px 0; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# HEADER: logo + stats
# ============================================================
st.markdown("## ⚡ PhysiQ")
st.caption("Aprende física universitaria como si fuera un juego, con un tutor de IA")

col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
with col1:
    st.markdown(f"<div class='stat-box'>🔥 <b>{st.session_state.streak}</b> días</div>", unsafe_allow_html=True)
with col2:
    st.markdown(f"<div class='stat-box'>⭐ <b>{st.session_state.xp}</b> XP</div>", unsafe_allow_html=True)
with col3:
    st.markdown(f"<div class='stat-box'>❤️ <b>{st.session_state.lives}</b> vidas</div>", unsafe_allow_html=True)
with col4:
    if st.button("🔑 Cambiar key", use_container_width=True):
        st.session_state.gemini_api_key = None
        st.rerun()

st.divider()

# ============================================================
# SELECTOR DE TEMA
# ============================================================
st.markdown("**Elige un tema:**")
topic_choice = st.radio("Tema", TOPICS, horizontal=True, label_visibility="collapsed",
                         index=TOPICS.index(st.session_state.topic))

if topic_choice != st.session_state.topic:
    st.session_state.topic = topic_choice
    st.session_state.q_idx = 0
    st.session_state.round_correct = 0
    st.session_state.round_xp = 0
    st.session_state.answered = False
    st.session_state.ai_question_active = False
    st.session_state.show_results = False
    st.session_state.current_q = QUESTIONS[topic_choice][0]
    st.rerun()

st.divider()

# ============================================================
# PANTALLA DE RESULTADOS (al terminar una ronda)
# ============================================================
if st.session_state.show_results:
    total = len(QUESTIONS[st.session_state.topic])
    pct = st.session_state.round_correct / total

    if pct == 1:
        st.success("🎉 ¡Perfecto! Respondiste todas correctamente")
    elif pct >= 0.6:
        st.success("👍 ¡Buen trabajo!")
    else:
        st.info("📘 Sigue practicando, vas mejorando")

    r1, r2, r3 = st.columns(3)
    with r1:
        st.metric("Correctas", f"{st.session_state.round_correct}/{total}")
    with r2:
        st.metric("XP ganados", f"+{st.session_state.round_xp}")
    with r3:
        st.metric("Racha", f"{st.session_state.streak} 🔥")

    if st.button("Jugar otra ronda", type="primary", use_container_width=True):
        st.session_state.q_idx = 0
        st.session_state.round_correct = 0
        st.session_state.round_xp = 0
        st.session_state.answered = False
        st.session_state.ai_question_active = False
        st.session_state.show_results = False
        st.session_state.current_q = QUESTIONS[st.session_state.topic][0]
        st.session_state.streak += 1
        st.rerun()

else:
    # ============================================================
    # ÁREA DE PREGUNTA
    # ============================================================
    total_qs = len(QUESTIONS[st.session_state.topic])
    st.markdown(f"<span class='topic-pill'>{st.session_state.topic}</span>", unsafe_allow_html=True)
    st.progress((st.session_state.q_idx) / total_qs, text=f"Pregunta {st.session_state.q_idx + 1} de {total_qs}")

    if IA_DISPONIBLE:
        if st.button("✨ Generar pregunta con IA (en vez de la fija)"):
            with st.spinner("Generando pregunta con IA..."):
                nueva = generar_pregunta_ia(st.session_state.topic)
                if nueva:
                    st.session_state.current_q = nueva
                    st.session_state.answered = False
                    st.session_state.selected_option = None
                    st.session_state.ai_question_active = True
                    st.rerun()

    q = st.session_state.current_q
    st.markdown(f"#### {q['t']}")
    if q.get("f"):
        st.markdown(f"<div class='formula-box'>{q['f']}</div>", unsafe_allow_html=True)

    if not st.session_state.answered:
        choice = st.radio("Opciones", q["o"], index=None, label_visibility="collapsed", key=f"radio_{st.session_state.q_idx}_{st.session_state.ai_question_active}")

        if st.button("Responder", type="primary", disabled=(choice is None)):
            st.session_state.selected_option = q["o"].index(choice)
            st.session_state.answered = True

            if st.session_state.selected_option == q["c"]:
                st.session_state.xp += 20
                st.session_state.round_correct += 1
                st.session_state.round_xp += 20
                st.session_state.last_wrong_q = None
            else:
                st.session_state.lives = max(0, st.session_state.lives - 1)
                st.session_state.last_wrong_q = q
            st.rerun()
    else:
        if st.session_state.selected_option == q["c"]:
            st.success(f"✅ **¡Correcto!** {q['e']}")
        else:
            st.error(f"❌ **Incorrecto.** La respuesta correcta era: *{q['o'][q['c']]}*\n\n{q['e']}")

        if st.button("Siguiente →", type="primary", use_container_width=True):
            st.session_state.q_idx += 1
            st.session_state.answered = False
            st.session_state.selected_option = None
            st.session_state.ai_question_active = False

            if st.session_state.q_idx >= total_qs:
                st.session_state.show_results = True
            else:
                st.session_state.current_q = QUESTIONS[st.session_state.topic][st.session_state.q_idx]
            st.rerun()

st.divider()

# ============================================================
# TUTOR IA (CHAT)
# ============================================================
st.markdown("### 🤖 Tutor IA")
st.caption("Pregúntale cualquier duda sobre el tema, o pídele que te explique por qué fallaste")

for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

if IA_DISPONIBLE:
    user_msg = st.chat_input("Escribe tu duda sobre física...")
    if user_msg:
        st.session_state.chat_history.append({"role": "user", "content": user_msg})
        with st.spinner("El tutor está pensando..."):
            respuesta = preguntar_tutor(
                user_msg,
                st.session_state.topic,
                st.session_state.current_q,
                st.session_state.last_wrong_q,
            )
        st.session_state.chat_history.append({"role": "assistant", "content": respuesta})
        st.rerun()
else:
    st.info("El chat con el tutor se activará cuando se configure la API key de Gemini.")
