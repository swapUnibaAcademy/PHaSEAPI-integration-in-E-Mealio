from typing import Optional


class HealthinessInfo:
    def __init__(self, score: str, qualitative: Optional[str] = None):
        self.score = score
        self.qualitative = qualitative

    def to_dict(self):
        return {
            "score": self.score,
            "qualitative": self.qualitative
        }

    def from_dict(data: dict):
        return HealthinessInfo(
            score=data.get("score", ""),
            qualitative=data.get("qualitative")
        )


class SustainabilityInfo:
    def __init__(self, score: str, qualitative: Optional[str] = None, CF: Optional[float] = None, WF: Optional[float] = None):
        self.score = score
        self.qualitative = qualitative
        self.CF = CF
        self.WF = WF

    def to_dict(self):
        return {
            "score": self.score,
            "qualitative": self.qualitative,
            "CF": self.CF,
            "WF": self.WF
        }

    def from_dict(data: dict):
        return SustainabilityInfo(
            score=data.get("score", ""),
            qualitative=data.get("qualitative"),
            CF=data.get("CF"),
            WF=data.get("WF")
        )
