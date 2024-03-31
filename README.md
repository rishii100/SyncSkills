# SyncSkills

SyncSkills is a web application designed to help users evaluate resumes based on given job descriptions. This application utilizes Google's Generative AI service (Gemini AI) to analyze resumes and provide feedback on their relevance to the job description.


## Architecture Design

![Architecture Design](https://github.com/rishii100/SyncSkills/assets/98979613/4b907aa1-2488-4f25-9bbd-db4ecd5382d7)

## Features

- Users can paste a job description and upload a resume in PDF format.
- Resumes are converted to images for analysis using PyMuPDF.
- The application sends the job description and resume image to Google's Generative AI service to generate a response.
- Users receive feedback on resume relevance and suggestions for improvement.

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/SyncSkills.git
   ```

2. Navigate to the project directory:
   ```
   cd SyncSkills
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project directory and add your Google API key:
   ```
   GOOGLE_API_KEY=your_api_key_here
   ```

5. Run the Streamlit application:
   ```
   streamlit run app.py
   ```

6. Access the application in your web browser at http://localhost:8501.

## Usage

1. Paste the job description into the text area provided.
2. Upload a resume in PDF format using the file uploader.
3. Click the "Submit" button to initiate the analysis.
4. View the generated response, including resume evaluation and suggestions for improvement.
5. 
## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.
