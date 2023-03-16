import streamlit as st
from helpers.namelist_validator import NamelistValidator
import pandas as pd
import io

st.title("AceCast Namelist Advisor v0.7")

# File uploader
namelist_file = st.file_uploader("Upload namelist file (FORTRAN namelist format)", type=["nml", "txt", "input"])

# Text area for namelist input
namelist_input = st.text_area("Or paste the contents of your namelist here")

# Check namelist button
check_namelist_button = st.button("Check Namelist")

if check_namelist_button:
    if namelist_file:
        validator = NamelistValidator("registry-v3.0.1.json", namelist_file)

        errors = validator.validate()
        if not errors:
            st.success("Namelist validation success!")
        else:
            st.error("Namelist validation failure. One or more unsupported options found!")
            if errors:
                error_df = pd.DataFrame(errors)
                st.table(error_df)
    elif namelist_input:
        # Convert the input text to a file-like buffer
        namelist_buffer = io.StringIO(namelist_input)

        validator = NamelistValidator("registry-v3.0.1.json", namelist_buffer)

        errors = validator.validate()
        if not errors:
            st.success("Namelist validation success!")
        else:
            st.error("Namelist validation failure. One or more unsupported options found!")
            if errors:
                error_df = pd.DataFrame(errors)
                st.table(error_df)
    else:
        st.warning("Please upload your namelist file or paste the namelist content to proceed.")
