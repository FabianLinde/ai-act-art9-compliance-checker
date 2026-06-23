import streamlit as st
from pyshacl import validate
import rdflib

# 1. Set up the Web Page Layout
st.set_page_config(page_title="AI Act Art. 9 Compliance Checker", page_icon="⚖️")
st.title("⚖️ AI Act Art. 9 Risk Management Compliance Checker")
st.write("Verify a semantic risk management model against the requirements of Article 9 of the EU AI Act. This tool uses SHACL constraints defined in `rules.shacl` to validate your model's compliance. You can upload your own Turtle file or use the interactive sample below.")
st.write("Note: This tool is based on the [Data Privacy Vocabulary (DPV)](https://w3id.org/dpv/). For the verification to work, the risk management must be modelled in DPV (including extensions).")
st.write("This application has been developed by [Fabian Linde](https://linkedin.com/in/fabianlinde) for deliverable D2.4 of the [HARNESS](https://harness-network.eu/index.html) project. This project has received funding from the European Union's Horizon Europe research and innovation programme under grant agreement [101169409](https://cordis.europa.eu/project/id/101169409).")
st.write("The output of this tool is purely informative. This is not legal advice.")         

# 2. Dynamically Load the Sample Model Template from local file
try:
    with open("sample_model.ttl", "r", encoding="utf-8") as f:
        sample_model = f.read()
except FileNotFoundError:
    sample_model = "# Error: sample_model.ttl file missing from repository."

# Dynamically Load the SHACL Rules for UI viewing
try:
    with open("rules.shacl", "r", encoding="utf-8") as f:
        shacl_rules = f.read()
except FileNotFoundError:
    shacl_rules = "# Error: rules.shacl file missing from repository."

# 3. Primary UI Feature: File Uploader
st.subheader("📁 Upload Model File")
uploaded_file = st.file_uploader("Choose a risk management model file (.ttl)", type=['ttl'])

# Variables to hold our targeted active data
ttl_data = None
source_name = ""

# 4. Secondary UI Feature: Collapsible Sample Sandbox
st.write("---") 
with st.expander("💡 Don't have a file? View, edit, or test with our built-in compliant risk management model."):
    st.write("You can modify this Turtle code directly inside the box to test how the constraints behave.")
    edited_code = st.text_area(
        label="Sample Model (TTL)", 
        value=sample_model, 
        height=300
    )
    run_sample = st.button("Run Compliance on Sample Model", type="secondary")

# New Collapsible Viewer: Inspect the rules.shacl file
with st.expander("🔍 Inspect the Validation Logic (rules.shacl)"):
    st.write("These are the SHACL graph constraints enforcing EU AI Act Art. 9 mappings on the risk management model structure:")
    st.code(shacl_rules, language="turtle")

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
