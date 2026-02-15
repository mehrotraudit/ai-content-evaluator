import streamlit as st
from utils.evaluator import ContentEvaluator
from utils.data_model import (
    MARKETING_COPY_CRITERIA,
    BILINGUAL_COMPLIANCE_CRITERIA,
    CriterionScore,
    get_decision
)
import json
from datetime import datetime

# Page config
st.set_page_config(
    page_title="AI Content Quality Evaluator",
    page_icon="🎯",
    layout="wide"
)

# Initialize evaluator
@st.cache_resource
def get_evaluator():
    return ContentEvaluator()

evaluator = get_evaluator()

# Initialize session state for storing evaluations
if 'evaluations' not in st.session_state:
    st.session_state.evaluations = []

# Title and description
st.title("🎯 AI Content Quality Evaluator")
st.markdown("""
Evaluate multilingual marketing content and bilingual compliance using AI-powered quality assessment.
Built for Amazon's North America Languages Experience team.
""")

# Create tabs
tab1, tab2, tab3 = st.tabs(["📝 Evaluate Content", "📊 Review History", "📚 Learn About Evals"])

# TAB 1: Evaluate Content
with tab1:
    st.header("Evaluate New Content")
    
    # Use case selection
    use_case = st.selectbox(
        "Select Use Case",
        options=["marketing_copy", "bilingual_compliance"],
        format_func=lambda x: "Marketing Copy (Multilingual Creation)" if x == "marketing_copy" else "Bilingual Compliance (Translation Quality)"
    )
    
    # Context input
    if use_case == "marketing_copy":
        context_placeholder = "e.g., Mother's Day campaign for Spanish-speaking US customers"
        st.info("📌 **Use Case:** Evaluating marketing copy created directly in target language (not translated)")
    else:
        context_placeholder = "e.g., Toy product warning label for Canadian market (English/French)"
        st.info("📌 **Use Case:** Evaluating bilingual product documentation quality")
    
    context = st.text_input("Context (optional)", placeholder=context_placeholder)
    
    # Content input
    content = st.text_area(
        "Content to Evaluate",
        height=200,
        placeholder="Paste your content here..."
    )
    
    # Evaluate button
    col1, col2 = st.columns([1, 5])
    with col1:
        evaluate_btn = st.button("🚀 Evaluate", type="primary", use_container_width=True)
    
    if evaluate_btn:
        if not content:
            st.error("Please enter content to evaluate")
        else:
            with st.spinner("Evaluating with Claude..."):
                try:
                    # Get evaluation
                    evaluation = evaluator.evaluate_content(
                        content=content,
                        use_case=use_case,
                        context=context
                    )
                    
                    # Store in session state
                    st.session_state.evaluations.append(evaluation)
                    st.session_state.show_last_eval = True
                    
                except Exception as e:
                    st.error(f"Error during evaluation: {str(e)}")
                    st.session_state.show_last_eval = False
    
    # Display last evaluation if it exists
    if st.session_state.get('show_last_eval') and len(st.session_state.evaluations) > 0:
        evaluation = st.session_state.evaluations[-1]
        
        # Display results
        st.success("✅ Evaluation Complete!")
        
        # Overall score with color coding
        score_color = "green" if evaluation.ai_decision == "auto_pass" else "orange" if evaluation.ai_decision == "human_review" else "red"
        
        st.markdown(f"""
        ### Overall Score: <span style='color:{score_color}; font-size:2em'>{evaluation.ai_overall_score}/5.0</span>
        **Decision:** {evaluation.ai_decision.replace('_', ' ').title()}
        """, unsafe_allow_html=True)
        
        # Detailed scores
        st.subheader("Detailed Scores")
        
        criteria = MARKETING_COPY_CRITERIA if evaluation.use_case == "marketing_copy" else BILINGUAL_COMPLIANCE_CRITERIA
        
        for criterion_key, criterion_info in criteria.items():
            score_obj = evaluation.ai_scores[criterion_key]
            
            with st.expander(f"**{criterion_info['name']}**: {score_obj.score}/5.0 (Weight: {int(criterion_info['weight']*100)}%)"):
                st.write(f"**Definition:** {criterion_info['description']}")
                st.write(f"**AI Explanation:** {score_obj.explanation}")
        
        # Option to add human judgment
        st.divider()
        st.subheader("Add Human Judgment (Optional)")
        
        # Show human judgment results if they already exist
        if evaluation.human_overall_score:
            st.success(f"✅ Human judgment recorded! Human score: {evaluation.human_overall_score}/5.0")
            
            # Show agreement
            agreement_diff = abs(evaluation.ai_overall_score - evaluation.human_overall_score)
            
            col1, col2 = st.columns(2)
            col1.metric("AI Score", f"{evaluation.ai_overall_score}/5.0")
            col2.metric("Human Score", f"{evaluation.human_overall_score}/5.0", 
                      delta=f"{evaluation.human_overall_score - evaluation.ai_overall_score:+.2f}")
            
            if agreement_diff < 0.5:
                st.info("🤝 High agreement between AI and Human (difference < 0.5)")
            elif agreement_diff < 1.0:
                st.warning("⚠️ Moderate agreement (difference < 1.0)")
            else:
                st.error("❌ Low agreement (difference ≥ 1.0)")
        else:
            # Form to add human judgment
            with st.form(key="human_judgment"):
                st.write("Rate the same criteria to compare AI vs Human judgment:")
                
                human_scores = {}
                cols = st.columns(2)
                
                for idx, (criterion_key, criterion_info) in enumerate(criteria.items()):
                    with cols[idx % 2]:
                        score = st.slider(
                            criterion_info['name'],
                            min_value=1.0,
                            max_value=5.0,
                            value=3.0,
                            step=0.5,
                            key=f"human_{criterion_key}"
                        )
                        human_scores[criterion_key] = score
                
                human_feedback = st.text_area("Additional Feedback (optional)")
                
                submit_human = st.form_submit_button("Submit Human Judgment")
                
                if submit_human:
                    # Calculate human overall score
                    total_score = sum(human_scores[k] * criteria[k]['weight'] for k in human_scores)
                    total_weight = sum(criteria[k]['weight'] for k in criteria)
                    human_overall = round(total_score / total_weight, 2)
                    
                    # Determine human decision
                    human_decision = get_decision(human_overall)
                    
                    # Update the evaluation in session state
                    evaluation.human_scores = {
                        k: CriterionScore(score=v, explanation="Human rating", weight=criteria[k]['weight'])
                        for k, v in human_scores.items()
                    }
                    evaluation.human_overall_score = human_overall
                    evaluation.human_decision = human_decision
                    evaluation.human_feedback = human_feedback
                    
                    # Force rerun to show updated metrics
                    st.balloons()
                    st.rerun()

# TAB 2: Review History
with tab2:
    st.header("Evaluation History")
    
    if not st.session_state.evaluations:
        st.info("No evaluations yet. Go to 'Evaluate Content' tab to create your first evaluation.")
    else:
        st.write(f"**Total Evaluations:** {len(st.session_state.evaluations)}")
        
        # Summary stats
        col1, col2, col3 = st.columns(3)
        
        auto_pass = sum(1 for e in st.session_state.evaluations if e.ai_decision == "auto_pass")
        auto_fail = sum(1 for e in st.session_state.evaluations if e.ai_decision == "auto_fail")
        human_review = sum(1 for e in st.session_state.evaluations if e.ai_decision == "human_review")
        
        col1.metric("Auto Pass", auto_pass)
        col2.metric("Auto Fail", auto_fail)
        col3.metric("Human Review Needed", human_review)
        
        # Average scores
        avg_ai_score = sum(e.ai_overall_score for e in st.session_state.evaluations) / len(st.session_state.evaluations)
        st.metric("Average AI Score", f"{avg_ai_score:.2f}/5.0")
        
        # Show evaluations
        st.divider()
        
        for idx, eval_obj in enumerate(reversed(st.session_state.evaluations)):
            with st.expander(f"Evaluation #{len(st.session_state.evaluations) - idx} - {eval_obj.use_case.replace('_', ' ').title()} - Score: {eval_obj.ai_overall_score}/5.0"):
                st.write(f"**Timestamp:** {eval_obj.timestamp}")
                st.write(f"**Context:** {eval_obj.context or 'None'}")
                st.write(f"**Decision:** {eval_obj.ai_decision.replace('_', ' ').title()}")
                
                st.text_area("Content", eval_obj.content, height=100, disabled=True, key=f"content_{idx}")
                
                if eval_obj.human_overall_score:
                    col1, col2 = st.columns(2)
                    col1.metric("AI Score", f"{eval_obj.ai_overall_score}/5.0")
                    col2.metric("Human Score", f"{eval_obj.human_overall_score}/5.0")
                    
                    if eval_obj.human_feedback:
                        st.write(f"**Human Feedback:** {eval_obj.human_feedback}")
        
        # Export option
        if st.button("Export History as JSON"):
            export_data = [e.to_dict() for e in st.session_state.evaluations]
            st.download_button(
                label="Download JSON",
                data=json.dumps(export_data, indent=2),
                file_name=f"evaluations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )

# TAB 3: Learn About Evals
with tab3:
    st.header("Understanding AI Evaluations")
    
    st.markdown("""
    ## What are Evals?
    
    **Evals (Evaluations)** are systematic methods for measuring the quality of AI-generated content. Unlike traditional software testing with binary pass/fail, AI evaluations measure subjective qualities like helpfulness, accuracy, and cultural appropriateness.
    
    ## Why Evals Matter
    
    Traditional metrics like click-through rates or engagement can be gamed (Goodhart's Law). Evals help you:
    - Measure actual quality, not just proxies
    - Catch issues before they reach customers
    - Improve models systematically
    - Build trust in AI systems
    
    ## How This Framework Works
    
    ### 1. LLM-as-Judge
    We use Claude to evaluate content on multiple criteria. This scales to thousands of evaluations per day.
    
    ### 2. Configurable Criteria
    Different use cases have different quality standards:
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Marketing Copy")
        for key, info in MARKETING_COPY_CRITERIA.items():
            st.write(f"**{info['name']}** ({int(info['weight']*100)}%)")
            st.write(f"_{info['description']}_")
            st.write("")
    
    with col2:
        st.subheader("Bilingual Compliance")
        for key, info in BILINGUAL_COMPLIANCE_CRITERIA.items():
            st.write(f"**{info['name']}** ({int(info['weight']*100)}%)")
            st.write(f"_{info['description']}_")
            st.write("")
    
    st.markdown("""
    ### 3. Weighted Scoring
    Each criterion has a weight based on business importance. The overall score is a weighted average.
    
    ### 4. Auto-Triage
    - **Auto-Pass** (≥4.0): High quality, ship it
    - **Human Review** (2.5-4.0): Needs human judgment
    - **Auto-Fail** (<2.5): Major issues, don't ship
    
    ### 5. Human-in-the-Loop
    AI judges can be biased or inconsistent. By adding human judgments, you can:
    - Measure AI-human agreement
    - Identify where AI struggles
    - Continuously improve the evaluation system
    
    ## Best Practices
    
    1. **Start with clear criteria** - Define what "good" means for your use case
    2. **Calibrate weights** - Adjust based on business impact
    3. **Validate the judge** - Compare AI ratings to human experts
    4. **Iterate** - Refine criteria and prompts based on results
    5. **Track trends** - Monitor quality over time
    
    ## Industry Best Practices
    
    This framework follows evaluation patterns used by leading AI companies:
    - **OpenAI**: Uses LLM-as-judge for model evaluations
    - **Anthropic**: Constitutional AI with multi-criteria evaluation
    - **Google**: Combines automated and human evaluation
    
    ## Learn More
    
    - [Anthropic's Claude Evaluation Guide](https://docs.anthropic.com/claude/docs/guide-to-anthropics-prompt-engineering-resources)
    - [OpenAI Evals Framework](https://github.com/openai/evals)
    - Research: "Judging LLM-as-a-judge with MT-Bench and Chatbot Arena"
    """)

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: gray;'>
Built by Udit Mehrotra | Amazon North America Languages Experience
</div>
""", unsafe_allow_html=True)