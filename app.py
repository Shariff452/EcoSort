import streamlit as st
import pandas as pd
import sqlite3
from pathlib import Path
from datetime import date, datetime

st.set_page_config(page_title="EcoSort", page_icon="♻️", layout="wide")
DB = Path(__file__).with_name("ecosort.db")

ITEMS = {
    "banana peel": ("Wet / Biodegradable", "Wet waste bin", "Place in wet waste; compost where locally accepted.", "ಒದ್ದೆ / ಜೈವಿಕ ತ್ಯಾಜ್ಯ", "ಒದ್ದೆ ತ್ಯಾಜ್ಯದ ಡಬ್ಬಿ", "ಒದ್ದೆ ತ್ಯಾಜ್ಯಕ್ಕೆ ಹಾಕಿ; ಸ್ಥಳೀಯವಾಗಿ ಅನುಮತಿ ಇದ್ದರೆ ಕಾಂಪೋಸ್ಟ್ ಮಾಡಿ."),
    "vegetable peels": ("Wet / Biodegradable", "Wet waste bin", "Keep separate from plastic wrappers.", "ಒದ್ದೆ / ಜೈವಿಕ ತ್ಯಾಜ್ಯ", "ಒದ್ದೆ ತ್ಯಾಜ್ಯದ ಡಬ್ಬಿ", "ಪ್ಲಾಸ್ಟಿಕ್ ಹೊದಿಕೆಗಳಿಂದ ಬೇರ್ಪಡಿಸಿ."),
    "leftover food": ("Wet / Biodegradable", "Wet waste bin", "Separate from packaging and dry waste.", "ಒದ್ದೆ / ಜೈವಿಕ ತ್ಯಾಜ್ಯ", "ಒದ್ದೆ ತ್ಯಾಜ್ಯದ ಡಬ್ಬಿ", "ಪ್ಯಾಕಿಂಗ್ ಮತ್ತು ಒಣ ತ್ಯಾಜ್ಯದಿಂದ ಬೇರ್ಪಡಿಸಿ."),
    "tea leaves": ("Wet / Biodegradable", "Wet waste bin", "Drain excess liquid; compost where accepted.", "ಒದ್ದೆ / ಜೈವಿಕ ತ್ಯಾಜ್ಯ", "ಒದ್ದೆ ತ್ಯಾಜ್ಯದ ಡಬ್ಬಿ", "ಹೆಚ್ಚುವರಿ ದ್ರವ ತೆಗೆದು, ಅನುಮತಿ ಇದ್ದರೆ ಕಾಂಪೋಸ್ಟ್ ಮಾಡಿ."),
    "paper": ("Dry / Recyclable", "Dry waste / paper recycling", "Keep clean and dry; follow local collection rules.", "ಒಣ / ಮರುಬಳಕೆ", "ಒಣ ತ್ಯಾಜ್ಯ / ಕಾಗದ ಮರುಬಳಕೆ", "ಸ್ವಚ್ಛವಾಗಿ ಮತ್ತು ಒಣಗಿರಿಸಿ; ಸ್ಥಳೀಯ ನಿಯಮ ಅನುಸರಿಸಿ."),
    "cardboard": ("Dry / Recyclable", "Dry waste / paper recycling", "Flatten and keep dry.", "ಒಣ / ಮರುಬಳಕೆ", "ಒಣ ತ್ಯಾಜ್ಯ / ಕಾಗದ ಮರುಬಳಕೆ", "ಮಡಚಿ ಒಣಗಿರಿಸಿ."),
    "plastic bottle": ("Dry / Recyclable", "Dry waste / plastic recycling", "Empty it and check local recycling rules.", "ಒಣ / ಮರುಬಳಕೆ", "ಒಣ ತ್ಯಾಜ್ಯ / ಪ್ಲಾಸ್ಟಿಕ್ ಮರುಬಳಕೆ", "ಖಾಲಿ ಮಾಡಿ ಸ್ಥಳೀಯ ಮರುಬಳಕೆ ನಿಯಮ ಪರಿಶೀಲಿಸಿ."),
    "glass bottle": ("Dry / Recyclable", "Dry waste / glass collection", "Handle carefully; securely wrap broken glass.", "ಒಣ / ಮರುಬಳಕೆ", "ಒಣ ತ್ಯಾಜ್ಯ / ಗಾಜು ಸಂಗ್ರಹಣೆ", "ಎಚ್ಚರಿಕೆಯಿಂದ ನಿರ್ವಹಿಸಿ; ಒಡೆದ ಗಾಜನ್ನು ಸುರಕ್ಷಿತವಾಗಿ ಸುತ್ತಿ."),
    "metal can": ("Dry / Recyclable", "Dry waste / metal recycling", "Empty and keep clean where practical.", "ಒಣ / ಮರುಬಳಕೆ", "ಒಣ ತ್ಯಾಜ್ಯ / ಲೋಹ ಮರುಬಳಕೆ", "ಖಾಲಿ ಮಾಡಿ ಸಾಧ್ಯವಾದಷ್ಟು ಸ್ವಚ್ಛವಾಗಿಡಿ."),
    "plastic wrapper": ("Dry / check local rules", "Dry waste; check local rules", "Not all flexible plastic packaging is recyclable.", "ಒಣ ತ್ಯಾಜ್ಯ / ಸ್ಥಳೀಯ ನಿಯಮ ಪರಿಶೀಲಿಸಿ", "ಒಣ ತ್ಯಾಜ್ಯ; ಸ್ಥಳೀಯ ನಿಯಮ ಪರಿಶೀಲಿಸಿ", "ಎಲ್ಲಾ ಪ್ಲಾಸ್ಟಿಕ್ ಹೊದಿಕೆಗಳನ್ನು ಮರುಬಳಕೆ ಮಾಡಲು ಸಾಧ್ಯವಿಲ್ಲ."),
    "battery": ("Hazardous household waste", "Battery collection point", "Never mix with wet waste; use a suitable collection point.", "ಅಪಾಯಕಾರಿ ಗೃಹ ತ್ಯಾಜ್ಯ", "ಬ್ಯಾಟರಿ ಸಂಗ್ರಹಣಾ ಕೇಂದ್ರ", "ಒದ್ದೆ ತ್ಯಾಜ್ಯದಲ್ಲಿ ಹಾಕಬೇಡಿ; ಸೂಕ್ತ ಸಂಗ್ರಹಣಾ ಕೇಂದ್ರಕ್ಕೆ ನೀಡಿ."),
    "led bulb": ("Special / E-waste", "E-waste collection point", "Keep separate and avoid breaking it.", "ವಿಶೇಷ / ಇ-ತ್ಯಾಜ್ಯ", "ಇ-ತ್ಯಾಜ್ಯ ಸಂಗ್ರಹಣಾ ಕೇಂದ್ರ", "ಪ್ರತ್ಯೇಕವಾಗಿಡಿ; ಒಡೆಯದಂತೆ ನೋಡಿಕೊಳ್ಳಿ."),
    "old mobile phone": ("E-waste", "Authorized e-waste collection point", "Erase personal data and use an authorized collector.", "ಇ-ತ್ಯಾಜ್ಯ", "ಅಧಿಕೃತ ಇ-ತ್ಯಾಜ್ಯ ಸಂಗ್ರಹಣಾ ಕೇಂದ್ರ", "ವೈಯಕ್ತಿಕ ಮಾಹಿತಿ ಅಳಿಸಿ ಅಧಿಕೃತ ಸಂಗ್ರಾಹಕರಿಗೆ ನೀಡಿ."),
    "medicine": ("Special household waste", "Pharmacy take-back / local guidance", "Do not flush or compost; ask a pharmacy or local authority.", "ವಿಶೇಷ ಗೃಹ ತ್ಯಾಜ್ಯ", "ಔಷಧ ಅಂಗಡಿ / ಸ್ಥಳೀಯ ಮಾರ್ಗದರ್ಶನ", "ಶೌಚಾಲಯಕ್ಕೆ ಹಾಕಬೇಡಿ ಅಥವಾ ಕಾಂಪೋಸ್ಟ್ ಮಾಡಬೇಡಿ; ಔಷಧ ಅಂಗಡಿ ಅಥವಾ ಸ್ಥಳೀಯ ಅಧಿಕಾರಿಯನ್ನು ಕೇಳಿ."),
    "sanitary waste": ("Domestic sanitary waste", "Securely wrapped separate waste", "Wrap securely and follow municipal collection guidance.", "ಗೃಹ ಸ್ವಚ್ಛತಾ ತ್ಯಾಜ್ಯ", "ಸುರಕ್ಷಿತವಾಗಿ ಸುತ್ತಿದ ಪ್ರತ್ಯೇಕ ತ್ಯಾಜ್ಯ", "ಸುರಕ್ಷಿತವಾಗಿ ಸುತ್ತಿ ನಗರಪಾಲಿಕೆ ಸೂಚನೆ ಅನುಸರಿಸಿ."),
    "used cooking oil": ("Special household waste", "Collection program / local guidance", "Do not pour into drains; let it cool first.", "ವಿಶೇಷ ಗೃಹ ತ್ಯಾಜ್ಯ", "ಸಂಗ್ರಹಣಾ ಕಾರ್ಯಕ್ರಮ / ಸ್ಥಳೀಯ ಮಾರ್ಗದರ್ಶನ", "ಚರಂಡಿಗೆ ಸುರಿಯಬೇಡಿ; ಮೊದಲು ತಣ್ಣಗಾಗಲು ಬಿಡಿ.")
}

QUIZ = [
    ("Where should a banana peel usually go?", ["Wet / biodegradable waste", "E-waste", "Battery collection"], 0, "Banana peels are biodegradable and commonly go in wet waste.", "ಬಾಳೆಹಣ್ಣಿನ ಸಿಪ್ಪೆ ಸಾಮಾನ್ಯವಾಗಿ ಒದ್ದೆ / ಜೈವಿಕ ತ್ಯಾಜ್ಯಕ್ಕೆ ಸೇರುತ್ತದೆ."),
    ("What should you do with a household battery?", ["Mix it with food scraps", "Use a battery collection point", "Put it in compost"], 1, "Batteries should be kept out of ordinary waste and taken to a suitable collection point.", "ಬ್ಯಾಟರಿಯನ್ನು ಸಾಮಾನ್ಯ ತ್ಯಾಜ್ಯದಿಂದ ಬೇರ್ಪಡಿಸಿ ಸೂಕ್ತ ಸಂಗ್ರಹಣಾ ಕೇಂದ್ರಕ್ಕೆ ನೀಡಿ."),
    ("How should clean, dry paper generally be handled?", ["With food scraps", "Keep dry for paper recycling where accepted", "With batteries"], 1, "Clean, dry paper is commonly recyclable; follow local rules.", "ಸ್ವಚ್ಛ, ಒಣ ಕಾಗದವನ್ನು ಸ್ಥಳೀಯ ನಿಯಮಗಳ ಪ್ರಕಾರ ಮರುಬಳಕೆ ಮಾಡಬಹುದು."),
    ("What should you do with an old mobile phone?", ["Wet waste", "Burn it outdoors", "Authorized e-waste collection"], 2, "Phones are e-waste and should go to an authorized collection route.", "ಮೊಬೈಲ್ ಫೋನ್ ಇ-ತ್ಯಾಜ್ಯ; ಅಧಿಕೃತ ಸಂಗ್ರಹಣಾ ವ್ಯವಸ್ಥೆಗೆ ನೀಡಿ."),
    ("Why separate wet and dry waste?", ["Helps recycling and composting", "Makes all waste hazardous", "Removes need for collection"], 0, "Segregation helps recover recyclables and manage biodegradable waste.", "ವಿಂಗಡಣೆ ಮರುಬಳಕೆ ಮತ್ತು ಜೈವಿಕ ತ್ಯಾಜ್ಯ ನಿರ್ವಹಣೆಗೆ ಸಹಾಯ ಮಾಡುತ್ತದೆ.")
]

def setup_db():
    with sqlite3.connect(DB) as c:
        c.execute("""CREATE TABLE IF NOT EXISTS waste_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item TEXT NOT NULL, category TEXT NOT NULL,
            kg REAL NOT NULL, entry_date TEXT NOT NULL)""")
        c.commit()

def read_logs():
    with sqlite3.connect(DB) as c:
        return pd.read_sql_query("SELECT item, category, kg, entry_date FROM waste_log ORDER BY entry_date DESC, id DESC", c)

setup_db()
lang = st.selectbox("Language / ಭಾಷೆ", ["English", "ಕನ್ನಡ"])
kn = lang == "ಕನ್ನಡ"
T = {
    "subtitle": "ಸ್ಮಾರ್ಟ್ ಗೃಹ ತ್ಯಾಜ್ಯ ವಿಂಗಡಣೆ ಸಹಾಯಕ" if kn else "Smart Household Waste Segregation Assistant",
    "intro": "ತ್ಯಾಜ್ಯ ವಸ್ತುವನ್ನು ಹುಡುಕಿ, ವಿಲೇವಾರಿ ತಿಳಿದುಕೊಳ್ಳಿ, ಪ್ರಮಾಣ ದಾಖಲಿಸಿ ಮತ್ತು ವಿಂಗಡಣೆಯನ್ನು ಅಭ್ಯಾಸ ಮಾಡಿ." if kn else "Search an item, learn disposal guidance, record quantities, and practise segregation.",
    "identify": "ವಸ್ತು ಗುರುತಿಸಿ" if kn else "Identify an item",
    "track": "ತ್ಯಾಜ್ಯ ದಾಖಲಾತಿ" if kn else "Waste tracking",
    "quiz": "ವಿಂಗಡಣೆ ರಸಪ್ರಶ್ನೆ" if kn else "Segregation quiz",
    "guide": "ಮಾರ್ಗದರ್ಶಿ ಅವಲೋಕನ" if kn else "Guide overview",
    "search": "ತ್ಯಾಜ್ಯದ ಹೆಸರನ್ನು ನಮೂದಿಸಿ" if kn else "Type a household waste item",
    "choose": "ಅಥವಾ ಉದಾಹರಣೆ ಆಯ್ಕೆಮಾಡಿ" if kn else "Or choose an example",
    "unknown": "ಈ ವಸ್ತು ಮಾರ್ಗದರ್ಶಿಯಲ್ಲಿ ಇಲ್ಲ. ಇದನ್ನು ವಿಶ್ವಾಸಾರ್ಹವಾಗಿ ವರ್ಗೀಕರಿಸಲು ಸಾಧ್ಯವಿಲ್ಲ. ಸ್ಥಳೀಯ ನಗರಪಾಲಿಕೆ ಮಾರ್ಗಸೂಚಿಗಳನ್ನು ಪರಿಶೀಲಿಸಿ." if kn else "This item is not in the guide yet. EcoSort cannot classify it reliably. Check local municipal guidance instead of guessing.",
    "instructions": "ಏನು ಮಾಡಬೇಕು" if kn else "What to do",
    "record": "ಗೃಹ ತ್ಯಾಜ್ಯ ದಾಖಲಿಸಿ" if kn else "Record household waste",
    "item": "ತ್ಯಾಜ್ಯದ ಹೆಸರು" if kn else "Waste item name",
    "category": "ವರ್ಗ" if kn else "Category",
    "kg": "ಪ್ರಮಾಣ (ಕೆ.ಜಿ.)" if kn else "Quantity (kg)",
    "date": "ದಿನಾಂಕ" if kn else "Date recorded",
    "save": "ದಾಖಲಿಸಿ" if kn else "Save waste entry",
    "weekly": "ವಾರದ ತ್ಯಾಜ್ಯ ಪ್ರಮಾಣ (ನಿಮ್ಮ ದಾಖಲೆಗಳು)" if kn else "Weekly waste quantities (your entries)",
    "records": "ನಿಮ್ಮ ದಾಖಲೆಗಳು" if kn else "Your recorded waste",
    "start": "ರಸಪ್ರಶ್ನೆ ಪ್ರಾರಂಭಿಸಿ / ಮರುಪ್ರಾರಂಭಿಸಿ" if kn else "Start / restart quiz",
    "check": "ಉತ್ತರ ಪರಿಶೀಲಿಸಿ" if kn else "Check answers",
    "score": "ನಿಮ್ಮ ಅಂಕ" if kn else "Your score"
}

st.title("♻️ EcoSort")
st.subheader(T["subtitle"])
st.write(T["intro"])
st.caption("ಈ ಆವೃತ್ತಿ ಪೂರ್ವನಿರ್ಧರಿತ ನಿಯಮಗಳನ್ನು ಬಳಸುತ್ತದೆ; AI ಚಿತ್ರ ಗುರುತಿಸುವಿಕೆ ಇಲ್ಲ." if kn else "This version uses predefined rules; it does not use AI image recognition.")
a, b, c, d = st.tabs([T["identify"], T["track"], T["quiz"], T["guide"]])

with a:
    typed = st.text_input(T["search"], placeholder="e.g. banana peel")
    choices = sorted(ITEMS.keys())
    chosen = st.selectbox(T["choose"], [""] + choices)
    query = typed.strip().lower() if typed.strip() else chosen.lower()
    if query:
        exact = query in ITEMS
        match = query if exact else next((x for x in choices if query in x or x in query), None)
        if match:
            cat, bin_name, advice, cat_kn, bin_kn, advice_kn = ITEMS[match]
            st.success(f"**{T['category']}:** {cat_kn if kn else cat}")
            st.metric("ಸೂಚಿತ ವಿಲೇವಾರಿ ವಿಧಾನ" if kn else "Suggested disposal route", bin_kn if kn else bin_name)
            st.markdown(f"**{T['instructions']}**")
            st.write(advice_kn if kn else advice)
        else:
            st.warning(T["unknown"])
            st.caption(("ಉದಾಹರಣೆಗಳು: " if kn else "Examples: ") + ", ".join(choices[:8]))

with b:
    st.markdown(f"### {T['record']}")
    cats = ["Wet / Biodegradable", "Dry / Recyclable", "Dry / Other", "Hazardous household waste", "E-waste", "Other / Unsure"]
    with st.form("record_form", clear_on_submit=True):
        item = st.text_input(T["item"])
        cat = st.selectbox(T["category"], cats)
        kg = st.number_input(T["kg"], min_value=0.01, max_value=10000.0, value=0.5, step=0.1)
        dt = st.date_input(T["date"], value=date.today(), max_value=date.today())
        save = st.form_submit_button(T["save"], type="primary")
        if save:
            if not item.strip():
                st.error("ದಯವಿಟ್ಟು ತ್ಯಾಜ್ಯದ ಹೆಸರನ್ನು ನಮೂದಿಸಿ." if kn else "Please enter a waste item name.")
            else:
                with sqlite3.connect(DB) as conn:
                    conn.execute("INSERT INTO waste_log(item, category, kg, entry_date) VALUES (?, ?, ?, ?)", (item.strip(), cat, float(kg), dt.isoformat()))
                    conn.commit()
                st.success("ದಾಖಲೆ ಉಳಿಸಲಾಗಿದೆ!" if kn else "Waste entry saved!")
                st.rerun()
    logs = read_logs()
    if not logs.empty:
        logs["entry_date"] = pd.to_datetime(logs["entry_date"])
        end = pd.Timestamp(date.today())
        start = end - pd.Timedelta(days=6)
        week = logs[(logs.entry_date >= start) & (logs.entry_date <= end)]
        st.markdown(f"### {T['weekly']}")
        if week.empty:
            st.info("ಕಳೆದ 7 ದಿನಗಳಲ್ಲಿ ದಾಖಲೆಗಳಿಲ್ಲ." if kn else "No entries recorded in the last 7 days yet.")
        else:
            daily = week.groupby(week.entry_date.dt.strftime("%Y-%m-%d"))["kg"].sum().sort_index()
            st.bar_chart(daily)
            st.markdown("**ವರ್ಗದ ಪ್ರಕಾರ ವಾರದ ಮೊತ್ತ**" if kn else "**Weekly total by category**")
            st.bar_chart(week.groupby("category")["kg"].sum())
            st.metric("ಈ ವಾರದ ಒಟ್ಟು" if kn else "Total recorded this week", f"{week.kg.sum():.2f} kg")
        st.markdown(f"### {T['records']}")
        logs["entry_date"] = logs["entry_date"].dt.strftime("%Y-%m-%d")
        st.dataframe(logs, width="stretch", hide_index=True)
        st.download_button("CSV ಡೌನ್‌ಲೋಡ್" if kn else "Download records as CSV", logs.to_csv(index=False).encode("utf-8"), "ecosort_waste_log.csv", "text/csv")
    else:
        st.info("ಚಾರ್ಟ್ ನೋಡಲು ಮೊದಲ ದಾಖಲೆಯನ್ನು ಸೇರಿಸಿ." if kn else "Add your first entry to generate a tracking chart.")

with c:
    st.markdown(f"### {T['quiz']}")
    if st.button(T["start"]):
        st.session_state.quiz_started = True
        st.session_state.quiz_done = False
    if st.session_state.get("quiz_started", False):
        with st.form("quiz_form"):
            answers = []
            for i, (q, opts, correct, why, why_kn) in enumerate(QUIZ):
                q_show = [q, 
                    "What should you do with a household battery?",
                    "How should clean, dry paper generally be handled?",
                    "What should you do with an old mobile phone?",
                    "Why separate wet and dry waste?"][i]
                opts_show = opts
                if kn:
                    q_show = [
                        "ಬಾಳೆಹಣ್ಣಿನ ಸಿಪ್ಪೆಯನ್ನು ಎಲ್ಲಿ ಹಾಕಬೇಕು?",
                        "ಮನೆಯ ಬ್ಯಾಟರಿಯನ್ನು ಏನು ಮಾಡಬೇಕು?",
                        "ಸ್ವಚ್ಛ, ಒಣ ಕಾಗದವನ್ನು ಹೇಗೆ ನಿರ್ವಹಿಸಬೇಕು?",
                        "ಹಳೆಯ ಮೊಬೈಲ್ ಫೋನ್ ಅನ್ನು ಏನು ಮಾಡಬೇಕು?",
                        "ಒದ್ದೆ ಮತ್ತು ಒಣ ತ್ಯಾಜ್ಯವನ್ನು ಏಕೆ ಬೇರ್ಪಡಿಸಬೇಕು?"
                    ][i]
                    opts_show = [
                        ["ಒದ್ದೆ / ಜೈವಿಕ ತ್ಯಾಜ್ಯ", "ಇ-ತ್ಯಾಜ್ಯ", "ಬ್ಯಾಟರಿ ಸಂಗ್ರಹಣೆ"],
                        ["ಆಹಾರದೊಂದಿಗೆ ಬೆರೆಸಿ", "ಬ್ಯಾಟರಿ ಸಂಗ್ರಹಣಾ ಕೇಂದ್ರಕ್ಕೆ ನೀಡಿ", "ಕಾಂಪೋಸ್ಟ್‌ಗೆ ಹಾಕಿ"],
                        ["ಆಹಾರದೊಂದಿಗೆ ಹಾಕಿ", "ಒಣಗಿರಿಸಿ ಮರುಬಳಕೆ ಮಾಡಿ", "ಬ್ಯಾಟರಿಗಳೊಂದಿಗೆ ಹಾಕಿ"],
                        ["ಒದ್ದೆ ತ್ಯಾಜ್ಯ", "ಹೊರಗೆ ಸುಡಿ", "ಅಧಿಕೃತ ಇ-ತ್ಯಾಜ್ಯ ಕೇಂದ್ರಕ್ಕೆ ನೀಡಿ"],
                        ["ಮರುಬಳಕೆ ಮತ್ತು ಕಾಂಪೋಸ್ಟಿಂಗ್‌ಗೆ ಸಹಾಯ", "ಎಲ್ಲಾ ತ್ಯಾಜ್ಯ ಅಪಾಯಕಾರಿ", "ಸಂಗ್ರಹಣೆ ಬೇಡ"]
                    ][i]
                answers.append(st.radio(q_show, opts_show, key=f"q{i}_{lang}"))
            check = st.form_submit_button(T["check"])
        if check:
            score = 0
            for i, ans in enumerate(answers):
                correct = QUIZ[i][2]
                correct_option = ([
                    ["ಒದ್ದೆ / ಜೈವಿಕ ತ್ಯಾಜ್ಯ", "ಇ-ತ್ಯಾಜ್ಯ", "ಬ್ಯಾಟರಿ ಸಂಗ್ರಹಣೆ"],
                    ["ಆಹಾರದೊಂದಿಗೆ ಬೆರೆಸಿ", "ಬ್ಯಾಟರಿ ಸಂಗ್ರಹಣಾ ಕೇಂದ್ರಕ್ಕೆ ನೀಡಿ", "ಕಾಂಪೋಸ್ಟ್‌ಗೆ ಹಾಕಿ"],
                    ["ಆಹಾರದೊಂದಿಗೆ ಹಾಕಿ", "ಒಣಗಿರಿಸಿ ಮರುಬಳಕೆ ಮಾಡಿ", "ಬ್ಯಾಟರಿಗಳೊಂದಿಗೆ ಹಾಕಿ"],
                    ["ಒದ್ದೆ ತ್ಯಾಜ್ಯ", "ಹೊರಗೆ ಸುಡಿ", "ಅಧಿಕೃತ ಇ-ತ್ಯಾಜ್ಯ ಕೇಂದ್ರಕ್ಕೆ ನೀಡಿ"],
                    ["ಮರುಬಳಕೆ ಮತ್ತು ಕಾಂಪೋಸ್ಟಿಂಗ್‌ಗೆ ಸಹಾಯ", "ಎಲ್ಲಾ ತ್ಯಾಜ್ಯ ಅಪಾಯಕಾರಿ", "ಸಂಗ್ರಹಣೆ ಬೇಡ"]
                ][i][correct] if kn else QUIZ[i][1][correct])
                if ans == correct_option:
                    score += 1
            st.session_state.quiz_score = score
            st.session_state.quiz_answers = answers
            st.session_state.quiz_done = True
        if st.session_state.get("quiz_done", False):
            st.success(f"{T['score']}: {st.session_state.quiz_score}/{len(QUIZ)}")
            for i, (q, opts, correct, why, why_kn) in enumerate(QUIZ):
                st.markdown(f"**{i+1}. {opts[correct]}**" if not kn else f"**{i+1}. {['ಒದ್ದೆ / ಜೈವಿಕ ತ್ಯಾಜ್ಯ','ಬ್ಯಾಟರಿ ಸಂಗ್ರಹಣಾ ಕೇಂದ್ರಕ್ಕೆ ನೀಡಿ','ಒಣಗಿರಿಸಿ ಮರುಬಳಕೆ ಮಾಡಿ','ಅಧಿಕೃತ ಇ-ತ್ಯಾಜ್ಯ ಕೇಂದ್ರಕ್ಕೆ ನೀಡಿ','ಮರುಬಳಕೆ ಮತ್ತು ಕಾಂಪೋಸ್ಟಿಂಗ್‌ಗೆ ಸಹಾಯ'][i]}**")
                st.caption(why_kn if kn else why)

with d:
    st.markdown("### " + ("ಮಾರ್ಗದರ್ಶಿಯಲ್ಲಿನ ಮಾದರಿ ವಸ್ತುಗಳು" if kn else "Example items in the guide"))
    rows = [{"Item": name, "Category": values[0], "Suggested route": values[1]} for name, values in ITEMS.items()]
    guide = pd.DataFrame(rows)
    counts = guide["Category"].value_counts()
    st.bar_chart(counts)
    st.caption("ಈ ಚಾರ್ಟ್ ಮಾರ್ಗದರ್ಶಿಯ ನಮೂದುಗಳನ್ನು ಎಣಿಸುತ್ತದೆ; ನಿಜವಾದ ತ್ಯಾಜ್ಯ ಪ್ರಮಾಣವಲ್ಲ." if kn else "This chart counts sample guide entries, not actual household waste quantities.")
    st.dataframe(guide, width="stretch", hide_index=True)
