import streamlit as st
from pyshacl import validate
import rdflib

# 1. Set up the Web Page Layout
st.set_page_config(page_title="AI Act Compliance Checker", page_icon="⚖️", layout="wide")
st.title("⚖️ AI Act SHACL Compliance Checker")
st.write("Verify a semantic risk management model against EU AI Act SHACL constraints.")

# 2. Embed the Sample Model Template
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

# 3. Setup Interface Tabs
tab1, tab2 = st.tabs(["✍️ Edit Model Directly", "📁 Upload Model File"])

ttl_data = None
source_name = ""

with tab1:
    st.subheader("Interactive Turtle Editor")
    st.write("Modify the graph below directly, then click the evaluation button.")
    
    # Large textbox displaying the default model
    edited_code = st.text_area(
        label="Turtle Data (TTL)", 
        value=DEFAULT_MODEL, 
        height=450, 
        help="Change values, classes, or properties to test failures!"
    )
    
    if st.button("Run Compliance Check", type="primary"):
        ttl_data = edited_code
        source_name = "Interactive Editor"

with tab2:
    st.subheader("Upload a Custom Model")
    uploaded_file = st.file_uploader("Upload Risk Model (.ttl)", type=['ttl'])
    if uploaded_file is not None:
        ttl_data = uploaded_file
        source_name = uploaded_file.name

# 4. Unified Processing Engine
if ttl_data is not None:
    st.divider()
    st.subheader(f"Validation Report ({source_name})")
    
    data_graph = rdflib.Graph()
    shacl_graph = rdflib.Graph()
    
    try:
        # Dynamically parse based on string text input vs. file upload
        if isinstance(ttl_data, str):
            print("\n[DEBUG] Parsing text from interactive editor...")
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
            
        # 5. Display the Results
        if conforms:
            st.balloons()
            st.success("✅ **COMPLIANT:** The model satisfies all SHACL constraints!")
        else:
            st.error("❌ **NON-COMPLIANT:** The model failed the compliance check. See details below:")
            st.text(results_text)
            
    except Exception as e:
        st.error(f"Error processing the RDF data: {e}")