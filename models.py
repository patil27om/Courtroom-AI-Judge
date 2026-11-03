from pydantic import BaseModel, Field
from typing import List, Literal, Optional

class ProsecutorCase(BaseModel):
    flaws_model_a: List[str] = Field(description="Hallucinations, fluff, or errors found in Model A.")
    flaws_model_b: List[str] = Field(description="Hallucinations, fluff, or errors found in Model B.")
    prosecution_summary: str = Field(description="Prosecutor's closing summary comparing the weaknesses of both.")

class DefenseCase(BaseModel):
    merits_model_a: List[str] = Field(description="Key strengths, accuracy, and utility of Model A.")
    merits_model_b: List[str] = Field(description="Key strengths, accuracy, and utility of Model B.")
    defense_summary: str = Field(description="Defense's closing summary advocating where each shines.")

class FinalVerdict(BaseModel):
    cross_examination_analysis: str = Field(
        description="Detailed comparative analysis weighing Model A vs Model B."
    )
    winner: Literal["MODEL A", "MODEL B", "SPLIT DECISION (TIE)"] = Field(
        description="The declared champion of the trial."
    )
    score_model_a: int = Field(ge=1, le=10, description="Rating for Model A from 1 to 10.")
    score_model_b: int = Field(ge=1, le=10, description="Rating for Model B from 1 to 10.")
    deciding_factor: str = Field(description="The primary reason why the winner clinched victory.")
    remedy_for_loser: str = Field(description="What the losing model would need to change to win next time.")

class DoubleTrialVerdict(BaseModel):
    pass_1_verdict: FinalVerdict
    pass_2_verdict: Optional[FinalVerdict] = None
    consensus_winner: str
    bias_detected: bool
    bias_explanation: str