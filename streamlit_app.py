import streamlit as st
from helpers.namelist_validator import NamelistValidator
from helpers.domain_grid_validation import DomainGridValidation
from helpers.vertical_coordinate_validation import VerticalCoordinateValidation
from helpers.physics_consistency_validation import PhysicsConsistencyValidation
from helpers.dynamics_options_validation import DynamicsOptionsValidation
from helpers.nesting_options_validation import NestingOptionsValidation
import pandas as pd
import io

st.title("AceCast Namelist Advisor v0.7")

# Initialize the counter
if 'check_namelist_count' not in st.session_state:
    st.session_state['check_namelist_count'] = 0



# Initialize session state values
if 'namelist_file' not in st.session_state:
    st.session_state['namelist_file'] = None

if 'namelist_input' not in st.session_state:
    st.session_state['namelist_input'] = ''

# File uploader
st.session_state.namelist_file = st.file_uploader("Upload namelist file (FORTRAN namelist format)", type=["nml", "txt", "input"])

# Text area for namelist input
st.session_state.namelist_input = st.text_area("Or paste the contents of your namelist here", st.session_state.namelist_input)

# Check namelist button
check_namelist_button = st.button("Check Namelist")


# Display the counter value
st.write(f"Check Namelist button clicked {st.session_state.check_namelist_count} times in this session.")


if check_namelist_button:
    st.session_state.check_namelist_count += 1

    if st.session_state.namelist_file or st.session_state.namelist_input:
        # Convert the input text to a file-like buffer if input is from text area
        namelist_buffer = io.StringIO(st.session_state.namelist_input) if st.session_state.namelist_input else st.session_state.namelist_file

        validator = NamelistValidator("registry-v3.0.1.json", namelist_buffer)
        domain_validator = DomainGridValidation(validator.user_nml)
        vcs_validator = VerticalCoordinateValidation(validator.user_nml)
        physics_validator = PhysicsConsistencyValidation(validator.user_nml)
        dynamics_validator = DynamicsOptionsValidation(validator.user_nml)
        nesting_validator = NestingOptionsValidation(validator.user_nml)

        # Call validation methods
        errors = validator.validate()
        domain_errors = domain_validator.validate_domain_coverage()
        vcs_errors = vcs_validator.run_validation()
        physics_errors = physics_validator.validate_physics_consistency()
        dynamics_errors = dynamics_validator.validate_advection_schemes()
        nesting_errors = nesting_validator.validate_nesting_options()

        # Combine error lists
        all_errors = [error for validator in [errors, domain_errors, vcs_errors, physics_errors, dynamics_errors, nesting_errors] for error in (validator if validator is not None else [])]

        if not all_errors:
            st.success("Namelist validation success!")
        else:
            st.error("Namelist validation failure. One or more unsupported options found!")
            error_df = pd.DataFrame(all_errors)
            st.table(error_df)
    else:
        st.warning("Please upload your namelist file or paste the namelist content to proceed.")
