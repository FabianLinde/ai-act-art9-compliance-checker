import streamlit as st
from pyshacl import validate
import rdflib

# 1. Set up the Web Page
st.set_page_config(page_title="AI Act Compliance Checker", page_icon="⚖️")
st.title("⚖️ AI Act SHACL Compliance Checker")
st.write("Upload your semantic risk management model (Turtle format) to verify compliance against the EU AI Act SHACL constraints.")

# 2. File Uploader UI
uploaded_file = st.file_uploader("Upload Risk Model (.ttl)", type=['ttl'])

if uploaded_file is not None:
    st.info("File uploaded successfully. Parsing data...")
    
    # 3. Initialize RDF Graphs
    data_graph = rdflib.Graph()
    shacl_graph = rdflib.Graph()
    
    try:
        # Load the uploaded data
        data_graph.parse(uploaded_file, format="turtle")
        
        # Load your provided SHACL rules
        shacl_graph.parse("rules.shacl", format="turtle")
        
        # 4. Run the Validation
        with st.spinner("Running PySHACL Validation..."):
            conforms, results_graph, results_text = validate(
                data_graph,
                shacl_graph=shacl_graph,
                data_graph_format="turtle",
                shacl_graph_format="turtle",
                inference='rdfs',
                debug=False
            )
            
        # 5. Display the Results
        if conforms:
            st.balloons()
            st.success("✅ **COMPLIANT:** The model satisfies all SHACL constraints!")
        else:
            st.error("❌ **NON-COMPLIANT:** The model failed the compliance check. See details below:")
            # Display the raw SHACL report so the user knows exactly what is missing
            st.text(results_text)
            
    except Exception as e:
        st.error(f"Error processing the RDF data: {e}")