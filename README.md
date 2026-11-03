# ⚖️ AI Courtroom Arena

An adversarial, multi-agent evaluation pipeline that pits language model outputs against each other in a courtroom trial. 

Instead of relying on a single judge prompt that blindly favors verbosity or polite formatting, **AI Courtroom Arena** splits evaluation into two opposing counsel personas (**The Prosecutor** and **The Defense**) before an impartial **Chief Presiding Judge** rules on the case. It also includes automated position-bias detection and generates official, publication-ready legal PDF transcripts.

---

## 🏛️ System Architecture

```text
                  [ User Prompt / Context ]
                             │
            ┌────────────────┴────────────────┐
            ▼                                 ▼
   [ Candidate Model A ]             [ Candidate Model B ]
            │                                 │
            └────────────────┬────────────────┘
                             ▼
              ┌─────────────────────────────┐
              │      Tribunal Router        │
              │  (Code, Career, Pitch, etc) │
              └──────────────┬──────────────┘
                             │
     ┌───────────────────────┴───────────────────────┐
     ▼                                               ▼
┌─────────────────────────┐             ┌─────────────────────────┐
│     The Prosecutor      │             │       The Defense       │
│  (Ruthless Critic AI)   │             │  (Dedicated Counsel AI) │
│ • Identifies Hallucina- │             │ • Highlights Strengths  │
│   tions & Missing Facts │             │ • Demonstrates Utility  │
│ • Flags Fluff & Flaws   │             │ • Argues Context Fit    │
└────────────┬────────────┘             └────────────┬────────────┘
             │                                       │
             └───────────────────┬───────────────────┘
                                 ▼
                 ┌───────────────────────────────┐
                 │      Chief Presiding Judge    │
                 │   (Structured Output Engine)  │
                 │ • Weighs Arguments            │
                 │ • Assigns Scores (1-10)       │
                 │ • Prescribes Loser's Remedy   │
                 └───────────────┬───────────────┘
                                 │
                 ┌───────────────┴───────────────┐
                 ▼                               ▼
     [ Anti-Bias Double Trial ]        [ ReportLab Engine ]
     (Flipped Order Verification)      (Official PDF Export)



🧠 Why This Architecture?
Standard LLM-as-a-Judge systems suffer from three well-documented failure modes:

Verbosity Bias: Models tend to award higher scores to longer answers, even if they are padded with fluff.

Blind Compliance: Single-agent evaluators often accept plausible-sounding hallucinations without aggressive verification.

Position Bias: Models frequently favor whichever candidate is passed first (Option A).

How We Solve It
Adversarial Triad: The Prosecutor is explicitly tasked with finding failure points, edge cases, and hallucinations. The Defense advocates for the clarity, practical utility, and accuracy of each submission.

Objective Arbitration: The Chief Judge evaluates the structured debate rather than just looking at the raw text, scoring both models out of 10 and specifying the deciding factor.

Anti-Bias Verification: When enabled, the system automatically executes a hidden secondary trial with the candidate order inverted ([B, A]). If the verdict flips, the transcript flags a Position Bias Alert instead of declaring a false victory.

Pydantic Structured Outputs: Every agent outputs strictly validated JSON through OpenAI's native parsing interface (client.beta.chat.completions.parse), eliminating regex or formatting failures.


Local Setup
Clone the repository:

Bash
git clone [https://github.com/](https://github.com/)<YOUR_GITHUB_USERNAME>/Courtroom-AI-Judge.git
cd Courtroom-AI-Judge
Create and activate a virtual environment:

Bash
# macOS / Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
.\venv\Scripts\activate
Install dependencies:

Bash
pip install -r requirements.txt
Configure environment variables:
Create a .env file in the root directory:

Code snippet
OPENAI_API_KEY=your_actual_openai_api_key_here
Run the Streamlit application:

Bash
streamlit run app.py


##Project Structure

Courtroom-AI-Judge/
│
├── .env                  # Local secret configuration (ignored by Git)
├── .gitignore            # Git exclusion rules
├── requirements.txt      # Core runtime dependencies
├── models.py             # Pydantic schemas for structured arguments & rulings
├── agents.py             # Persona prompts, anti-bias logic, and model orchestration
├── app.py                # Streamlit UI + ReportLab PDF generator
└── README.md             # Project documentation