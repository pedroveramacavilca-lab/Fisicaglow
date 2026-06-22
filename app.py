import streamlit as st
import google.generativeai as genai
import json

st.set_page_config(page_title="PhysiQ", page_icon="⚡", layout="centered")

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
# BANCO DE PREGUNTAS
# ============================================================
TOPICS = [
    "Movimiento 1D y 2D",
    "Fuerzas y leyes de Newton",
    "Torque y equilibrio",
    "Trabajo y potencia",
    "Energía y conservación",
]

QUESTIONS = {
    "Movimiento 1D y 2D": [
        {"t": "Un auto parte del reposo y alcanza 20 m/s en 5 s con aceleración constante. ¿Cuál es su aceleración?",
         "f": "a = (vf - vi) / t", "o": ["2 m/s²", "4 m/s²", "10 m/s²", "100 m/s²"], "c": 1,
         "e": "a = (20 - 0) / 5 = 4 m/s². En el MRUV la aceleración es constante e igual al cambio de velocidad entre el tiempo."},
        {"t": "Un objeto en MRU recorre 150 m en 30 s. ¿Cuál es su velocidad?",
         "f": "v = d / t", "o": ["0.2 m/s", "5 m/s", "450 m/s", "30 m/s"], "c": 1,
         "e": "v = 150 / 30 = 5 m/s. En MRU la velocidad es constante e igual a la distancia entre el tiempo."},
        {"t": "En caída libre desde el reposo, ¿cuánto cae un objeto en los primeros 3 s? (g = 9.8 m/s²)",
         "f": "y = ½ g t²", "o": ["9.8 m", "29.4 m", "44.1 m", "88.2 m"], "c": 2,
         "e": "y = ½ × 9.8 × 9 = 44.1 m. La distancia en caída libre crece con el cuadrado del tiempo."},
        {"t": "Un proyectil se lanza horizontalmente a 15 m/s. ¿Cuál es su velocidad horizontal a los 3 s?",
         "f": None, "o": ["45 m/s", "9.8 m/s", "15 m/s", "29.4 m/s"], "c": 2,
         "e": "En movimiento parabólico la componente horizontal es constante (no hay aceleración horizontal). Siempre vale 15 m/s."},
        {"t": "Un objeto en movimiento circular uniforme tiene ω = 2π rad/s y radio r = 3 m. ¿Cuál es su velocidad lineal?",
         "f": "v = ω · r", "o": ["6π m/s", "2π m/s", "3 m/s", "π m/s"], "c": 0,
         "e": "v = ω × r = 2π × 3 = 6π ≈ 18.85 m/s. La velocidad lineal es el producto de la velocidad angular por el radio."},
    ],
    "Fuerzas y leyes de Newton": [
        {"t": "Un bloque de 8 kg reposa sobre una superficie horizontal. ¿Cuál es la fuerza normal? (g = 9.8 m/s²)",
         "f": "N = m · g", "o": ["9.8 N", "78.4 N", "8 N", "0 N"], "c": 1,
         "e": "N = m × g = 8 × 9.8 = 78.4 N. La normal equilibra el peso del objeto en reposo sobre superficie horizontal."},
        {"t": "Se aplica 40 N a un bloque de 5 kg con fricción cinética de 15 N. ¿Cuál es la aceleración?",
         "f": "ΣF = F - f = ma", "o": ["8 m/s²", "3 m/s²", "5 m/s²", "11 m/s²"], "c": 2,
         "e": "ΣF = 40 - 15 = 25 N → a = 25/5 = 5 m/s². La fricción se resta a la fuerza aplicada antes de aplicar F = ma."},
        {"t": "Dos bloques A (3 kg) y B (5 kg) en contacto reciben 24 N. ¿Cuál es la fuerza de contacto entre ellos?",
         "f": "F_contacto = m_B · a", "o": ["24 N", "15 N", "9 N", "3 N"], "c": 1,
         "e": "a = 24/8 = 3 m/s². Fuerza sobre B = m_B × a = 5 × 3 = 15 N. Se aplica la 2ª ley sobre B solo."},
        {"t": "Coeficiente de fricción estática μe = 0.4 y normal N = 50 N. ¿Cuál es la máxima fricción estática?",
         "f": "fs = μe · N", "o": ["125 N", "20 N", "0.4 N", "50 N"], "c": 1,
         "e": "fs_max = μe × N = 0.4 × 50 = 20 N. Si la fuerza aplicada supera 20 N, el objeto comienza a moverse."},
        {"t": "Un objeto está en equilibrio con ΣFx = 0, ΣFy = 0 y Στ = 0. ¿Qué tipo de equilibrio es?",
         "f": None, "o": ["Dinámico", "Inestable", "Estático", "Neutral"], "c": 2,
         "e": "Equilibrio estático: el objeto no se traslada ni rota. Requiere las tres condiciones simultáneamente."},
    ],
    "Torque y equilibrio": [
        {"t": "Una fuerza de 30 N se aplica perpendicularmente a 0.5 m del pivote. ¿Cuál es el torque?",
         "f": "τ = F · d", "o": ["60 N·m", "15 N·m", "0.5 N·m", "30 N·m"], "c": 1,
         "e": "τ = F × d = 30 × 0.5 = 15 N·m. Cuando la fuerza es perpendicular al brazo, el torque es simplemente su producto."},
        {"t": "Una fuerza de 20 N a 0.8 m del eje forma 30° con el brazo. ¿Cuál es el torque?",
         "f": "τ = F · d · sen(θ)", "o": ["16 N·m", "8 N·m", "13.9 N·m", "20 N·m"], "c": 1,
         "e": "τ = 20 × 0.8 × sen(30°) = 20 × 0.8 × 0.5 = 8 N·m. Solo la componente perpendicular a r genera torque."},
        {"t": "Una varilla uniforme de 4 m y 10 kg está apoyada en sus extremos. ¿Reacción en cada apoyo? (g = 10 m/s²)",
         "f": "R1 = R2 = mg / 2", "o": ["100 N cada uno", "50 N cada uno", "25 N cada uno", "200 N cada uno"], "c": 1,
         "e": "Por simetría: R1 + R2 = mg = 100 N y R1 = R2, entonces cada apoyo soporta 50 N."},
        {"t": "¿Cuál es la condición de equilibrio rotacional?",
         "f": None, "o": ["ΣF = 0", "Στ = 0", "v = 0", "a = 0"], "c": 1,
         "e": "Equilibrio rotacional exige Στ = 0. El equilibrio traslacional exige ΣF = 0. Ambas se necesitan para equilibrio completo de un cuerpo rígido."},
        {"t": "Un cuerpo rígido tiene Στ = 0 y ΣF ≠ 0. ¿Qué movimiento tiene?",
         "f": None, "o": ["Solo rotación", "Solo traslación", "Traslación y rotación", "Está en reposo"], "c": 1,
         "e": "ΣF ≠ 0 implica aceleración traslacional. Στ = 0 implica sin aceleración angular. Resultado: solo traslación acelerada."},
    ],
    "Trabajo y potencia": [
        {"t": "Una fuerza de 50 N desplaza un objeto 8 m en la misma dirección. ¿Cuánto trabajo realiza?",
         "f": "W = F · d", "o": ["6.25 J", "400 J", "58 J", "42 J"], "c": 1,
         "e": "W = F × d = 50 × 8 = 400 J. Cuando fuerza y desplazamiento son paralelos, el trabajo es su producto directo."},
        {"t": "Una fuerza de 60 N se aplica con 60° respecto al desplazamiento de 5 m. ¿Cuál es el trabajo?",
         "f": "W = F · d · cos(θ)", "o": ["300 J", "150 J", "259.8 J", "75 J"], "c": 1,
         "e": "W = 60 × 5 × cos(60°) = 60 × 5 × 0.5 = 150 J. Solo la componente de la fuerza paralela al desplazamiento hace trabajo."},
        {"t": "Un resorte tiene k = 500 N/m. ¿Trabajo al comprimirlo 0.2 m desde su posición natural?",
         "f": "W = ½ k x²", "o": ["100 J", "10 J", "50 J", "0.02 J"], "c": 1,
         "e": "W = ½ × 500 × (0.2)² = ½ × 500 × 0.04 = 10 J. La fuerza del resorte es variable, por eso se usa ½kx²."},
        {"t": "Una máquina realiza 3000 J de trabajo en 60 s. ¿Cuál es su potencia?",
         "f": "P = W / t", "o": ["180 000 W", "0.02 W", "50 W", "3060 W"], "c": 2,
         "e": "P = W/t = 3000/60 = 50 W. La potencia mide qué tan rápido se realiza trabajo; su unidad es el watt (W = J/s)."},
        {"t": "¿Cuál es el trabajo realizado por la fuerza normal sobre un objeto que se desliza horizontalmente?",
         "f": None, "o": ["Igual al peso × distancia", "Positivo", "Cero", "Negativo"], "c": 2,
         "e": "La fuerza normal es perpendicular al desplazamiento. Como cos(90°) = 0, el trabajo de la normal es siempre cero."},
    ],
    "Energía y conservación": [
        {"t": "Un objeto de 4 kg cae libremente 10 m. ¿Cuánta energía potencial pierde? (g = 10 m/s²)",
         "f": "Ep = m · g · h", "o": ["40 J", "4 J", "400 J", "14 J"], "c": 2,
         "e": "ΔEp = m × g × h = 4 × 10 × 10 = 400 J. Esa energía se transforma en energía cinética durante la caída."},
        {"t": "Un objeto de 2 kg se mueve a 10 m/s. ¿Cuál es su energía cinética?",
         "f": "Ec = ½ m v²", "o": ["10 J", "20 J", "100 J", "200 J"], "c": 2,
         "e": "Ec = ½ × 2 × 10² = 100 J. La energía cinética depende del cuadrado de la velocidad."},
        {"t": "Un bloque cae sin fricción desde h = 5 m. ¿Cuál es su velocidad al llegar al suelo? (g = 10 m/s²)",
         "f": "v = √(2gh)", "o": ["5 m/s", "10 m/s", "7.07 m/s", "50 m/s"], "c": 1,
         "e": "v = √(2 × 10 × 5) = √100 = 10 m/s. Sin fricción, toda la energía potencial se convierte en cinética."},
        {"t": "¿Cuál de las siguientes fuerzas NO es conservativa?",
         "f": None, "o": ["Gravitatoria", "Elástica (resorte)", "Fricción cinética", "Eléctrica"], "c": 2,
         "e": "La fricción cinética disipa energía como calor, por eso no es conservativa. Las fuerzas conservativas tienen trabajo independiente de la trayectoria."},
        {"t": "Un sistema conservativo tiene Ec = 80 J y Ep = 20 J. Si Ep aumenta a 50 J, ¿cuánto vale Ec?",
         "f": "Em = Ec + Ep = constante", "o": ["80 J", "130 J", "50 J", "30 J"], "c": 2,
         "e": "Em = 80 + 20 = 100 J (constante). Si Ep = 50 J → Ec = 100 - 50 = 50 J. La energía mecánica total se conserva."},
    ],
}

# ============================================================
# ESTADO DE SESIÓN
# ============================================================
def init_state():
    defaults = {
        "topic": TOPICS[0],
        "q_idx": 0,
        "xp": 0,
        "lives": 5,
        "rounds": 0,
        "round_correct": 0,
        "round_xp": 0,
        "answered": False,
        "selected_option": None,
        "current_q": None,
        "ai_question_active": False,
        "chat_history": [],
        "last_wrong_q": None,
        "show_results": False,
        "topic_xp": {t: 0 for t in TOPICS},
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v
    if st.session_state.current_q is None:
        st.session_state.current_q = QUESTIONS[st.session_state.topic][0]

init_state()

# ============================================================
# PANTALLA DE BIENVENIDA — pide API key
# ============================================================
if not st.session_state.gemini_api_key:
    st.markdown("## ⚡ PhysiQ")
    st.caption("Aprende física universitaria como si fuera un juego, con un tutor de IA")
    st.divider()
    st.markdown("### 🔑 Ingresa tu API key de Gemini para empezar")
    st.write(
        "PhysiQ usa Google Gemini como tutor de IA. Necesitas tu propia API key gratuita. "
        "No se guarda en ningún servidor ni se comparte — solo existe durante tu sesión."
    )
    with st.expander("¿No tienes una API key? Consíguela gratis en 1 minuto"):
        st.markdown("""
1. Ve a **[aistudio.google.com](https://aistudio.google.com)** e inicia sesión con tu cuenta de Google
2. En el menú izquierdo, clic en **"Get API key"**
3. Clic en **"Create API key"**
4. Copia la clave (empieza con `AIza...`) y pégala abajo

No necesitas tarjeta de crédito. El plan gratuito es más que suficiente.
        """)
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
                    st.error(f"API key no válida o error de conexión: {e}")
    st.stop()

# ============================================================
# FUNCIONES DE IA
# ============================================================
def generar_pregunta_ia(topic):
    prompt = f"""Eres un generador de preguntas de física universitaria básica.
Genera UNA pregunta de examen sobre el tema: {topic}.
Responde SOLO con JSON válido sin backticks ni texto extra:
{{"t":"pregunta","f":"formula o null","o":["A","B","C","D"],"c":0,"e":"explicacion 2-3 oraciones"}}
El campo "c" es el índice (0-3) de la opción correcta. Usa valores numéricos concretos. Responde en español."""
    try:
        response = model.generate_content(prompt)
        raw = response.text.strip().replace("```json", "").replace("```", "").strip()
        return json.loads(raw)
    except Exception as e:
        st.error(f"No se pudo generar la pregunta: {e}")
        return None

def preguntar_tutor(mensaje, topic, pregunta_actual, wrong_q=None):
    ctx_error = f'El estudiante falló esta pregunta: "{wrong_q["t"]}". Ayúdalo a entenderla sin revelar la respuesta directamente.' if wrong_q else ""
    prompt = f"""Eres PhysiQ, tutor de física universitaria básica. Amigable y conciso.
Tema actual: {topic}. Pregunta activa: "{pregunta_actual['t']}"
{ctx_error}
Responde en español, máximo 3-4 oraciones, con analogías cotidianas cuando ayude.
Pregunta del estudiante: {mensaje}"""
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error al conectar con el tutor: {e}"

# ============================================================
# ESTILOS
# ============================================================
st.markdown("""
<style>
.stApp { max-width: 720px; margin: 0 auto; }
.stat-box { text-align: center; padding: 8px 4px; border-radius: 10px;
            background: #f0f2f6; font-size: 14px; }
.topic-badge { display: inline-block; padding: 3px 12px; background: #E6F1FB;
               color: #0C447C; border-radius: 20px; font-size: 13px;
               font-weight: 600; margin-bottom: 8px; }
.formula-box { background: #f0f2f6; padding: 10px 14px; border-radius: 8px;
               text-align: center; font-family: monospace; margin: 8px 0; font-size: 14px; }
.result-card { background: #f0f2f6; padding: 12px; border-radius: 10px; text-align: center; }
.result-num { font-size: 22px; font-weight: 600; margin-bottom: 2px; }
.result-lbl { font-size: 12px; color: #666; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# HEADER
# ============================================================
st.markdown("## ⚡ PhysiQ")
st.caption("Física universitaria · Tutor con IA")

col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
with col1:
    st.markdown(f"<div class='stat-box'>⭐ <b>{st.session_state.xp}</b> XP</div>", unsafe_allow_html=True)
with col2:
    st.markdown(f"<div class='stat-box'>❤️ <b>{st.session_state.lives}</b> vidas</div>", unsafe_allow_html=True)
with col3:
    st.markdown(f"<div class='stat-box'>🔄 <b>{st.session_state.rounds}</b> rondas</div>", unsafe_allow_html=True)
with col4:
    if st.button("🔑 Cambiar key", use_container_width=True):
        st.session_state.gemini_api_key = None
        st.rerun()

st.divider()

# ============================================================
# SELECTOR DE TEMA
# ============================================================
st.markdown("**Elige un tema:**")
topic_choice = st.radio("Tema", TOPICS, horizontal=False, label_visibility="collapsed",
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
# PANTALLA DE RESULTADOS
# ============================================================
if st.session_state.show_results:
    total = len(QUESTIONS[st.session_state.topic])
    pct = st.session_state.round_correct / total
    if pct == 1.0:
        st.success("🎉 ¡Perfecto! Respondiste todas correctamente")
    elif pct >= 0.6:
        st.success("👍 ¡Buen trabajo!")
    else:
        st.info("📘 Sigue practicando, vas mejorando")

    r1, r2, r3 = st.columns(3)
    with r1:
        st.markdown(f"<div class='result-card'><div class='result-num' style='color:#1D9E75'>{st.session_state.round_correct}/{total}</div><div class='result-lbl'>Correctas</div></div>", unsafe_allow_html=True)
    with r2:
        st.markdown(f"<div class='result-card'><div class='result-num' style='color:#BA7517'>+{st.session_state.round_xp}</div><div class='result-lbl'>XP ganados</div></div>", unsafe_allow_html=True)
    with r3:
        st.markdown(f"<div class='result-card'><div class='result-num' style='color:#185FA5'>{st.session_state.rounds}</div><div class='result-lbl'>Rondas totales</div></div>", unsafe_allow_html=True)

    st.markdown("")
    if st.button("Jugar otra ronda", type="primary", use_container_width=True):
        st.session_state.q_idx = 0
        st.session_state.round_correct = 0
        st.session_state.round_xp = 0
        st.session_state.answered = False
        st.session_state.ai_question_active = False
        st.session_state.show_results = False
        st.session_state.current_q = QUESTIONS[st.session_state.topic][0]
        st.rerun()

else:
    # ============================================================
    # ÁREA DE PREGUNTA
    # ============================================================
    total_qs = len(QUESTIONS[st.session_state.topic])
    st.markdown(f"<span class='topic-badge'>{st.session_state.topic}</span>", unsafe_allow_html=True)
    st.progress(st.session_state.q_idx / total_qs,
                text=f"Pregunta {st.session_state.q_idx + 1} de {total_qs}")

    if st.button("✨ Generar pregunta con IA"):
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
        choice = st.radio("Opciones", q["o"], index=None,
                          label_visibility="collapsed",
                          key=f"radio_{st.session_state.q_idx}_{st.session_state.ai_question_active}")
        if st.button("Responder", type="primary", disabled=(choice is None)):
            sel = q["o"].index(choice)
            st.session_state.selected_option = sel
            st.session_state.answered = True
            if sel == q["c"]:
                st.session_state.xp += 20
                st.session_state.round_correct += 1
                st.session_state.round_xp += 20
                st.session_state.topic_xp[st.session_state.topic] = min(
                    100, st.session_state.topic_xp[st.session_state.topic] + 20)
                st.session_state.last_wrong_q = None
            else:
                st.session_state.lives = max(0, st.session_state.lives - 1)
                st.session_state.last_wrong_q = q
            st.rerun()
    else:
        if st.session_state.selected_option == q["c"]:
            st.success(f"✅ **¡Correcto!** {q['e']}")
        else:
            correcta = q["o"][q["c"]]
            st.error(f"❌ **Incorrecto.** La respuesta correcta era: *{correcta}*\n\n{q['e']}")

        if st.button("Siguiente →", type="primary", use_container_width=True):
            st.session_state.q_idx += 1
            st.session_state.answered = False
            st.session_state.selected_option = None
            st.session_state.ai_question_active = False
            if st.session_state.q_idx >= total_qs:
                st.session_state.rounds += 1
                st.session_state.show_results = True
            else:
                st.session_state.current_q = QUESTIONS[st.session_state.topic][st.session_state.q_idx]
            st.rerun()

st.divider()

# ============================================================
# TUTOR IA — CHAT
# ============================================================
st.markdown("### 🤖 Tutor IA")
st.caption("Pregúntame cualquier duda del tema o pídeme que explique por qué fallaste")

for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

user_msg = st.chat_input("Escribe tu duda de física...")
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
