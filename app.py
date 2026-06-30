import streamlit as st
import google.generativeai as genai
import json

st.set_page_config(
    page_title="PhysiQ",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# API KEY
# ============================================================
if "gemini_api_key" not in st.session_state:
    st.session_state.gemini_api_key = None

model = None

if st.session_state.gemini_api_key:
    try:
        genai.configure(api_key=st.session_state.gemini_api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")
    except Exception:
        model = None

# ============================================================
# TEMAS DEL CURSO
# ============================================================
TOPICS = [
    "📐  Movimiento 1D y 2D",
    "⚖️  Fuerzas y leyes de Newton",
    "🔄  Torque y equilibrio",
    "💼  Trabajo y potencia",
    "⚡  Energía y conservación",
]

# ============================================================
# ESTADO DE SESIÓN
# ============================================================
def init_state():
    defaults = {
        "topic": TOPICS[0],
        "chat_history": [],         # historial del chat visible
        "gemini_history": [],       # historial para la API de Gemini (multi-turn)
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ============================================================
# PROMPT DEL SISTEMA — el corazón pedagógico de la app
# ============================================================
def build_system_prompt(topic):
    return f"""Eres PhysiQ, un tutor de física universitaria especializado en enseñanza profunda.
Tu filosofía: NUNCA das una fórmula sin explicar primero de dónde viene y para qué sirve.

Tema actual del estudiante: {topic}

## Tus dos modos de respuesta:

### MODO SOCRÁTICO (cuando el estudiante trae un ejercicio con datos):
1. Primero pregúntale: ¿qué crees que está pasando físicamente en este problema?
2. Ayúdalo a identificar qué datos tiene y qué le piden
3. Pregúntale qué principio físico cree que aplica, ANTES de decírselo tú
4. Guíalo paso a paso con preguntas, sin resolver por él
5. Solo confirma o corrige cuando el estudiante proponga algo
6. Al final, explica el significado físico del resultado — no solo el número

### MODO CONCEPTUAL (cuando pregunta por teoremas, leyes o conceptos):
1. Empieza SIEMPRE con una analogía cotidiana antes de cualquier fórmula
2. Explica el "por qué" existe ese concepto — qué problema de la física resuelve
3. Después muestra la fórmula y explica cada símbolo
4. Da un ejemplo numérico simple
5. Termina con una pregunta para verificar que entendió

## Reglas que nunca rompes:
- Nunca resuelves un ejercicio completo de una sola vez
- Nunca das una fórmula sin su explicación conceptual primero
- Siempre preguntas al estudiante antes de explicar, para activar su razonamiento
- Si el estudiante insiste en que le des la respuesta directa, dile amablemente que aprenderá más si llega solo
- Detecta errores conceptuales y nómbralos claramente: "Aquí estás confundiendo X con Y, son diferentes porque..."
- Responde siempre en español
- Sé amigable, paciente y motivador — nunca condescendiente"""

# ============================================================
# FUNCIÓN PRINCIPAL DE CHAT CON GEMINI (multi-turn real)
# ============================================================
def chat_con_tutor(mensaje_usuario, topic):
    if not model:
        return "Error: no hay conexión con la IA."

    try:
        # El modelo se crea con la instrucción del sistema ya incluida
        chat_model = genai.GenerativeModel(
            "gemini-2.5-flash",
            system_instruction=build_system_prompt(topic)
        )

        # Reconstruir el historial previo en formato Gemini
        gemini_messages = []
        for msg in st.session_state.gemini_history:
            gemini_messages.append({
                "role": msg["role"],
                "parts": [msg["content"]]
            })

        # Iniciar el chat CON el historial previo (esto da la continuidad real)
        chat = chat_model.start_chat(history=gemini_messages)

        response = chat.send_message(
            mensaje_usuario,
            generation_config={"temperature": 0.7, "max_output_tokens": 1024},
        )
        respuesta = response.text.strip()

        # Guardar el turno en el historial para la siguiente consulta
        st.session_state.gemini_history.append({"role": "user", "content": mensaje_usuario})
        st.session_state.gemini_history.append({"role": "model", "content": respuesta})

        return respuesta

    except Exception as e:
        return f"Error de conexión con la IA: {e}"

# ============================================================
# ESTILOS DARK MODE
# ============================================================
st.markdown("""
<style>
.stApp { background-color: #0D0F14; color: #E8EAF0; }

[data-testid="stSidebar"] {
    background-color: #141720 !important;
    border-right: 1px solid rgba(255,255,255,0.07);
}
[data-testid="stSidebar"] * { color: #E8EAF0 !important; }

[data-testid="stTextInput"] input,
[data-testid="stChatInput"] textarea {
    background-color: #1C2030 !important;
    color: #E8EAF0 !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 10px !important;
}

.stButton > button[kind="primary"] {
    background: #4C8EF7 !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
}
.stButton > button {
    background: #1C2030 !important;
    color: #8B90A0 !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 10px !important;
}
.stButton > button:hover {
    border-color: #4C8EF7 !important;
    color: #E8EAF0 !important;
}

[data-testid="stChatMessage"] {
    background: #1C2030 !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 12px !important;
    margin-bottom: 8px !important;
}

.stSuccess { background: rgba(52,211,153,0.1) !important; border-color: rgba(52,211,153,0.3) !important; color: #34D399 !important; border-radius: 10px !important; }
.stInfo    { background: rgba(76,142,247,0.1)  !important; border-color: rgba(76,142,247,0.3)  !important; color: #4C8EF7  !important; border-radius: 10px !important; }
.stWarning { background: rgba(251,191,36,0.1)  !important; border-color: rgba(251,191,36,0.3)  !important; color: #FBBF24  !important; border-radius: 10px !important; }

hr { border-color: rgba(255,255,255,0.07) !important; }

.stat-card {
    background: #1C2030;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 10px;
    padding: 12px;
    text-align: center;
    margin-bottom: 8px;
}
.stat-val { font-size: 22px; font-weight: 700; color: #E8EAF0; }
.stat-lbl { font-size: 11px; color: #555A70; margin-top: 2px; }

.tip-box {
    background: rgba(76,142,247,0.08);
    border: 1px solid rgba(76,142,247,0.2);
    border-radius: 10px;
    padding: 12px 16px;
    font-size: 13px;
    color: #8B90A0;
    margin-bottom: 1rem;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# PANTALLA DE BIENVENIDA — API key
# ============================================================
if not st.session_state.gemini_api_key:
    st.markdown("## ⚡ PhysiQ")
    st.markdown("#### Tu tutor de física — aprende el *por qué*, no solo la fórmula")
    st.divider()

    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("**¿Qué puedes hacer?**")
        st.markdown("""
- 📝 **Traer un ejercicio** y resolverlo paso a paso guiado por la IA
- 💡 **Preguntar por un concepto** y entender de dónde vienen las fórmulas
- 🔍 **Verificar tu procedimiento** y saber exactamente dónde te equivocaste
- 🧠 **Explorar el "por qué"** detrás de cada ley y teorema
        """)
    with col2:
        st.markdown("**¿Cómo funciona?**")
        st.info("La IA no te da las respuestas directamente. Te hace preguntas para que llegues solo — así aprendes de verdad.")

    st.divider()
    st.markdown("### 🔑 Ingresa tu API key de Gemini para empezar")
    st.caption("Gratuita, no se guarda en ningún servidor, solo existe durante tu sesión.")

    with st.expander("¿Cómo consigo mi API key gratis?"):
        st.markdown("""
1. Ve a **[aistudio.google.com](https://aistudio.google.com)** e inicia sesión con Google
2. Clic en **"Get API key"** → **"Create API key"**
3. Copia la clave (empieza con `AIza...`) y pégala abajo
        """)

    key_input = st.text_input("Tu API key de Gemini", type="password", placeholder="AIza...")
    col_a, col_b = st.columns([1, 3])
    with col_a:
        if st.button("Entrar →", type="primary", use_container_width=True):
            if not key_input.strip():
                st.error("Ingresa una API key válida.")
            else:
                with st.spinner("Verificando..."):
                    try:
                        genai.configure(api_key=key_input.strip())
                        test = genai.GenerativeModel("gemini-2.5-flash")
                        test.generate_content("OK")
                        st.session_state.gemini_api_key = key_input.strip()
                        st.rerun()
                    except Exception as e:
                        st.error(f"API key no válida: {e}")
    st.stop()

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown("## ⚡ PhysiQ")
    st.caption("Tutor de física con IA")
    st.divider()

    st.markdown("**Tema actual**")
    for t in TOPICS:
        is_active = st.session_state.topic == t
        if st.button(
            t, key=f"topic_{t}",
            use_container_width=True,
            type="primary" if is_active else "secondary"
        ):
            if t != st.session_state.topic:
                st.session_state.topic = t
                # Al cambiar de tema, limpiar historial para nuevo contexto
                st.session_state.chat_history = []
                st.session_state.gemini_history = []
                st.rerun()

    st.divider()

    if st.button("🗑️ Nueva conversación", use_container_width=True):
        st.session_state.chat_history = []
        st.session_state.gemini_history = []
        st.rerun()

    st.divider()
    if st.button("🔑 Cambiar API key", use_container_width=True):
        st.session_state.gemini_api_key = None
        st.rerun()

# ============================================================
# ÁREA PRINCIPAL
# ============================================================
topic_clean = st.session_state.topic.split("  ", 1)[-1].strip()
st.markdown(f"## {st.session_state.topic}")
st.caption(f"Modo socrático activo — la IA te guía sin darte las respuestas directas")
st.divider()

# ============================================================
# SUGERENCIAS DE USO (solo si no hay mensajes aún)
# ============================================================
if not st.session_state.chat_history:
    st.markdown("<div class='tip-box'>💬 <b>¿Cómo empezar?</b> Puedes escribir un ejercicio con sus datos, preguntar por un concepto o teorema, o pedirle que revise tu procedimiento. La IA siempre te preguntará antes de explicar.</div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""**📝 Ejemplo — Ejercicio**
> *"Un auto de 1200 kg frena desde 20 m/s hasta detenerse en 4 s. ¿Cuál es la fuerza de frenado?"*""")
    with col2:
        st.markdown("""**💡 Ejemplo — Concepto**
> *"No entiendo la diferencia entre masa y peso, ¿me lo puedes explicar?"*""")
    with col3:
        st.markdown("""**🔍 Ejemplo — Verificar**
> *"Resolví así: F = m×a = 1200×5 = 6000 N ¿está bien mi procedimiento?"*""")
    st.divider()

# ============================================================
# CHAT
# ============================================================
chat_container = st.container(height=480)
with chat_container:
    if not st.session_state.chat_history:
        with st.chat_message("assistant"):
            st.write(f"Hola, soy PhysiQ. Estamos trabajando el tema **{topic_clean}**. Puedes traerme un ejercicio, preguntarme por un concepto, o pedirme que revise tu procedimiento. ¿Por dónde empezamos?")
    else:
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

user_msg = st.chat_input(f"Escribe tu ejercicio o duda sobre {topic_clean}...")
if user_msg:
    st.session_state.chat_history.append({"role": "user", "content": user_msg})
    with st.spinner("PhysiQ está pensando..."):
        respuesta = chat_con_tutor(user_msg, st.session_state.topic)
    st.session_state.chat_history.append({"role": "assistant", "content": respuesta})
    st.rerun()
