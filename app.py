from flask import Flask, render_template, request, redirect, url_for, session
from io import StringIO
import json

from helpers.namelist_validator import NamelistValidator
from helpers.domain_grid_validation import DomainGridValidation
from helpers.vertical_coordinate_validation import VerticalCoordinateValidation
from helpers.physics_consistency_validation import PhysicsConsistencyValidation
from helpers.dynamics_options_validation import DynamicsOptionsValidation
from helpers.nesting_options_validation import NestingOptionsValidation

app = Flask(__name__)
app.secret_key = "secret_key"

@app.route("/", methods=['GET', 'POST'])
def index():

    # if session errors exist, clear them
    if 'result' in session:
        session.pop('result', None)

    # clear session state
    # Initialize the counter
    session.setdefault('check_namelist_count', 0)

    # Initialize session state values
    session.setdefault('namelist_file', None)
    session.setdefault('namelist_input', '')
    session.setdefault('result', '')

    if request.method == 'POST':
        file = request.files['namelist_file']
        text = request.form['namelist_input']

        if not file and not text:
            session['result'] = "Please upload a file or enter text."
        else:
            # Convert the input text to a file-like buffer if input is from text area
            # namelist_buffer = StringIO(text) if text else file

            # Convert the input text to a file-like buffer if input is from text area
            namelist_buffer = StringIO(text) if text else file

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
                session['result'] = "Namelist validation success!"
            else:
                # session['result'] = json.dumps(all_errors)

                # make a formatted tailwind list item for all errors and append to session['result']
                for error in all_errors:
                    session['result'] += f' <li class="list-disc list-inside">{error}</li>'
                




        session['check_namelist_count'] += 1

    return render_template('index.html', count=session['check_namelist_count'], result=session['result'])


if __name__ == "__main__":
    app.run(debug=True)
