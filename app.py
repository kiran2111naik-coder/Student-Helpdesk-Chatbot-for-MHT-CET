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
        ["DY Patil Pune","IT",2024,95.8,94.0,90.0,85.5],
        ["Sinhgad Pune","Computer Engineering",2024,94.5,92.0,88.5,84.0],
        ["AISSMS Pune","IT",2024,93.0,90.5,86.0,82.0],
        ["NIT Nagpur","Computer Engineering",2024,98.0,96.5,93.0,90.0],
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

            temp = df.copy()
            temp["gap"] = temp[category] - perc
            temp["score"] = abs(temp["gap"])

            result = temp.sort_values(["score", category]).drop_duplicates("College").head(10)

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
# TREND
# -------------------------------
def show_trend(college):

    st.subheader(f"📊 Trend Analysis - {college}")

    data = df[df["College"] == college]

    if data.empty:
        st.warning("No data available")
        return

    chart = data.set_index("Branch")[["OPEN","OBC","SC","ST"]]

    st.bar_chart(chart)
    st.dataframe(data)

# -------------------------------
# UI
# -------------------------------
st.set_page_config(page_title="MHT CET App")

st.title("🎓 MHT-CET Counselling App (FINAL AI-STYLE PREDICTOR)")

menu = st.sidebar.selectbox("Menu", ["Predictor", "Trend", "Chatbot"])

# -------------------------------
# PREDICTOR (ULTRA IMPROVED VERSION)
# -------------------------------
if menu == "Predictor":

    st.subheader("🎯 Smart Counselling Predictor (AI Logic)")

    perc = st.slider("Enter Percentile", 50, 100, 90)
    category = st.selectbox("Category", ["OPEN","OBC","SC","ST"])

    temp = df.copy()

    if category not in temp.columns:
        category = "OPEN"

    # -------------------------------
    # SMART 3-ZONE SYSTEM
    # -------------------------------
    temp["gap"] = temp[category] - perc

    safe_zone = temp[temp["gap"] <= -2].copy()
    target_zone = temp[(temp["gap"] > -2) & (temp["gap"] <= 3)].copy()
    dream_zone = temp[temp["gap"] > 3].copy()

    safe_zone["score"] = abs(safe_zone["gap"]) * 0.5
    target_zone["score"] = abs(target_zone["gap"]) * 1.0
    dream_zone["score"] = abs(dream_zone["gap"]) * 1.5

    safe_zone["priority"] = 1
    target_zone["priority"] = 2
    dream_zone["priority"] = 3

    result = pd.concat([safe_zone, target_zone, dream_zone])

    result = result.sort_values(
        by=["priority", "score", category],
        ascending=[True, True, False]
    )

    result = result.drop_duplicates("College")

    result = result.head(max(20, len(result)))

    st.write("📊 AI-Style Counselling Results:")

    st.dataframe(result.drop(columns=["gap","score","priority"]))

    st.success(suggest_branch(perc))

# -------------------------------
# TREND
# -------------------------------
elif menu == "Trend":

    st.subheader("📊 Trend Section")

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
