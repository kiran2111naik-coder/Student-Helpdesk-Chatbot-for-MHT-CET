import streamlit as st
import pandas as pd
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# -------------------------------
# BUILT-IN DATA
# -------------------------------
def load_data():
    data = [
        ["COEP Pune","Computer Engineering",2024,99.5,99.3,99.6,98.7,98.5,98.8,96.2,96.0,96.5,93.5,93.0,94.0],
        ["COEP Pune","Mechanical Engineering",2024,97.2,97.0,97.5,95.8,95.5,96.0,92.1,91.8,92.5,89.0,88.5,89.5],
        ["VJTI Mumbai","IT",2024,99.2,99.0,99.3,98.5,98.2,98.6,95.8,95.5,96.0,92.8,92.3,93.0],
        ["SPIT Mumbai","Computer Engineering",2024,98.8,98.5,99.0,97.9,97.5,98.0,94.2,94.0,94.5,91.0,90.5,91.5],
        ["PCCOE Pune","Computer Engineering",2024,97.5,97.2,97.8,96.0,95.8,96.2,92.5,92.0,93.0,89.5,89.0,90.0],
        ["MIT WPU Pune","IT",2024,96.5,96.2,96.8,94.8,94.5,95.0,90.5,90.0,91.0,87.0,86.5,87.5],
        ["DY Patil Pune","Computer Engineering",2024,95.8,95.5,96.0,94.0,93.5,94.5,89.5,89.0,90.0,85.5,85.0,86.0],
        ["VIT Pune","IT",2024,97.8,97.5,98.0,96.5,96.0,97.0,93.5,93.0,94.0,90.5,90.0,91.0],
    ]

    cols = ["College","Branch","Year","OPEN","OPEN_F","OPEN_M",
            "OBC","OBC_F","OBC_M","SC","SC_F","SC_M","ST","ST_F","ST_M"]

    return pd.DataFrame(data, columns=cols)

df = load_data()

# -------------------------------
# DATA EXPANSION
# -------------------------------
def expand_data(df):
    new_rows = []

    cutoff_cols = ["OPEN","OPEN_F","OPEN_M","OBC","OBC_F","OBC_M",
                   "SC","SC_F","SC_M","ST","ST_F","ST_M"]

    for _, row in df.iterrows():
        for delta in [-2, -1, 0, 1, 2]:
            new_row = row.copy()

            for col in cutoff_cols:
                if col in df.columns:
                    new_row[col] = max(50, min(100, row[col] + delta))

            new_rows.append(new_row)

    return pd.DataFrame(new_rows).drop_duplicates()

df = expand_data(df)

# -------------------------------
# FAQ + NLP
# -------------------------------
faq_q = ["What is MHT CET?", "Eligibility?", "CAP round?", "Documents?"]
faq_a = [
    "MHT CET is an engineering entrance exam.",
    "12th PCM required.",
    "CAP is admission process.",
    "Marksheets + CET scorecard required."
]

vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(faq_q)

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
# CHATBOT FUNCTION
# -------------------------------
def chatbot(user_input):
    text = user_input.lower()

    if any(word in text for word in ["percentile", "%"]):
        try:
            perc = float(re.findall(r'\d+\.?\d*', text)[0])

            category = "OPEN"
            if "obc" in text: category = "OBC"
            elif "sc" in text: category = "SC"
            elif "st" in text: category = "ST"

            col = category
            if "female" in text: col += "_F"
            elif "male" in text: col += "_M"

            result = df[df[col] <= perc + 1]

            if result.empty:
                result = df.sort_values(by=col, ascending=False)

            # REMOVE DUPLICATES
            result = result.drop_duplicates(subset=["College", "Branch"])

            # SORT & LIMIT
            result = result.sort_values(by=col, ascending=False).head(5)

            res = "🎯 Top Colleges:\n\n"
            for _, row in result.iterrows():
                res += f"{row['College']} - {row['Branch']} ({row[col]}%)\n"

            res += "\n🎯 Suggested Branch: " + suggest_branch(perc)
            return res

        except:
            return "Enter like: 95 percentile OBC female"

    vec = vectorizer.transform([user_input])
    sim = cosine_similarity(vec, X)

    if sim.max() < 0.4:
        return "Ask about MHT CET or enter percentile like 95% OBC"

    return faq_a[sim.argmax()]

# -------------------------------
# TREND GRAPH (NO MATPLOTLIB)
# -------------------------------
def show_trend(college, branch, category):
    data = df[(df["College"] == college) & (df["Branch"] == branch)]
    data = data.sort_values("Year")

    if data.empty:
        st.warning("No data available")
        return

    chart_data = data.set_index("Year")[category]
    st.line_chart(chart_data)

# -------------------------------
# UI
# -------------------------------
st.set_page_config(page_title="MHT CET App")

st.title("🎓 MHT-CET Counselling App")

menu = st.sidebar.selectbox("Menu", ["Predictor", "Trend", "Chatbot"])

# -------------------------------
# PREDICTOR
# -------------------------------
if menu == "Predictor":
    perc = st.slider("Percentile", 50, 100, 90)
    category = st.selectbox("Category", ["OPEN","OBC","SC","ST"])
    gender = st.selectbox("Gender", ["Neutral","Female","Male"])

    col = category
    if gender == "Female": col += "_F"
    elif gender == "Male": col += "_M"

    result = df[df[col] <= perc + 1]

    if result.empty:
        result = df.sort_values(by=col, ascending=False)

    result = result.drop_duplicates(subset=["College","Branch"])
    result = result.sort_values(by=col, ascending=False).head(10)

    st.subheader("🎯 Top Colleges")
    st.dataframe(result)

    st.success(suggest_branch(perc))

# -------------------------------
# TREND
# -------------------------------
elif menu == "Trend":
    college = st.selectbox("College", df["College"].unique())
    branch = st.selectbox("Branch", df["Branch"].unique())
    category = st.selectbox("Category", ["OPEN","OBC","SC","ST"])

    if st.button("Show Trend"):
        show_trend(college, branch, category)

# -------------------------------
# CHATBOT
# -------------------------------
elif menu == "Chatbot":

    st.subheader("💬 MHT-CET Chatbot")

    if "chat" not in st.session_state:
        st.session_state.chat = []

    user_input = st.chat_input("Type your message...")

    if user_input:
        response = chatbot(user_input)

        st.session_state.chat.append(("You", user_input))
        st.session_state.chat.append(("Bot", response))

    for sender, msg in st.session_state.chat:
        if sender == "You":
            with st.chat_message("user"):
                st.write(msg)
        else:
            with st.chat_message("assistant"):
                st.write(msg)
