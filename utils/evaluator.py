import os
from anthropic import Anthropic
from typing import Dict, List
import json
from datetime import datetime
import uuid
from dotenv import load_dotenv

from .data_model import (
    Evaluation,
    CriterionScore,
    MARKETING_COPY_CRITERIA,
    BILINGUAL_COMPLIANCE_CRITERIA,
    get_decision
)

# Load environment variables
load_dotenv()

class ContentEvaluator:
    """Evaluates content using Claude as a judge"""
    
    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
        self.client = Anthropic(api_key=api_key)
        self.model = "claude-sonnet-4-20250514"
    
    def evaluate_content(
        self,
        content: str,
        use_case: str,
        context: str = ""
    ) -> Evaluation:
        """
        Evaluate content using Claude API
        
        Args:
            content: The text content to evaluate
            use_case: Either "marketing_copy" or "bilingual_compliance"
            context: Additional context (campaign type, product category, etc.)
        
        Returns:
            Evaluation object with scores and decision
        """
        # Get criteria based on use case
        criteria = self._get_criteria(use_case)
        
        # Build the evaluation prompt
        prompt = self._build_evaluation_prompt(content, use_case, context, criteria)
        
        # Call Claude API
        response = self.client.messages.create(
            model=self.model,
            max_tokens=2000,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        
        # Parse the response
        ai_scores = self._parse_claude_response(response.content[0].text, criteria)
        
        # Calculate overall score (weighted average)
        overall_score = self._calculate_overall_score(ai_scores, criteria)
        
        # Determine decision
        decision = get_decision(overall_score)
        
        # Create Evaluation object
        evaluation = Evaluation(
            id=str(uuid.uuid4()),
            timestamp=datetime.now().isoformat(),
            use_case=use_case,
            content=content,
            context=context,
            ai_scores=ai_scores,
            ai_overall_score=overall_score,
            ai_decision=decision
        )
        
        return evaluation
    
    def _get_criteria(self, use_case: str) -> Dict:
        """Get evaluation criteria for the use case"""
        if use_case == "marketing_copy":
            return MARKETING_COPY_CRITERIA
        elif use_case == "bilingual_compliance":
            return BILINGUAL_COMPLIANCE_CRITERIA
        else:
            raise ValueError(f"Unknown use case: {use_case}")
    
    def _build_evaluation_prompt(
        self,
        content: str,
        use_case: str,
        context: str,
        criteria: Dict
    ) -> str:
        """Build the evaluation prompt for Claude"""
        
        if use_case == "marketing_copy":
            use_case_description = """
You are evaluating MULTILINGUAL MARKETING COPY that was created directly in the target language 
(not translated from English). The goal is to assess whether this copy is culturally appropriate, 
persuasive, and effective for the target audience.
"""
        else:  # bilingual_compliance
            use_case_description = """
You are evaluating BILINGUAL PRODUCT DOCUMENTATION (user manuals, packaging, labels) to ensure 
both languages are present and the translation quality meets regulatory and usability standards.
"""
        
        # Build criteria description
        criteria_desc = "\n".join([
            f"{i+1}. **{info['name']}** (Weight: {int(info['weight']*100)}%): {info['description']}"
            for i, (key, info) in enumerate(criteria.items())
        ])
        
        prompt = f"""You are an expert content quality evaluator specializing in multilingual content assessment.

{use_case_description}

**CONTENT TO EVALUATE:**
{content}

**CONTEXT:**
{context if context else "No additional context provided"}

**EVALUATION CRITERIA:**
{criteria_desc}

**INSTRUCTIONS:**
For each criterion above, provide:
1. A score from 1-5 (where 1 = Poor, 2 = Below Average, 3 = Average, 4 = Good, 5 = Excellent)
2. A brief explanation (2-3 sentences) justifying the score

**OUTPUT FORMAT:**
You must respond ONLY with valid JSON in exactly this format (no other text before or after):

{{
  "criterion_key_1": {{
    "score": X,
    "explanation": "Your explanation here"
  }},
  "criterion_key_2": {{
    "score": X,
    "explanation": "Your explanation here"
  }},
  ...
}}

The criterion keys must be exactly: {', '.join(criteria.keys())}

Return ONLY the JSON object, no markdown formatting, no additional text.
"""
        return prompt
    
    def _parse_claude_response(self, response_text: str, criteria: Dict) -> Dict[str, CriterionScore]:
        """Parse Claude's JSON response into CriterionScore objects"""
        try:
            # Remove any markdown code blocks if present
            response_text = response_text.strip()
            if response_text.startswith("```"):
                # Remove ```json and ``` markers
                lines = response_text.split("\n")
                response_text = "\n".join(lines[1:-1])
            
            # Parse JSON
            scores_dict = json.loads(response_text)
            
            # Convert to CriterionScore objects
            ai_scores = {}
            for key, info in criteria.items():
                if key in scores_dict:
                    ai_scores[key] = CriterionScore(
                        score=float(scores_dict[key]["score"]),
                        explanation=scores_dict[key]["explanation"],
                        weight=info["weight"]
                    )
                else:
                    # Fallback if criterion missing
                    ai_scores[key] = CriterionScore(
                        score=3.0,
                        explanation="Score not provided by evaluator",
                        weight=info["weight"]
                    )
            
            return ai_scores
            
        except Exception as e:
            print(f"Error parsing Claude response: {e}")
            print(f"Response text: {response_text}")
            # Return default scores on error
            return {
                key: CriterionScore(score=3.0, explanation="Error parsing response", weight=info["weight"])
                for key, info in criteria.items()
            }
    
    def _calculate_overall_score(self, ai_scores: Dict[str, CriterionScore], criteria: Dict) -> float:
        """Calculate weighted average of all criterion scores"""
        total_score = 0.0
        total_weight = 0.0
        
        for key, criterion_score in ai_scores.items():
            total_score += criterion_score.score * criterion_score.weight
            total_weight += criterion_score.weight
        
        # Normalize to 1-5 scale
        if total_weight > 0:
            return round(total_score / total_weight, 2)
        return 3.0  # Default if weights are invalid