import os
from dotenv import load_dotenv
from openai import OpenAI
from models import ProsecutorCase, DefenseCase, FinalVerdict, DoubleTrialVerdict

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL_NAME = "gpt-4o-mini"

PRESET_PROMPTS = {
    "General Fact-Check & Reasoning": {
        "pros": "Scrutinize factual accuracy, hallucination, logical fallacies, ungrounded claims, and filler fluff.",
        "def": "Advocate for conceptual clarity, directness, logical structure, and practical usefulness.",
        "judge": "Weigh factual correctness first, followed by brevity and utility."
    },
    "Code Review Tribunal": {
        "pros": "Aggressively inspect both codes for edge cases, bugs, poor time/space complexity, lack of input validation, and bad practices.",
        "def": "Highlight modularity, clean readability, idiomatic syntax, correct logic, and maintainability.",
        "judge": "Prioritize bug-free execution, edge case safety, and code efficiency over superficial styling."
    },
    "Resume & Career Screener": {
        "pros": "Expose vague buzzwords, lack of quantifiable metrics, passive voice, over-promising, and disorganized structure.",
        "def": "Champion measurable business impact, action verbs, clear role relevance, and punchy readability.",
        "judge": "Rule based on hiring manager impact: evidence of skill mastery, clarity, and metric-backed results."
    },
    "Creative Writing & Pitch": {
        "pros": "Attack cliches, boring hooks, robotic AI tone, poor pacing, and weak emotional resonance.",
        "def": "Celebrate compelling hooks, original imagery, engaging rhythm, audience empathy, and vivid narrative voice.",
        "judge": "Judge based on emotional impact, memorability, flow, and persuasion."
    }
}

def run_prosecutor(prompt: str, context: str, response_a: str, response_b: str, preset: str) -> ProsecutorCase:
    persona_rule = PRESET_PROMPTS.get(preset, PRESET_PROMPTS["General Fact-Check & Reasoning"])["pros"]
    system_prompt = (
        f"You are the Lead Prosecutor in an AI Courtroom Battle. Specific tribunal directive: {persona_rule} "
        "Critique BOTH Model A and Model B ruthlessly."
    )
    user_prompt = f"""
    [ORIGINAL PROMPT]: {prompt}
    [CONTEXT / REFERENCE]: {context or 'None provided.'}

    [CANDIDATE MODEL A]:
    {response_a}

    [CANDIDATE MODEL B]:
    {response_b}
    """
    completion = client.beta.chat.completions.parse(
        model=MODEL_NAME,
        temperature=0.0,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        response_format=ProsecutorCase
    )
    return completion.choices[0].message.parsed

def run_defense(prompt: str, context: str, response_a: str, response_b: str, preset: str) -> DefenseCase:
    persona_rule = PRESET_PROMPTS.get(preset, PRESET_PROMPTS["General Fact-Check & Reasoning"])["def"]
    system_prompt = (
        f"You are the Defense Counsel in an AI Courtroom Battle. Specific tribunal directive: {persona_rule} "
        "Advocate for BOTH Model A and Model B, noting their strongest merits."
    )
    user_prompt = f"""
    [ORIGINAL PROMPT]: {prompt}
    [CONTEXT / REFERENCE]: {context or 'None provided.'}

    [CANDIDATE MODEL A]:
    {response_a}

    [CANDIDATE MODEL B]:
    {response_b}
    """
    completion = client.beta.chat.completions.parse(
        model=MODEL_NAME,
        temperature=0.0,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        response_format=DefenseCase
    )
    return completion.choices[0].message.parsed

def run_chief_judge(prompt: str, context: str, response_a: str, response_b: str,
                    prosecution: ProsecutorCase, defense: DefenseCase, preset: str) -> FinalVerdict:
    persona_rule = PRESET_PROMPTS.get(preset, PRESET_PROMPTS["General Fact-Check & Reasoning"])["judge"]
    system_prompt = (
        f"You are the Chief Presiding Judge. Specific tribunal directive: {persona_rule} "
        "Review arguments from Prosecution and Defense, score each candidate (1-10), pick a winner, and explain why."
    )
    user_prompt = f"""
    [ORIGINAL PROMPT]: {prompt}
    [CONTEXT / REFERENCE]: {context or 'None provided.'}

    [CANDIDATE MODEL A]: {response_a}
    [CANDIDATE MODEL B]: {response_b}

    [PROSECUTION INDICTMENT]:
    - Model A Flaws: {prosecution.flaws_model_a}
    - Model B Flaws: {prosecution.flaws_model_b}
    - Summary: {prosecution.prosecution_summary}

    [DEFENSE PRAISE]:
    - Model A Merits: {defense.merits_model_a}
    - Model B Merits: {defense.merits_model_b}
    - Summary: {defense.defense_summary}
    """
    completion = client.beta.chat.completions.parse(
        model=MODEL_NAME,
        temperature=0.0,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        response_format=FinalVerdict
    )
    return completion.choices[0].message.parsed

def execute_full_trial(prompt: str, context: str, response_a: str, response_b: str, preset: str, anti_bias: bool = False):
    # Pass 1: Standard Order (A then B)
    pros1 = run_prosecutor(prompt, context, response_a, response_b, preset)
    def1 = run_defense(prompt, context, response_a, response_b, preset)
    verdict1 = run_chief_judge(prompt, context, response_a, response_b, pros1, def1, preset)

    if not anti_bias:
        return DoubleTrialVerdict(
            pass_1_verdict=verdict1,
            pass_2_verdict=None,
            consensus_winner=verdict1.winner,
            bias_detected=False,
            bias_explanation="Anti-bias mode was not enabled. Single-pass evaluation used."
        ), pros1, def1

    # Pass 2: Position Swap (B fed as First, A fed as Second)
    pros2 = run_prosecutor(prompt, context, response_b, response_a, preset)
    def2 = run_defense(prompt, context, response_b, response_a, preset)
    verdict2_raw = run_chief_judge(prompt, context, response_b, response_a, pros2, def2, preset)

    # In pass 2: Model A was in position "MODEL B", and Model B was in position "MODEL A"
    pass2_winner_mapped = (
        "MODEL B" if verdict2_raw.winner == "MODEL A"
        else "MODEL A" if verdict2_raw.winner == "MODEL B"
        else "SPLIT DECISION (TIE)"
    )

    if verdict1.winner == pass2_winner_mapped:
        consensus = verdict1.winner
        bias_detected = False
        explanation = f"Solid consensus: {consensus} won decisively regardless of presentation order."
    else:
        consensus = "SPLIT DECISION (POSITION BIAS DETECTED)"
        bias_detected = True
        explanation = (
            f"Pass 1 favored {verdict1.winner}, but when order was swapped, Pass 2 favored {pass2_winner_mapped}. "
            "The decision was influenced by the order in which responses were presented."
        )

    return DoubleTrialVerdict(
        pass_1_verdict=verdict1,
        pass_2_verdict=verdict2_raw,
        consensus_winner=consensus,
        bias_detected=bias_detected,
        bias_explanation=explanation
    ), pros1, def1