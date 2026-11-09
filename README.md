# EcoSort Enhanced

Features: unknown-item handling, English/Kannada interface and disposal guidance, SQLite household waste logging in kg, weekly charts, CSV export, interactive quiz with score and explanations, and a separate sample-guide chart.

## Run locally
1. Open this folder in VS Code.
2. Run `python -m pip install -r requirements.txt`
3. Run `python -m streamlit run app.py`
4. Open the local URL shown in the terminal.

The app creates `ecosort.db` beside `app.py`. Keep it to retain your local entries. For online hosting, local SQLite persistence may not survive some redeployments/restarts; a persistent database is better for a multi-user version.

The guide uses predefined rules, not AI image recognition. Check local municipal waste guidance. Kannada text is a starter translation and should be reviewed before public use.
