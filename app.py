import streamlit as st
import google.generativeai as genai
import os
import fitz  # PyMuPDF
from PIL import Image
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Function: Convert uploaded PDF to images
def convert_pdf_to_image(uploaded_file, page_number=0):
    pdf_document = fitz.open(stream=BytesIO(uploaded_file.read()))
    page = pdf_document[page_number]
    pix = page.get_pixmap(matrix=fitz.Matrix(300/72, 300/72))
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    pdf_document.close()
    return img

# Function: Get response from Gemini
def get_gemini_response(input_prompt, pdf_img, job_desc, struc):
    model = genai.GenerativeModel('gemini-1.5-pro')
    response = model.generate_content([input_prompt, pdf_img, job_desc, struc])
    return response.text

# Function: Create PDF file from text
def create_pdf(text):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    y = height - 40

    for line in text.split('\n'):
        c.drawString(40, y, line)
        y -= 15
        if y < 40:
            c.showPage()
            y = height - 40

    c.save()
    buffer.seek(0)
    return buffer

# --------------- Streamlit UI ---------------

st.title("SyncSkills 🚀")
st.caption("Your Achievements, Your Career, Our Revolution.")

# Step 1: Get Job Description
st.markdown("### Step 1: Paste the Job Description")
jd = st.text_area("Job Description", height=200)

# Step 2: Upload Resume
st.markdown("### Step 2: Upload Your Resume (PDF)")
uploaded_file = st.file_uploader("Upload your resume here", type=["pdf"])

if uploaded_file:
    st.success("✅ Resume Uploaded Successfully!")

# Input prompt templates
input_prompt = """
Hey, act like a skilled ATS (Applicant Tracking System) expert with deep knowledge of tech roles.
Strictly evaluate the resume based on the given job description.
Assign a strict realistic match percentage and list missing keywords or improvements.

Resume:
"""

struc = """
Respond like this:
- "Job-Description Match: %"
- "Describe how to improve the given resume."

Be strict and professional.
"""

submit = st.button("Submit")

if submit:
    if not uploaded_file or not jd.strip():
        st.error("⚠️ Please upload a resume and enter a job description.")
    else:
        with st.spinner("Analyzing your resume..."):
            pdf_img = convert_pdf_to_image(uploaded_file)
            job_desc = f"The job description: {jd}"
            response = get_gemini_response(input_prompt, pdf_img, job_desc, struc)

        # Display response
        st.subheader("📄 Evaluation Result")
        st.markdown(response)

        # Create downloadable PDF
        pdf_file = create_pdf(response)

        # Download button
        st.download_button(
            label="📄 Download Evaluation Report",
            data=pdf_file,
            file_name="resume_evaluation.pdf",
            mime="application/pdf"
        )
