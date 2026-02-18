import streamlit as st
import core.extractor as extractor
import core.visualizer_mermaid as visualizer_mermaid
import core.generator as generator
import core.validator as validator
import json

st.set_page_config(page_title="Logic Foundry", layout="wide")

st.title("Logic Foundry 🏭")
st.markdown("Extract and visualize business logic from code.")

# Sidebar Configuration
with st.sidebar:
    st.header("Settings")
    # OpenRouter Model Selection
    model_name = st.selectbox(
        "AI Model", 
        [
            "anthropic/claude-3.5-sonnet", # Best for logic
            "google/gemini-2.0-flash-001", # Fast
            "openai/gpt-4o",               # General purpose
            "meta-llama/llama-3-70b-instruct",
            "mistralai/mistral-large"
        ]
    )

# Main Input
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("1. Input Legacy Code")
    code_input = st.text_area("Paste Spaghetti Code Here", height=400)
    extract_btn = st.button("Extract Logic", type="primary")

if extract_btn and code_input:
    with st.spinner("Extracting Logic..."):
        # Run Extractor
        result = extractor.extract_logic(code_input, model_name)
        st.session_state['logic_data'] = result
        st.session_state['modern_code'] = None # Reset code when new logic extracted
        st.success("Extraction Complete!")

# Tabs for Output
# ---------------------------------------------------------
# UPDATE: Added "⚖️ Validator" as the 4th tab
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Flowchart", "📄 Raw Logic", "✨ Modern Code", "⚖️ Validator", "📈 Stats"])
# ---------------------------------------------------------

if 'logic_data' in st.session_state:
    logic_data = st.session_state['logic_data']
    
    # Tab 1: Flowchart
    with tab1:
        st.subheader("Logic Visualization")
        try:
            # Use Mermaid.js Visualizer
            mermaid_code = visualizer_mermaid.generate_mermaid(logic_data)
            
            # Render Mermaid
            st.markdown(f"```mermaid\n{mermaid_code}\n```")
            
            # Export Options
            st.divider()
            st.subheader("Export Flowchart")
            st.text_area("Mermaid Source (Copy & Paste into Mermaid Live Editor)", mermaid_code, height=200)
            st.markdown("[Open Mermaid Live Editor](https://mermaid.live/)")
                    
        except Exception as e:
            st.error(f"Visualization failed: {e}")

    # Tab 2: JSON
    with tab2:
        st.subheader("Extracted Business Rules")
        st.json(logic_data)
        json_str = json.dumps(logic_data, indent=2)
        st.download_button(
            label="Download JSON Analysis",
            data=json_str,
            file_name="logic_analysis.json",
            mime="application/json"
        )

    # Tab 3: Code Generator
    with tab3:
        st.subheader("Generate Modern Implementation")
        target_lang = st.selectbox("Target Language", ["Python 3.12", "TypeScript (Node)", "Go", "Java 21"])
        
        if st.button("Generate Code"):
            with st.spinner("Refactoring..."):
                # Pass empty dict for keys to use env defaults from extractor
                modern_code = generator.generate_modern_code(
                        logic_data, 
                        target_lang,
                        {}, 
                        model_name
                )
                # SAVE TO SESSION STATE so Validator can see it
                st.session_state['modern_code'] = modern_code 
                st.code(modern_code, language=target_lang.lower().split()[0])
        elif 'modern_code' in st.session_state and st.session_state['modern_code']:
            st.code(st.session_state['modern_code'], language=target_lang.lower().split()[0])

    # Tab 4: VALIDATOR (The New Section)
    with tab4:
        st.subheader("Symbolic Equivalence Check")
        st.markdown("This module mathematically compares the **Extracted Logic** against the **Modern Code** to ensure zero bugs were introduced.")
        
        # Check if we have both pieces of data
        has_logic = 'logic_data' in st.session_state
        has_code = 'modern_code' in st.session_state and st.session_state['modern_code'] is not None
        
        if st.button("Run Verification Audit", disabled=not (has_logic and has_code)):
            with st.spinner("Auditing Code Logic..."):
                audit_result = validator.validate_equivalence(
                    st.session_state['logic_data'], 
                    st.session_state['modern_code'], 
                    model_name
                )
                
                # Display High-Level Metrics
                m_col1, m_col2, m_col3 = st.columns(3)
                
                # Score Metric
                score = audit_result.get('score', 0)
                m_col1.metric("Equivalence Score", f"{score}/100")
                
                # Status Metric
                status = audit_result.get('status', 'UNKNOWN')
                if status == "PASS":
                    m_col2.success(f"✅ {status}")
                elif status == "FAIL":
                    m_col2.error(f"❌ {status}")
                else:
                    m_col2.warning(f"⚠️ {status}")

                st.info(f"**Summary:** {audit_result.get('summary', 'No summary provided')}")

                # Display Discrepancies if any
                discrepancies = audit_result.get('discrepancies', [])
                if discrepancies:
                    st.write("### 🚨 Discrepancies Found")
                    for issue in discrepancies:
                        with st.expander(f"{issue.get('severity', 'ISSUE')}: {issue.get('rule_id', 'Unknown Rule')}"):
                            st.write(issue.get('issue'))
                elif status == "PASS":
                    st.balloons()
                    st.write("### ✨ Perfect Match. No regressions detected.")
        
        if not has_code:
            st.warning("⚠️ You must generate Modern Code (Tab 3) before you can validate it.")

    # Tab 5: Stats
    with tab5:
         stats = logic_data.get("stats", {})
         st.metric("Rule Count", stats.get("rule_count", 0))
         st.metric("Complexity Score", stats.get("complexity_score", 0))

else:
    if not code_input:
        st.info("👈 Enter Legacy Code and click 'Extract Logic' to start.")
