import streamlit as st
from pyshacl import validate
import rdflib

# 1. Set up the Web Page Layout
st.set_page_config(page_title="AI Act Compliance Checker", page_icon="⚖️")
st.title("⚖️ AI Act SHACL Compliance Checker")
st.write("Verify a semantic risk management model against EU AI Act SHACL constraints.")

# 2. Embed the Sample Model Template (Tucked away inside code variables)
DEFAULT_MODEL = """@prefix sh:   <http://www.w3.org/ns/shacl#> .
@prefix dpv:  <http://w3id.org/dpv#> .
@prefix risk: <https://w3id.org/dpv/risk#> .
@prefix eu:     <https://w3id.org/dpv/legal/eu#> .
@prefix tech:   <https://w3id.org/dpv/tech#> .
@prefix euaiact:   <https://w3id.org/dpv/legal/eu/aiact#> .
@prefix ex:    <http://example.org/#> .

# 1. The Core System
ex:MySystem a euaiact:HighRiskAISystem ;
    tech:hasDocumentation ex:MyDocs ;
    tech:hasProvider ex:MyProvider ;
    risk:hasRiskManagement ex:MyRiskManagement .

ex:MyDocs a euaiact:InstructionsForUse .

# 2. Provider & Training
ex:MyProvider a euaiact:AIProvider ;
    dpv:hasOrganisationalMeasure ex:MyTraining .
ex:MyTraining a euaiact:TrainingForDeployer .

# 3. Risk Management Pipeline
ex:MyRiskManagement a risk:RiskManagement ;
    risk:hasRiskAssessment ex:MyAssessment .

ex:MyAssessment a risk:RiskAssessment ;
    risk:hasRiskIdentification ex:MyIdentification .

ex:MyIdentification a risk:RiskIdentification ;
    risk:identifies ex:MyRisk .

# 4. The Risk Details
ex:MyRisk a risk:Risk ;
    risk:hasRiskSource ex:MySource ;
    dpv:hasConsequence ex:MyConsequence ;
    risk:hasRiskTreatment ex:MyTreatment ;
    risk:hasRiskControl ex:MyControl ;
    risk:hasRiskEvaluation ex:MyEvaluation .

ex:MySource a risk:RiskSource .
ex:MyTreatment a risk:RiskTreatment .
ex:MyControl a risk:RiskControl .
ex:MyEvaluation a risk:RiskEvaluation .

# 5. Consequences
ex:MyConsequence a dpv:Consequence ;
    dpv:hasConsequenceOn ex:HealthImpact ;
    dpv:hasSeverity ex:HighSeverity ;
    dpv:hasLikelihood ex:HighLikelihood .

ex:HealthImpact a risk:Health .
ex:HighSeverity a dpv:Severity .
ex:HighLikelihood a dpv:Likelihood .
"""

# 3. Primary UI Feature: File Uploader
st.subheader("📁 Primary Action: Upload Model File")
uploaded_file = st.file_uploader("Choose a compliance risk model file (.ttl)", type=['ttl'])

# Variables to hold our targeted active data
ttl_data = None
source_name = ""

# 4. Secondary UI Feature: Collapsible Sample Sandbox
st.write("---") # Visual divider line
with st.expander("💡 Don't have a file? View, edit, or test with our built-in compliant model"):
    st.write("You can modify this Turtle code directly inside the box to test how the constraints behave.")
    edited_code = st.text_area(
        label="Sample Data (TTL)", 
        value=DEFAULT_MODEL, 
        height=300
    )
    run_sample = st.button("Run Compliance on Sample Data", type="secondary")

# Determine which action the user chose
if uploaded_file is not None:
    ttl_data = uploaded_file
    source_name = uploaded_file.name
elif run_sample:
    ttl_data = edited_code
    source_name = "Interactive Sample Data"

# 5. Unified Processing Engine
if ttl_data is not None:
    st.divider()
    st.subheader(f"Validation Report ({source_name})")
    
    data_graph = rdflib.Graph()
    shacl_graph = rdflib.Graph()
    
    try:
        # Dynamically parse based on string text input vs. file upload wrapper
        if isinstance(ttl_data, str):
            print("\n[DEBUG] Parsing text from interactive expander...")
            data_graph.parse(data=ttl_data, format="turtle")
        else:
            print(f"\n[DEBUG] Parsing uploaded file: {source_name}...")
            data_graph.parse(ttl_data, format="turtle")
        print("[DEBUG] Successfully parsed target model data!")
        
        print("[DEBUG] Starting to parse rules.shacl...")
        shacl_graph.parse("rules.shacl", format="turtle")
        print("[DEBUG] Successfully parsed rules.shacl!")
        
        with st.spinner("Running PySHACL Validation..."):
            print("[DEBUG] Launching PySHACL validator (inference=None)...")
            conforms, results_graph, results_text = validate(
                data_graph,
                shacl_graph=shacl_graph,
                data_graph_format="turtle",
                shacl_graph_format="turtle",
                inference=None,
                debug=False
            )
            print("[DEBUG] PySHACL validation finished successfully!")
            
        # 6. Display the Results
        if conforms:
            st.balloons()
            st.success("✅ **COMPLIANT:** The model satisfies all SHACL constraints!")
        else:
            st.error("❌ **NON-COMPLIANT:** The model failed the compliance check. See details below:")
            st.text(results_text)
            
    except Exception as e:
        st.error(f"Error processing the RDF data: {e}")