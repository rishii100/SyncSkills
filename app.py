import streamlit as st
import google.generativeai as genai
import os
import fitz  # PyMuPDF
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Function: Convert uploaded PDF to image
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

# Function: Create fancy, clean PDF
def create_pdf(text):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            rightMargin=40, leftMargin=40,
                            topMargin=60, bottomMargin=40)
    
    styles = getSampleStyleSheet()
    story = []

    # Custom style for bold headings
    heading_style = styles["Heading2"]
    heading_style.textColor = colors.darkblue
    heading_style.alignment = TA_LEFT

    # Normal paragraph style
    normal_style = styles["BodyText"]
    normal_style.fontName = "Helvetica"
    normal_style.fontSize = 11

    # Split and format intelligently
    for line in text.split("\n"):
        if "Job-Description Match" in line:
            story.append(Paragraph(line, heading_style))
            story.append(Spacer(1, 12))
        elif "describe how to improve" in line.lower():
            story.append(Paragraph(line, heading_style))
            story.append(Spacer(1, 12))
        else:
            story.append(Paragraph(line, normal_style))
            story.append(Spacer(1, 8))

    doc.build(story)
    buffer.seek(0)
    return buffer

# --------------- Streamlit UI ---------------

st.set_page_config(page_title="SyncSkills - Resume Evaluator", page_icon="📄")
st.title("SyncSkills 🚀")
st.caption("Your Achievements, Your Career, Our Revolution.")

# Step 1: Job Description input
st.markdown("### Step 1: Paste the Job Description")
jd = st.text_area("Job Description", height=200)

# Step 2: Upload Resume
st.markdown("### Step 2: Upload Your Resume (PDF)")
uploaded_file = st.file_uploader("Upload your resume here", type=["pdf"])

if uploaded_file:
    st.success("✅ Resume Uploaded Successfully!")

# Input prompts
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

# Submit Button
submit = st.button("Submit")

if submit:
    if not uploaded_file or not jd.strip():
        st.error("⚠️ Please upload a resume and enter a job description.")
    else:
        with st.spinner("Analyzing your resume..."):
            pdf_img = convert_pdf_to_image(uploaded_file)
            job_desc = f"The job description: {jd}"
            response = get_gemini_response(input_prompt, pdf_img, job_desc, struc)

        # Dynamically extract match percentage from the response (parse it)
        match_percentage = None
        for line in response.split("\n"):
            if "Job-Description Match" in line:
                # Extract match percentage from the response (this is a simple example, you can improve the parsing)
                match_percentage = line.split(":")[1].strip()
                break

        if match_percentage:
            # Match Percentage display without extra markdown symbols
            st.markdown(f"### Job-Description Match: {match_percentage}")
        else:
            st.warning("Couldn't extract match percentage from the response.")

        # Display the rest of the evaluation result
        st.subheader("📄 Evaluation Result")
        st.markdown(response)

        # Create and offer Downloadable PDF
        pdf_file = create_pdf(response)
        st.download_button(
            label="📄 Download Evaluation Report",
            data=pdf_file,
            file_name="resume_evaluation.pdf",
            mime="application/pdf"
        )
