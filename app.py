import streamlit as st
import os
import pdfplumber
import docx
import pandas as pd

# === Functions ===

def load_keywords(file_path="keywords.txt"):
    with open(file_path, "r") as file:
        return [line.strip().lower() for line in file if line.strip()]

def extract_text_from_pdf(file):
    text = ''
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            content = page.extract_text()
            if content:
                text += content + '\n'
    return text

def extract_text_from_docx(file):
    doc = docx.Document(file)
    return "\n".join([p.text for p in doc.paragraphs])

def extract_resume_text(uploaded_file):
    if uploaded_file.name.endswith(".pdf"):
        return extract_text_from_pdf(uploaded_file)
    elif uploaded_file.name.endswith(".docx"):
        return extract_text_from_docx(uploaded_file)
    else:
        return ""

def score_resume(text, keywords):
    text = text.lower()
    matched = [kw for kw in keywords if kw in text]
    return len(matched), matched

# === UI ===

st.title("📄 Resume Screener (Full Stack Dev Edition)")
st.write("Upload multiple resumes and screen them based on keyword matches.")

uploaded_files = st.file_uploader("Upload resumes (PDF or DOCX)", type=["pdf", "docx"], accept_multiple_files=True)

keywords = load_keywords()

if uploaded_files:
    results = []

    for resume in uploaded_files:
        text = extract_resume_text(resume)
        score, matched_keywords = score_resume(text, keywords)
        match_percent = round((score / len(keywords)) * 100, 2)

        results.append({
            "filename": resume.name,
            "score": score,
            "match %": match_percent,
            "matched_keywords": ", ".join(matched_keywords)
        })

    df = pd.DataFrame(results).sort_values(by="score", ascending=False)
    st.success("✅ Screening complete!")
    st.dataframe(df)

    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Download Results as CSV", csv, "results.csv", "text/csv")
else:
    st.info("Please upload some resumes to get started.")
