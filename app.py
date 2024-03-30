import streamlit as st
import google.generativeai as genai
import os
import PyPDF2 as pdf
from dotenv import load_dotenv
import fitz  # PyMuPDF
from PIL import Image, PngImagePlugin
from io import BytesIO

load_dotenv() 

genai.configure(api_key=os.getenv(st.secrets["GOOGLE_API_KEY"]))


def get_gemini_response(input_prompt, pdf_img, job_desc,struc):
    model=genai.GenerativeModel('gemini-pro-vision')
    response=model.generate_content([input_prompt, pdf_img, job_desc,struc])
    return response.text


def convert_pdf_to_image(uploaded_file, page_number=0):

    pdf_document = fitz.open(stream=BytesIO(uploaded_file.read()))
    page = pdf_document[page_number]

    # Get the dimensions of the page
    rect = page.rect

    # Convert the page to an image (RGB)
    pix = page.get_pixmap(matrix=fitz.Matrix(300 / 72, 300 / 72))
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

    pdf_document.close()
    return img

#Prompt Template

input_prompt="""
Hey Act Like a skilled or very experience ATS(Application Tracking System)
with a deep understanding of tech field,software engineering,data science ,data analyst
and big data engineer. Your task is to evaluate the resume based on the given job description.
 Assign the percentage Matching based 
on Job description,relevance and the missing keywords with high accuracy

resume:
"""
job_desc = 'The job description:{jd}'
## streamlit app
st.title("RESUME CHECKER")
st.text("Optimize Your Resume Using Gemini Pro")
jd=st.text_area("Paste the Job Description")
uploaded_file=st.file_uploader("Upload Your Resume",type="pdf",help="Please upload the pdf")

struc = '''
I want the response having the structure
"Job-Description Match:%" /n "describe how to improve the given resume:".
the job description match should not be very high it should very strict and hard 
'''
if uploaded_file is not None:
    st.write("PDF Uploaded Successfully")


submit = st.button("Submit")

if submit:
    if uploaded_file:

        pdf_img=convert_pdf_to_image(uploaded_file)
        response=get_gemini_response(input_prompt, pdf_img, job_desc, struc)
        st.subheader(response)