import streamlit as st
import os
import base64
import requests
import io
from pdfminer3.layout import LAParams, LTTextBox
from pdfminer3.pdfpage import PDFPage
from pdfminer3.pdfinterp import PDFResourceManager
from pdfminer3.pdfinterp import PDFPageInterpreter
from pdfminer3.converter import TextConverter
from PIL import Image
from pyresparser import ResumeParser

# Define API details for Hugging Face model
API_URL = "https://api-inference.huggingface.co/models/youssefkhalil320/news-topic-classification-with-bert-resumesClasssifierV1"
API_TOKEN = "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"
HEADERS = {"Authorization": f"Bearer {API_TOKEN}"}


# Function to classify the resume text
def classify_resume_text(text):
    payload = {"inputs": text}  # Preparing input payload
    response = requests.post(API_URL, headers=HEADERS, json=payload)
    return response.json()


# Function to generate download link for CSV
def get_csv_download_link(df, filename, text):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # Encoding CSV as base64
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{text}</a>'
    return href


# Function to read PDF and extract text
def pdf_reader(file):
    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    converter = TextConverter(resource_manager, fake_file_handle, laparams=LAParams())
    page_interpreter = PDFPageInterpreter(resource_manager, converter)

    with open(file, 'rb') as fh:
        for page in PDFPage.get_pages(fh, caching=True, check_extractable=True):
            page_interpreter.process_page(page)
        text = fake_file_handle.getvalue()

    converter.close()
    fake_file_handle.close()
    return text


# Function to show the PDF file in Streamlit
def show_pdf(file_path):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)


# Main function to run the Streamlit app
def run():
    # Setting up page configurations
    st.set_page_config(page_title="AI Resume Analyzer", page_icon='./Logo/recommend.png')

    # Display logo image
    img = Image.open('C:/Users/Public/RESUME/App/Logo/RESUM.png')
    st.image(img)

    # Sidebar with options
    st.sidebar.markdown("# Choose Something...")
    activities = ["User", "Feedback", "About", "Admin"]
    choice = st.sidebar.selectbox("Choose among the given options:", activities)

    # User option for resume analysis
    if choice == 'User':
        # Upload PDF file
        pdf_file = st.file_uploader("Choose your Resume", type=["pdf"])
        if pdf_file is not None:
            # Save the uploaded file
            save_image_path = os.path.join(r'C:\Users\Public\AI Lab\AI_PROJECT\Uploaded_Resumes', pdf_file.name)
            with open(save_image_path, "wb") as f:
                f.write(pdf_file.getbuffer())

            # Show PDF
            show_pdf(save_image_path)

            # Parse and extract data from resume
            resume_data = ResumeParser(save_image_path).get_extracted_data()
            if resume_data:
                # Get resume text from PDF
                resume_text = pdf_reader(save_image_path)
                st.text(resume_text)

                # Call Hugging Face API to classify the resume
                classification_result = classify_resume_text(resume_text)
                st.write("Classification Result:")

                # Debugging: Print the classification result to inspect its structure
                st.write(f"Full Classification Result: {classification_result}")

                if isinstance(classification_result, list) and len(classification_result) > 0:
                    # The result is a list with a list inside, so we access the first list item
                    inner_list = classification_result[0]

                    # Extracting and displaying the label with the highest score
                    try:
                        top_result = max(inner_list, key=lambda x: x['score'])  # Get the label with the highest score
                        st.write(f"Top Label: {top_result['label']}")
                        st.write(f"Score: {top_result['score']:.4f}")
                    except KeyError as e:
                        st.error(f"Error: Missing expected key in classification result: {e}")
                else:
                    st.error("Invalid classification result format.")
            else:
                st.error('Something went wrong while extracting data from the resume.')

# Run the app
run()
