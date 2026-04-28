import streamlit as st
import pandas as pd
import re

# -------------------------------
# DATA (TOP COLLEGES SAMPLE)
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
# CHATBOT (NO ML - SAFE VERSION)
# -------------------------------
def chatbot(user_input):
    text = user_input.lower()

    # Percentile logic
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

            result = df[df[category] <= perc + 1]

            if result.empty:
                result = df.sort_values(by=category, ascending=False)

            result = result.drop_duplicates(subset=["College"])
            result = result.sort_values(by=category, ascending=False).head(5)

            response = "🎯 Top Colleges:\n\n"

            for _, row in result.iterrows():
                response += f"{row['College']} - {row['Branch']} ({row[category]}%)\n"

            response += "\n🎯 Suggested Branch: " + suggest_branch(perc)
            return response

        except:
            return "Enter like: 95 percentile OBC"

    # Simple FAQ
    if "mht cet" in text:
        return "MHT CET is engineering entrance exam in Maharashtra."
    elif "eligibility" in text:
        return "12th PCM required for MHT CET."
    elif "cap" in text:
        return "CAP is centralized admission process."
    elif "document" in text:
        return "You need marksheet, CET scorecard, ID proof."
    else:
        return "Ask about MHT CET or enter percentile like 95 OBC"

# -------------------------------
# UI
# -------------------------------
st.set_page_config(page_title="MHT CET App")

st.title("🎓 MHT-CET Counselling App (Stable Version)")

menu = st.sidebar.selectbox("Menu", ["Predictor", "Chatbot"])

# -------------------------------
# PREDICTOR
# -------------------------------
if menu == "Predictor":

    perc = st.slider("Percentile", 50, 100, 90)
    category = st.selectbox("Category", ["OPEN","OBC","SC","ST"])

    if category not in df.columns:
        category = "OPEN"

    result = df[df[category] <= perc + 1]

    if result.empty:
        result = df.sort_values(by=category, ascending=False)

    result = result.drop_duplicates(subset=["College"])
    result = result.sort_values(by=category, ascending=False).head(10)

    st.subheader("🎯 Top Colleges")
    st.dataframe(result)

    st.success(suggest_branch(perc))

# -------------------------------
# CHATBOT (FIXED)
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
