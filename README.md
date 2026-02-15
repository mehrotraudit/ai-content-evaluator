# AI Content Quality Evaluator

A production-ready evaluation framework for assessing multilingual marketing content and bilingual compliance using LLM-as-judge patterns.

Built for Amazon's North America Languages Experience team to evaluate content quality at scale across 60M+ customers.

## Problem Statement

Traditional content quality metrics (click-through rates, engagement) can be gamed and don't measure actual quality. Manual review doesn't scale. This framework solves both problems by:

1. Using Claude AI as an automated quality judge
2. Implementing human-in-the-loop validation
3. Providing configurable, weighted evaluation criteria
4. Auto-triaging content (pass/fail/needs-review)

## Features

- **Two Use Cases**:
  - Marketing Copy (multilingual content creation)
  - Bilingual Compliance (translation quality for regulatory requirements)

- **LLM-as-Judge Pattern**: Uses Claude Sonnet 4 to evaluate content on 5 configurable criteria

- **Weighted Scoring**: Business-driven weights (e.g., Cultural Appropriateness: 30%, Persuasiveness: 25%)

- **Auto-Triage Logic**:
  - Auto-Pass (≥4.0): Ship it
  - Human Review (2.5-4.0): Needs expert judgment
  - Auto-Fail (<2.5): Major issues

- **Human-in-the-Loop**: Compare AI judgments vs human ratings to measure agreement

- **Interactive Web App**: Built with Streamlit
  - Evaluate content tab
  - Review history with trend analysis
  - Educational content for PMs

## Tech Stack

- **Backend**: Python 3.9, Anthropic Claude API
- **Frontend**: Streamlit
- **Data Model**: Dataclasses with JSON serialization
- **Deployment**: Local (Streamlit Cloud ready)

## Installation
```bash
# Clone the repository
git clone https://github.com/mehrotraudit/ai-content-evaluator.git
cd ai-content-evaluator

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
echo "ANTHROPIC_API_KEY=your-api-key-here" > .env
```

## Usage
```bash
# Run the app
./run.sh

# Or manually:
streamlit run app.py
```

## Evaluation Criteria

### Marketing Copy
1. **Cultural Appropriateness** (30%) - Idioms, cultural references, tone
2. **Persuasiveness** (25%) - Drives action and conversion
3. **Brand Voice** (20%) - Matches Amazon's brand
4. **Grammar & Fluency** (15%) - Natural, error-free
5. **Semantic Accuracy** (10%) - Conveys intended message

### Bilingual Compliance
1. **Completeness** (25%) - Both languages present
2. **Translation Accuracy** (25%) - Meaning preserved
3. **Fluency** (20%) - Natural and readable
4. **Terminology Consistency** (15%) - Technical terms correct
5. **Regulatory Compliance** (15%) - Safety warnings properly translated

## Project Structure
```
ai-content-evaluator/
├── app.py                 # Streamlit web interface
├── utils/
│   ├── evaluator.py      # Claude API integration & evaluation logic
│   └── data_model.py     # Data structures and criteria definitions
├── .env                   # API keys (not committed)
├── requirements.txt       # Python dependencies
└── README.md
```

## Results & Impact

- Evaluates content in ~5-10 seconds (vs hours for manual review)
- Configurable criteria aligned with business priorities
- Human-AI agreement tracking for continuous improvement
- Scales to thousands of evaluations per day

## Future Enhancements

- [ ] File upload support (PDF, DOCX)
- [ ] Batch evaluation (100s of items at once)
- [ ] Persistent database storage
- [ ] Quality trend visualization over time
- [ ] API endpoint for programmatic access
- [ ] Multi-language UI

## Author

**Udit Mehrotra**  
Principal Product Manager, Amazon Kindle  
North America Languages Experience (NALX)

## License

MIT License
