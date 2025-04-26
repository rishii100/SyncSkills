import streamlit as st
import google.generativeai as genai
import os
import PyPDF2 as pdf
from dotenv import load_dotenv
import fitz  # PyMuPDF
from PIL import Image
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Load environment variables
load_dotenv()

# Configure Gemini API Key
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Convert full PDF to images (multi-page support)
def convert_pdf_to_images(file_bytes):
    pdf_document = fitz.open(stream=file_bytes)
    images = []
    for page in pdf_document:
        pix = page.get_pixmap(matrix=fitz.Matrix(300/72, 300/72))
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        images.append(img)
    pdf_document.close()
    return images

# Send prompt to Gemini
def get_gemini_response(input_prompt, pdf_imgs, job_desc, struc):
    model = genai.GenerativeModel('gemini-1.5-pro')
    response = model.generate_content([input_prompt, *pdf_imgs, job_desc, struc])
    return response.text

# Create a simple PDF file from text
def create_pdf(text):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    y = height - 40  # Start near the top

    for line in text.split('\n'):
        c.drawString(40, y, line)
        y -= 15  # Line spacing
        if y < 40:
            c.showPage()
            y = height - 40

    c.save()
    buffer.seek(0)
    return buffer

# Prompt template
input_prompt = """
Hey, act like a highly skilled Applicant Tracking System (ATS) expert with deep knowledge of the tech industry.
Your job is to evaluate resumes against the given job description. Assign a strict and realistic match percentage.
Be detailed about missing skills or improvements needed.

Resume:
"""

# Structure for Gemini to follow
struc = """
Respond in the following format:
- "Job-Description Match: %"
- "Describe how to improve the given resume."
Make the evaluation strict and professional.
"""

# --------------------- Streamlit App ------------------------

st.title("SyncSkills")
st.caption("Your Achievements, Your Career, Our Revolution 🚀")

st.markdown("### Step 1: Paste the Job Description")
jd = st.text_area("Job Description", height=200)

st.markdown("### Step 2: Upload Your Resume")
uploaded_file = st.file_uploader("Upload your resume (PDF)", type="pdf", help="Only PDF files are supported.")

if uploaded_file:
    st.success("Resume Uploaded Successfully ✅")

submit = st.button("Submit")

if submit:
    if not uploaded_file or not jd.strip():
        st.error("Please upload a resume and paste a job description.")
    else:
        with st.spinner('Analyzing your resume with AI...'):
            file_bytes = uploaded_file.read()
            pdf_imgs = convert_pdf_to_images(BytesIO(file_bytes))
            job_desc = f"The job description: {jd}"
            response = get_gemini_response(input_prompt, pdf_imgs, job_desc, struc)
        
        # Display Results
        st.subheader("📄 Evaluation Result:")
        try:
            lines = response.split("\n")
            match_line = next((line for line in lines if "Match" in line), "Match Percentage: Not found")
            improvement_lines = [line for line in lines if "improve" in line.lower() or "missing" in line.lower()]

            st.metric(label="Job Match %", value=match_line.split(":")[1].strip() if ":" in match_line else "N/A")
            st.markdown("### Suggestions to Improve Your Resume:")
            for imp in improvement_lines:
                st.write(f"🔹 {imp}")
            
            # Full Response (expandable)
            with st.expander("See Full AI Evaluation"):
                st.markdown(response)

            # PDF download section
            pdf_file = create_pdf(response)
            st.download_button(
                label="📄 Download Evaluation Report",
                data=pdf_file,
                file_name="resume_evaluation.pdf",
                mime="application/pdf"
            )

        except Exception as e:
            st.error("Error parsing AI response. Here's the full text:")
            st.text(response)
