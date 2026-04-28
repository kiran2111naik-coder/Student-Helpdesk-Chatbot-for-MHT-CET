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

            # fallback safety
            if category not in df.columns:
                category = "OPEN"

            df["diff"] = abs(df[category] - perc)
            result = df.sort_values("diff").head(5)
            result = result.drop_duplicates(subset=["College"])

            res = "🎯 Top Colleges (Best Match):\n\n"

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
# TREND (FIXED & STABLE)
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

st.title("🎓 MHT-CET Counselling App (FINAL STABLE VERSION)")

menu = st.sidebar.selectbox("Menu", ["Predictor", "Trend", "Chatbot"])

# -------------------------------
# PREDICTOR (FIXED DYNAMIC LOGIC)
# -------------------------------
if menu == "Predictor":

    st.subheader("🎯 College Predictor")

    perc = st.slider("Enter Percentile", 50, 100, 90)
    category = st.selectbox("Category", ["OPEN","OBC","SC","ST"])

    if category not in df.columns:
        category = "OPEN"

    # 🔥 SMART MATCHING LOGIC (FIXED)
    df["diff"] = abs(df[category] - perc)

    result = df.sort_values("diff").head(10)
    result = result.drop_duplicates(subset=["College"])

    st.write("📊 Best Matching Colleges Based on Your Score:")

    st.dataframe(result.drop(columns=["diff"]))

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
