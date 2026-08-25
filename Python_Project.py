import streamlit as st
from pypdf import PdfReader
import re

# ----------------------------
# Function to Extract Text
# ----------------------------
def extract_resume_text(uploaded_file):
    reader = PdfReader(uploaded_file)

    text = ""

    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + " "

    return text


# ----------------------------
# Function to Clean Text
# ----------------------------
def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


# ----------------------------
# Streamlit UI
# ----------------------------
st.title("Resume Parser")

uploaded_file = st.file_uploader(
    "Upload Resume (PDF)",
    type=["pdf"]
)

job_description = st.text_area(
    "Paste Job Description",
    height=250
)

# ----------------------------
# Process
# ----------------------------
if st.button("Analyze Resume"):

    if uploaded_file is None:
        st.warning("Please upload a Resume.")
        st.stop()

    if job_description.strip() == "":
        st.warning("Please enter Job Description.")
        st.stop()

    # ------------------------
    # Extract Resume
    # ------------------------

    resume = extract_resume_text(uploaded_file)

    clean_resume = clean_text(resume)
    clean_jd = clean_text(job_description)

    resume_words = set(clean_resume.split())
    jd_words = set(clean_jd.split())

    # ------------------------
    # Matching
    # ------------------------

    matched_words = sorted(resume_words.intersection(jd_words))
    missing_words = sorted(jd_words.difference(resume_words))

    # ------------------------
    # ATS Score
    # ------------------------

    if len(jd_words) != 0:
        score = len(matched_words) / len(jd_words) * 100
    else:
        score = 0

    # ------------------------
    # Highlight Function
    # ------------------------

    def highlight_text(text, matched):

        highlighted = []

        for word in text.split():

            clean = re.sub(r'[^a-zA-Z]', '', word).lower()

            if clean in matched:
                highlighted.append(
                    f"<span style='background-color:#90EE90;"
                    f"padding:2px;border-radius:4px;'>"
                    f"{word}</span>"
                )
            else:
                highlighted.append(word)

        return " ".join(highlighted)

    # ------------------------
    # ATS REPORT
    # ------------------------

    st.header("📄 ATS Resume Report")

    st.metric("ATS Score", f"{score:.2f}%")

    st.progress(score / 100)

    # ------------------------
    # Matched Skills
    # ------------------------

    st.subheader("✅ Matched Keywords")

    if matched_words:
        st.success(", ".join(matched_words))
    else:
        st.error("No matching keywords found.")

    # ------------------------
    # Missing Skills
    # ------------------------

    st.subheader("❌ Missing Keywords")

    if missing_words:
        st.warning(", ".join(missing_words))
    else:
        st.success("Excellent! No missing keywords.")

    # ------------------------
    # Statistics
    # ------------------------

    col1, col2, col3 = st.columns(3)

    col1.metric("Resume Keywords", len(resume_words))
    col2.metric("JD Keywords", len(jd_words))
    col3.metric("Matched", len(matched_words))

    # ------------------------
    # Highlight Resume
    # ------------------------

    st.subheader("📑 Resume (Matched Words Highlighted)")

    st.markdown(
        highlight_text(resume, matched_words),
        unsafe_allow_html=True
    )

    # ------------------------
    # Highlight JD
    # ------------------------

    st.subheader("📝 Job Description (Matched Words Highlighted)")

    st.markdown(
        highlight_text(job_description, matched_words),
        unsafe_allow_html=True
    )

    # ------------------------
    # Recommendation
    # ------------------------

    st.subheader("💡 Recommendation")

    if score >= 80:
        st.success("Excellent match! Your resume is well aligned with the Job Description.")

    elif score >= 60:
        st.info("Good match. Consider adding the missing keywords if you have those skills.")

    elif score >= 40:
        st.warning("Average match. Your resume needs improvement.")

    else:
        st.error("Low ATS score. Update your resume to include more relevant skills.")