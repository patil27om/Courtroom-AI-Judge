import io
import streamlit as st
from datetime import datetime

# ReportLab Imports
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# Local Agent Imports
from agents import execute_full_trial, PRESET_PROMPTS


# --- PDF GENERATOR FUNCTION ---
def create_court_transcript_pdf(trial_data: dict) -> io.BytesIO:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=45,
        leftMargin=45,
        topMargin=45,
        bottomMargin=45
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#1E293B'),
        alignment=1
    )

    meta_style = ParagraphStyle(
        'MetaText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#64748B'),
        alignment=1
    )

    h2_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#0F172A'),
        spaceBefore=10,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor('#334155')
    )

    bullet_style = ParagraphStyle(
        'BulletItem',
        parent=body_style,
        leftIndent=14,
        firstLineIndent=-10
    )

    verdict_val_style = ParagraphStyle(
        'VerdictVal',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=colors.HexColor('#047857') if not trial_data['verdict'].get('bias_detected') else colors.HexColor('#B45309')
    )

    elements = []

    # Title & Metadata
    elements.append(Paragraph("OFFICIAL AI COURT TRANSCRIPT", title_style))
    elements.append(Spacer(1, 4))
    elements.append(Paragraph(f"TRIBUNAL: {trial_data.get('preset', 'General').upper()} | SESSION DATE: {trial_data.get('timestamp')}", meta_style))
    elements.append(Spacer(1, 10))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#CBD5E1'), spaceAfter=14))

    # Ruling Banner Table
    v = trial_data['verdict']
    p1 = v.get('pass_1_verdict', {})

    ruling_data = [
        [
            Paragraph("<b>OFFICIAL CHAMPION:</b>", body_style),
            Paragraph(f"{v.get('consensus_winner', 'N/A')}", verdict_val_style),
            Paragraph("<b>POSITION BIAS:</b>", body_style),
            Paragraph("DETECTED" if v.get('bias_detected') else "BIAS-FREE", body_style)
        ],
        [
            Paragraph("<b>MODEL A SCORE:</b>", body_style),
            Paragraph(f"{p1.get('score_model_a', 0)} / 10", body_style),
            Paragraph("<b>MODEL B SCORE:</b>", body_style),
            Paragraph(f"{p1.get('score_model_b', 0)} / 10", body_style)
        ]
    ]

    ruling_table = Table(ruling_data, colWidths=[110, 150, 110, 150])
    ruling_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#E2E8F0')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(ruling_table)
    elements.append(Spacer(1, 12))

    # Judicial Determination
    elements.append(Paragraph("JUDICIAL DETERMINATION & RATIONALE", h2_style))
    elements.append(Paragraph(f"<b>Core Deciding Factor:</b> {p1.get('deciding_factor', '')}", body_style))
    elements.append(Spacer(1, 4))
    elements.append(Paragraph(f"<b>Comparative Analysis:</b> {p1.get('cross_examination_analysis', '')}", body_style))
    elements.append(Spacer(1, 4))
    elements.append(Paragraph(f"<b>Remedy Prescribed for Losing Party:</b> {p1.get('remedy_for_loser', '')}", body_style))
    elements.append(Spacer(1, 12))

    # Proceedings
    pros = trial_data.get('prosecution', {})
    defense = trial_data.get('defense', {})

    elements.append(Paragraph("CROSS-EXAMINATION PROCEEDINGS", h2_style))

    elements.append(Paragraph("<b>1. Prosecution Indictment (Flaws & Hallucinations)</b>", body_style))
    for flaw in pros.get('flaws_model_a', []):
        elements.append(Paragraph(f"• <b>[Model A]</b> {flaw}", bullet_style))
    for flaw in pros.get('flaws_model_b', []):
        elements.append(Paragraph(f"• <b>[Model B]</b> {flaw}", bullet_style))
    elements.append(Spacer(1, 4))
    elements.append(Paragraph(f"<i>Prosecutor's Statement:</i> {pros.get('prosecution_summary', '')}", body_style))
    elements.append(Spacer(1, 8))

    elements.append(Paragraph("<b>2. Defense Advocacy (Strengths & Utility)</b>", body_style))
    for merit in defense.get('merits_model_a', []):
        elements.append(Paragraph(f"• <b>[Model A]</b> {merit}", bullet_style))
    for merit in defense.get('merits_model_b', []):
        elements.append(Paragraph(f"• <b>[Model B]</b> {merit}", bullet_style))
    elements.append(Spacer(1, 4))
    elements.append(Paragraph(f"<i>Defense Counsel's Statement:</i> {defense.get('defense_summary', '')}", body_style))
    elements.append(Spacer(1, 12))

    # Exhibits
    elements.append(Paragraph("EXHIBIT EVIDENCE RECORD", h2_style))
    elements.append(Paragraph(f"<b>Original Prompt:</b> {trial_data.get('prompt', '')}", body_style))
    elements.append(Spacer(1, 4))

    model_a_raw = trial_data.get('model_a', '').replace('\n', '<br/>')
    model_b_raw = trial_data.get('model_b', '').replace('\n', '<br/>')

    exhibit_data = [
        [Paragraph("<b>Candidate Model A Output</b>", body_style), Paragraph("<b>Candidate Model B Output</b>", body_style)],
        [Paragraph(model_a_raw, body_style), Paragraph(model_b_raw, body_style)]
    ]
    exhibit_table = Table(exhibit_data, colWidths=[260, 260])
    exhibit_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F1F5F9')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(exhibit_table)

    doc.build(elements)
    buffer.seek(0)
    return buffer


# --- STREAMLIT UI ---
st.set_page_config(page_title="AI Courtroom Arena", layout="wide")

st.title("⚖️ AI Courtroom Arena: Model vs Model Battle")
st.caption("Adversarial multi-agent evaluation pipeline with Anti-Bias Verification and Tribunal Presets.")

with st.sidebar:
    st.header("⚙️ Tribunal Configuration")

    preset_choice = st.selectbox(
        "Select Court Tribunal Preset",
        options=list(PRESET_PROMPTS.keys())
    )

    enable_anti_bias = st.toggle(
        "🛡️ Enable Anti-Bias Double-Trial",
        value=True,
        help="Runs an automated second trial with candidate orders swapped to ensure the decision is invariant to position bias."
    )

    st.markdown("---")
    st.header("📋 Case Evidence")

    default_prompt = "Explain quantum computing to a 10-year-old in two clear sentences."
    default_a = "Regular computers think in light switches that are either ON or OFF. Quantum computers use magic-like switches that can be ON, OFF, or both at the same time, which lets them solve giant puzzles super fast!"
    default_b = "Quantum computing utilizes quantum mechanical phenomena such as superposition and entanglement to execute operations exponentially faster than standard silicon processors on specific algorithms."

    if preset_choice == "Code Review Tribunal":
        default_prompt = "Write a Python function to check if a string is a palindrome."
        default_a = "def is_palindrome(s):\n    cleaned = ''.join(c.lower() for c in s if c.isalnum())\n    return cleaned == cleaned[::-1]"
        default_b = "def is_palindrome(s):\n    return s == s[::-1] # simple one liner"
    elif preset_choice == "Resume & Career Screener":
        default_prompt = "Summarize accomplishment as an engineering lead."
        default_a = "Led cross-functional team of 6 engineers to re-architect payments pipeline, reducing checkout latency by 42% and processing $12M/month."
        default_b = "Responsible for leading team members and handling various microservices and fixing bugs in the payment system with high dedication."
    elif preset_choice == "Creative Writing & Pitch":
        default_prompt = "Write an opening pitch line for an eco-friendly coffee mug."
        default_a = "The last cup you'll ever need—crafted from discarded husks to keep your brew hot and the planet cool."
        default_b = "We present an innovative, state-of-the-art sustainable beverage vessel designed to optimize user experience and environmental responsibility."

    input_prompt = st.text_area("User Prompt / Task", value=default_prompt, height=100)
    input_context = st.text_area("Ground Truth / Reference (Optional)", value="")

col1, col2 = st.columns(2)
with col1:
    st.subheader("🔵 Candidate Model A")
    model_a_text = st.text_area("Model A Output", height=180, value=default_a)

with col2:
    st.subheader("🟣 Candidate Model B")
    model_b_text = st.text_area("Model B Output", height=180, value=default_b)

start_trial = st.button("⚡ Convene Court & Judge Battle", type="primary", use_container_width=True)

if start_trial:
    if not model_a_text.strip() or not model_b_text.strip():
        st.error("Please supply responses for both Model A and Model B.")
    else:
        with st.spinner("The Court is cross-examining both candidates..."):
            trial_result, prosecution, defense = execute_full_trial(
                prompt=input_prompt,
                context=input_context,
                response_a=model_a_text,
                response_b=model_b_text,
                preset=preset_choice,
                anti_bias=enable_anti_bias
            )

            st.session_state["last_trial"] = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "preset": preset_choice,
                "anti_bias_enabled": enable_anti_bias,
                "prompt": input_prompt,
                "context": input_context,
                "model_a": model_a_text,
                "model_b": model_b_text,
                "prosecution": prosecution.model_dump(),
                "defense": defense.model_dump(),
                "verdict": trial_result.model_dump()
            }

if "last_trial" in st.session_state:
    data = st.session_state["last_trial"]
    verdict = data["verdict"]
    p1 = verdict["pass_1_verdict"]
    prosecution = data["prosecution"]
    defense = data["defense"]

    st.markdown("---")
    st.header("🏆 The Official Ruling")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Declared Winner", verdict["consensus_winner"])
    m2.metric("Model A Score", f"{p1['score_model_a']} / 10")
    m3.metric("Model B Score", f"{p1['score_model_b']} / 10")
    m4.metric("Bias Status", "⚠️ Bias Detected" if verdict["bias_detected"] else "✅ Bias-Free")

    if verdict["bias_detected"]:
        st.error(f"**Position Bias Warning:** {verdict['bias_explanation']}")
    else:
        st.success(f"**Verification:** {verdict['bias_explanation']}")

    st.info(f"**Deciding Factor:** {p1['deciding_factor']}")
    st.write(f"**Comparative Weighing:** {p1['cross_examination_analysis']}")
    st.warning(f"**Remedy for Loser:** {p1['remedy_for_loser']}")

    st.markdown("---")
    st.header("📜 Cross-Examination Proceedings")

    tab1, tab2 = st.tabs(["🔴 The Prosecution (Critique)", "🟢 The Defense (Merits)"])

    with tab1:
        pros_col_a, pros_col_b = st.columns(2)
        with pros_col_a:
            st.markdown("#### Criticisms: Model A")
            for flaw in prosecution["flaws_model_a"]:
                st.write(f"- {flaw}")
        with pros_col_b:
            st.markdown("#### Criticisms: Model B")
            for flaw in prosecution["flaws_model_b"]:
                st.write(f"- {flaw}")
        st.info(f"**Prosecution Closing Argument:** {prosecution['prosecution_summary']}")

    with tab2:
        def_col_a, def_col_b = st.columns(2)
        with def_col_a:
            st.markdown("#### Merits: Model A")
            for merit in defense["merits_model_a"]:
                st.write(f"- {merit}")
        with def_col_b:
            st.markdown("#### Merits: Model B")
            for merit in defense["merits_model_b"]:
                st.write(f"- {merit}")
        st.info(f"**Defense Closing Argument:** {defense['defense_summary']}")

    st.markdown("---")
    st.subheader("📥 Export Official Court Transcript")

    pdf_stream = create_court_transcript_pdf(data)

    st.download_button(
        label="⚖️ Download Official Court Transcript (PDF)",
        data=pdf_stream,
        file_name=f"court_transcript_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
        mime="application/pdf",
        type="primary",
        use_container_width=True
    )