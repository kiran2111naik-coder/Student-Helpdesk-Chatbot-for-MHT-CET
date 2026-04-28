import streamlit as st
import pandas as pd
import re

# -------------------------------
# DATA
# -------------------------------
def load_data():
    data = [
        ["COEP Pune","Computer Engineering",2024,99.5,98.7,96.2,93.5],
        ["VJTI Mumbai","IT",2024,99.2,98.5,95.8,92.8],
        ["SPIT Mumbai","Computer Engineering",2024,98.8,97.9,94.2,91.0],
        ["PCCOE Pune","Computer Engineering",2024,97.5,96.0,92.5,89.5],
        ["MIT WPU Pune","IT",2024,96.5,94.8,90.5,87.0],
        ["VIT Pune","IT",2024,97.8,96.5,93.5,90.5],
    ]

    cols = ["College","Branch","Year","OPEN","OBC","SC","ST"]
    return pd.DataFrame(data, columns=cols)

df = load_data()

# -------------------------------
# BRANCH SUGGESTION
# -------------------------------
def suggest_branch(p):
    if p >= 98:
        return "💻 Computer / IT"
    elif p >= 95:
        return "🖥️ IT / EXTC"
    elif p >= 90:
        return "⚙️ Mechanical / Electrical"
    else:
        return "🏗️ Civil / Other"

# -------------------------------
# CHATBOT
# -------------------------------
def chatbot(user_input):
    text = user_input.lower()

    if "percentile" in text or "%" in text:
        try:
            perc = float(re.findall(r'\d+\.?\d*', text)[0])

            category = "OPEN"
            if "obc" in text:
                category = "OBC"
            elif "sc" in text:
                category = "SC"
            elif "st" in text:
                category = "ST"

            if category not in df.columns:
                category = "OPEN"

            result = df[df[category] <= perc]

            if result.empty:
                result = df.sort_values(by=category, ascending=False)

            result = result.drop_duplicates(subset=["College"])
            result = result.sort_values(by=category, ascending=False).head(5)

            res = "🎯 Top Colleges:\n\n"
            for _, row in result.iterrows():
                res += f"{row['College']} - {row['Branch']} ({row[category]}%)\n"

            res += "\n🎯 Suggested Branch: " + suggest_branch(perc)
            return res

        except:
            return "Enter like: 95 percentile OBC"

    if "mht cet" in text:
        return "MHT CET is engineering entrance exam in Maharashtra."
    elif "eligibility" in text:
        return "12th PCM required."
    elif "cap" in text:
        return "CAP is centralized admission process."
    elif "document" in text:
        return "Marksheets + CET scorecard required."
    else:
        return "Ask about MHT CET or enter percentile like 95 OBC"

# -------------------------------
# TREND DATA (SIMPLE SIMULATION)
# -------------------------------
def show_trend(college):
    sample = df[df["College"] == college].copy()

    if sample.empty:
        st.warning("No data")
        return

    sample = sample.set_index("Branch")[["OPEN","OBC","SC","ST"]]
    st.bar_chart(sample)

# -------------------------------
# UI
# -------------------------------
st.set_page_config(page_title="MHT CET App")

st.title("🎓 MHT-CET Counselling App (FIXED VERSION)")

menu = st.sidebar.selectbox("Menu", ["Predictor", "Trend", "Chatbot"])

# -------------------------------
# PREDICTOR
# -------------------------------
if menu == "Predictor":

    perc = st.slider("Percentile", 50, 100, 90)
    category = st.selectbox("Category", ["OPEN","OBC","SC","ST"])

    if category not in df.columns:
        category = "OPEN"

    result = df[df[category] <= perc]

    if result.empty:
        result = df.sort_values(by=category, ascending=False)

    result = result.drop_duplicates(subset=["College"])
    result = result.sort_values(by=category, ascending=False).head(10)

    st.subheader("🎯 Top Colleges")
    st.dataframe(result)

    st.success(suggest_branch(perc))

# -------------------------------
# TREND (RESTORED)
# -------------------------------
elif menu == "Trend":

    college = st.selectbox("Select College", df["College"].unique())

    if st.button("Show Trend"):
        show_trend(college)

# -------------------------------
# CHATBOT
# -------------------------------
elif menu == "Chatbot":

    st.subheader("💬 Chatbot")

    if "chat" not in st.session_state:
        st.session_state.chat = []

    user_input = st.chat_input("Type your message...")

    if user_input:
        reply = chatbot(user_input)

        st.session_state.chat.append(("You", user_input))
        st.session_state.chat.append(("Bot", reply))

    for sender, msg in st.session_state.chat:
        if sender == "You":
            with st.chat_message("user"):
                st.write(msg)
        else:
            with st.chat_message("assistant"):
                st.write(msg)
