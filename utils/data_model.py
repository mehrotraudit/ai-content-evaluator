from dataclasses import dataclass, asdict
from typing import Dict, List, Optional
from datetime import datetime
import json

@dataclass
class CriterionScore:
    """Individual criterion evaluation"""
    score: float  # 1-5
    explanation: str
    weight: float  # percentage weight for this criterion

@dataclass
class Evaluation:
    """Complete evaluation of a piece of content"""
    id: str  # unique identifier
    timestamp: str  # ISO format datetime
    use_case: str  # "marketing_copy" or "bilingual_compliance"
    content: str  # the content being evaluated
    context: str  # additional context provided
    
    # AI Judge scores
    ai_scores: Dict[str, CriterionScore]  # criterion_name -> score
    ai_overall_score: float  # weighted average
    ai_decision: str  # "auto_pass" | "auto_fail" | "human_review"
    
    # Human Judge scores (optional)
    human_scores: Optional[Dict[str, CriterionScore]] = None
    human_overall_score: Optional[float] = None
    human_decision: Optional[str] = None
    human_feedback: Optional[str] = None
    
    def to_dict(self):
        """Convert to dictionary for JSON storage"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create from dictionary"""
        # Convert nested CriterionScore dicts back to objects
        if 'ai_scores' in data:
            data['ai_scores'] = {
                k: CriterionScore(**v) if isinstance(v, dict) else v
                for k, v in data['ai_scores'].items()
            }
        if data.get('human_scores'):
            data['human_scores'] = {
                k: CriterionScore(**v) if isinstance(v, dict) else v
                for k, v in data['human_scores'].items()
            }
        return cls(**data)

# Evaluation Criteria Definitions

MARKETING_COPY_CRITERIA = {
    "cultural_appropriateness": {
        "name": "Cultural Appropriateness",
        "description": "Idioms, cultural references, and tone appropriate for target culture",
        "weight": 0.30
    },
    "persuasiveness": {
        "name": "Persuasiveness",
        "description": "Likely to drive action and conversion",
        "weight": 0.25
    },
    "brand_voice": {
        "name": "Brand Voice Consistency",
        "description": "Matches Amazon's brand voice in the target language",
        "weight": 0.20
    },
    "grammar_fluency": {
        "name": "Grammar & Fluency",
        "description": "Natural, error-free language",
        "weight": 0.15
    },
    "semantic_accuracy": {
        "name": "Semantic Accuracy",
        "description": "Conveys the intended message accurately",
        "weight": 0.10
    }
}

BILINGUAL_COMPLIANCE_CRITERIA = {
    "completeness": {
        "name": "Completeness",
        "description": "Both languages present, all content translated",
        "weight": 0.25
    },
    "accuracy": {
        "name": "Translation Accuracy",
        "description": "Meaning preserved, no mistranslations",
        "weight": 0.25
    },
    "fluency": {
        "name": "Fluency",
        "description": "Natural and readable in target language",
        "weight": 0.20
    },
    "terminology": {
        "name": "Terminology Consistency",
        "description": "Technical/product terms used correctly",
        "weight": 0.15
    },
    "regulatory_compliance": {
        "name": "Regulatory Compliance",
        "description": "Safety warnings and legal text properly translated",
        "weight": 0.15
    }
}

# Decision thresholds
AUTO_PASS_THRESHOLD = 4.0
AUTO_FAIL_THRESHOLD = 2.5

def get_decision(overall_score: float) -> str:
    """Determine auto-pass/fail/review based on score"""
    if overall_score >= AUTO_PASS_THRESHOLD:
        return "auto_pass"
    elif overall_score < AUTO_FAIL_THRESHOLD:
        return "auto_fail"
    else:
        return "human_review"