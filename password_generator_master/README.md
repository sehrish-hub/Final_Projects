install uv
pip install uv
create and initialize the project
uv init --package password_generator_master
cd password_generator_master
install dependency
uv add streamlit
active uv virtual environment
uv venv
.venv\Scripts\activate
run the app
streamlit run password_generator_master.py
