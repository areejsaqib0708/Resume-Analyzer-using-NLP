import streamlit as SSS
import pandas as PAN
import base64, random
import numpy as np
import time, datetime
import os
import socket
import platform
import geocoder
import secrets
import pyodbc
import json
import io, random
from geopy.geocoders import Nominatim
from pyresparser import ResumeParser
from pdfminer3.layout import LAParams, LTTextBox
from pdfminer3.pdfpage import PDFPage
from pdfminer3.pdfinterp import PDFResourceManager
from pdfminer3.pdfinterp import PDFPageInterpreter
from pdfminer3.converter import TextConverter
from streamlit_tags import st_tags
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from PIL import Image
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from utill import insert_datas
from Courses import resume_videos, interview_videos
import nltk
from request import RESUME_SCORE
nltk.download('stopwords')
# _________________________________________________________________________________________________________________________________
def TO_READ_PDF(file):
    resource_manager = PDFResourceManager()
    TEXT_FRO_PDF = io.StringIO()
    converter = TextConverter(resource_manager, TEXT_FRO_PDF, laparams=LAParams())
    PROCESS_EACH_PAGE = PDFPageInterpreter(resource_manager, converter)
    with open(file, 'rb') as fh:
        for page in PDFPage.get_pages(fh,
                                      caching=True,
                                      check_extractable=True):
            PROCESS_EACH_PAGE.process_page(page)
            print(page)
        text = TEXT_FRO_PDF.getvalue()

    converter.close()
    TEXT_FRO_PDF.close()
    return text
# _________________________________________________________________________________________________________________________________
def TO_SHOW_PDF(file_path):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    DISPLAU_PDF = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
    SSS.markdown(DISPLAU_PDF, unsafe_allow_html=True)
#_________________________________________________________________________________________________________________________________
def load_data(file_path):
    return PAN.read_csv(file_path)

def JOB_REC0M_FROM_DATASET(user_skills, JOB_DATA):
    REC_JOB = []
    for index, row in JOB_DATA.iterrows():
        job_skills = str(row['Key Skills']).lower().split("|")
        job_skills_str = " ".join(job_skills)
        SIMILARITY = CAL_COSNIE_SIM(" ".join(user_skills), job_skills_str)
        REC_JOB.append((row['Job Title'], row['Key Skills'], row['URL'],SIMILARITY))
    SORTED_REC_JOB = sorted(REC_JOB, key=lambda x: x[3], reverse=True)

    TOP_JOBS = SORTED_REC_JOB[:3]
    return TOP_JOBS

#_________________________________________________________________________________________________________________________________
def CAL_COSNIE_SIM(user_skills, job_skills):
    USER_AND_DATSET_SKILLS = [user_skills, job_skills]
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(USER_AND_DATSET_SKILLS)

    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
    return similarity[0][0]

#___________________________________________________________________________________________________________________________
SSS.set_page_config(
    page_title=" Resume Analyzer",
    page_icon='./Logo/recommend.png',
)
# ________________________________________________________________________________________________________________________________
DRIVER_NAME = '{SQL Server}'
SERVER_NAME = 'DESKTOP-4R9T5DH\\SQLEXPRESS'
DATABASE_NAME = 'AI'

CONNECT_TO_DB = (f"DRIVER={DRIVER_NAME};"
                     f"SERVER={SERVER_NAME};"
                     f"DATABASE={DATABASE_NAME};"
                     f"Trusted_Connection=yes;")
connection = pyodbc.connect(CONNECT_TO_DB)
cursor = connection.cursor()
#________________________________________________________________________________________________________________________________________________________

def DATA_INSERTION_IN_SQL(name, email, Contact, timestamp, Score, reco_field, cand_level, skills, recommended_skills,
                rec_courses):
    try:
        INSERT_DATA_INTO_SQL = """
            INSERT INTO user_data (name, email, Contact, timestamp, Score, reco_field, cand_level, skills, recommended_skills, rec_courses)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        rec_values = (
            name,
            email,
            Contact,
            timestamp,
            Score,
            reco_field,
            cand_level,
            str(skills),
            str(recommended_skills),
            str(rec_courses)
        )
        cursor.execute(INSERT_DATA_INTO_SQL, rec_values)
        connection.commit()
        print("CHLA GYA.")
    except pyodbc.ProgrammingError as e:
        print(f"ProgrammingError: {e}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        connection.close()


# _________________________________________________________________________________________________________________________________
def MAIN():
    activities = ["User", "About","Project Overview"]
    OPTION = SSS.sidebar.selectbox("Choose among the given options:", activities)

    DB_table_name = 'user_data'
    table_sql = f"""
        IF OBJECT_ID('{DB_table_name}', 'U') IS NULL
        BEGIN
            CREATE TABLE {DB_table_name} (
                ID INT NOT NULL IDENTITY(1,1),
                Name VARCHAR(100) NOT NULL,
                Email_ID VARCHAR(50) NOT NULL,
                resume_score VARCHAR(8) NOT NULL,
                Timestamp VARCHAR(50) NOT NULL,
                Page_no VARCHAR(5) NOT NULL,
                Predicted_Field VARCHAR(25) NOT NULL,
                User_level VARCHAR(30) NOT NULL,
                Actual_skills VARCHAR(300) NOT NULL,
                Recommended_skills VARCHAR(300) NOT NULL,
                Recommended_courses VARCHAR(600) NOT NULL,
                PRIMARY KEY (ID)
            );
        END;
        """
    cursor.execute(table_sql)

    if OPTION == 'User':
        FRONT_IMAGE = Image.open('C:/Users/ua/AI-Resume-Analyzer/App/Logo/PICSS.jpg')
        FRONT_IMAGE = FRONT_IMAGE.resize((350, 330))
        MOVED_IMAGE = Image.new("RGB", (550, 330), (255, 255, 255))
        MOVED_IMAGE.paste(FRONT_IMAGE, (160, 0))
        SSS.image(MOVED_IMAGE)

        SSS.markdown('''<h5 style='text-align: left; color: #021659;'> Upload Your Resume, And Get Smart Recommendations</h5>''',unsafe_allow_html=True)

        pdf_file = SSS.file_uploader("Choose your Resume", type=["pdf"])
        if pdf_file is not None:
            RESUME_INTO_FOLDER = './Uploaded_Resumes/' + pdf_file.name
            pdf_name = pdf_file.name
            with open(RESUME_INTO_FOLDER, "wb") as f:
                f.write(pdf_file.getbuffer())
            TO_SHOW_PDF(RESUME_INTO_FOLDER)

            STRUCTURED_DTA_FROM_RESUE = ResumeParser(RESUME_INTO_FOLDER).get_extracted_data()
            if STRUCTURED_DTA_FROM_RESUE:
                TEXT_EXTRACTED_FROM_RESUME = TO_READ_PDF(RESUME_INTO_FOLDER)
                SSS.header("**Resume Analysis 🤘**")
                STRUCTURED_DTA_FROM_RESUE = insert_datas(STRUCTURED_DTA_FROM_RESUE, TO_READ_PDF, RESUME_INTO_FOLDER)
                SSS.success("Hello " + STRUCTURED_DTA_FROM_RESUE['name'])
                SSS.subheader("**YOUR BASIC INFORMATION**")
                try:
                    SSS.text('Name: ' + STRUCTURED_DTA_FROM_RESUE['name'])
                    SSS.text('Email: ' + STRUCTURED_DTA_FROM_RESUE['email'])
                    SSS.text('Contact: ' + STRUCTURED_DTA_FROM_RESUE['mobile_number'])
                    SSS.text('Degree: ' + str(STRUCTURED_DTA_FROM_RESUE['degree']))
                    SSS.text('Resume pages: ' + str(STRUCTURED_DTA_FROM_RESUE['no_of_pages']))

                except:
                    pass
                if 'INTERNSHIP' in TEXT_EXTRACTED_FROM_RESUME or 'INTERNSHIPS' in TEXT_EXTRACTED_FROM_RESUME or 'Internship' in TEXT_EXTRACTED_FROM_RESUME or 'Internships' in TEXT_EXTRACTED_FROM_RESUME:
                    cand_level = "Intermediate"
                    SSS.markdown('''<h4 style='text-align: left; color: #1ed760;'>You are at intermediate level!</h4>''',
                                unsafe_allow_html=True)
                elif 'EXPERIENCE' in TEXT_EXTRACTED_FROM_RESUME or 'Experience' in TEXT_EXTRACTED_FROM_RESUME or 'WORK EXPERIENCE' in TEXT_EXTRACTED_FROM_RESUME or 'Work Experience' in TEXT_EXTRACTED_FROM_RESUME:
                    cand_level = "Experienced"
                    SSS.markdown('''<h4 style='text-align: left; color: #fba171;'>You are at experience level!''',
                                unsafe_allow_html=True)
                else:
                    cand_level = "Fresher"
                    SSS.markdown('''<h4 style='text-align: left; color: #fba171;'>You are at Fresher level!!''',
                                unsafe_allow_html=True)
                # cand_level=experience(TEXT_EXTRACTED_FROM_RESUME)

 # __________________________________________________________________________________________________________________________________________________
                ## Skills Analyzing and Recommendation
                SSS.markdown("""
                    <style>
                    .stTag {
                        background: linear-gradient(135deg, #ff7e5f, #feb47b);  /* Gradient background */
                        color: white;                 /* White text color */
                        border-radius: 30px;          /* More rounded corners */
                        font-weight: bold;            /* Bold text */
                        padding: 5px 15px;            /* Padding inside the tags */
                        font-size: 14px;              /* Slightly larger text size */
                        transition: transform 0.2s ease-in-out; /* Smooth hover animation */
                        box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1); /* Subtle shadow */
                    }
                    .stTag:hover {
                        transform: scale(1.05);       /* Slight zoom effect on hover */
                        background: linear-gradient(135deg, #feb47b, #ff7e5f); /* Reverse gradient on hover */
                    }
                    </style>
                """, unsafe_allow_html=True)

#_____________________________________________________________________________________________________________________
                dataset_path = r'C:\Users\ua\AI-Resume-Analyzer\jobss.csv'
                JOB_FROM_DATASET = load_data(dataset_path)
                EXTRACTED_SKILLS_FROM_RESUME = STRUCTURED_DTA_FROM_RESUE['skills']

                keywords = st_tags(label='### YOUR CURRENT SKILLS',
                                   text='See our skills recommendation below', value=STRUCTURED_DTA_FROM_RESUE['skills'], key='1  ')
                matching_jobs = JOB_REC0M_FROM_DATASET(EXTRACTED_SKILLS_FROM_RESUME, JOB_FROM_DATASET)
                RECOMMENDED_JOB = []
                RECOMMENDED_SKILS=[]
                REC_COURSE_VIDEO=[]
                COSINE_SIMILARITY=[]
                if EXTRACTED_SKILLS_FROM_RESUME:
                    matching_jobs = JOB_REC0M_FROM_DATASET(EXTRACTED_SKILLS_FROM_RESUME, JOB_FROM_DATASET)
                    if matching_jobs:
                        SSS.subheader("### MATCHING JOB RECOMMENDATION")
                        for job, skills, URL,sim in matching_jobs:
                            RECOMMENDED_JOB.append(job)
                            print(RECOMMENDED_JOB)
                            RECOMMENDED_SKILS.append(skills)
                            REC_COURSE_VIDEO.append(URL)
                            COSINE_SIMILARITY.append(sim)
                            SSS.success(f"**Job Title:** {job}\n")
                            SSS.markdown(f"**Required Skills:** {skills}")
                            sim=(sim/1)*100
                            sim=sim+20
                            SSS.markdown(f"**Job Recommendation Relevance %:** {sim:.2f}")
                            if URL and str(URL).strip() != "nan":
                                SSS.markdown(f"**Recommendation Course:** {URL}")
                            else:
                                SSS.warning("No course video available for this job.")
                    else:
                        SSS.warning("No matching jobs found. Try adding more relevant skills.")

                SSS.subheader("**RESUME TIPS**")
                TEXT_EXTRACTED_FROM_RESUME=TEXT_EXTRACTED_FROM_RESUME.upper()
                if 'Objective' or 'Summary' in TEXT_EXTRACTED_FROM_RESUME:
                    SSS.markdown(
                        '''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Objective/Summary</h4>''',
                        unsafe_allow_html=True)
                else:
                    SSS.markdown(
                        '''<h5 style='text-align: left; color: #000000;'>[-] Please add your career objective, it will give your career intension to the Recruiters.</h4>''',
                        unsafe_allow_html=True)

                if 'Education' or 'School' or 'College' in TEXT_EXTRACTED_FROM_RESUME:
                    SSS.markdown(
                        '''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Education Details</h4>''',
                        unsafe_allow_html=True)
                else:
                    SSS.markdown(
                        '''<h5 style='text-align: left; color: #000000;'>[-] Please add Education. It will give Your Qualification level to the recruiter</h4>''',
                        unsafe_allow_html=True)

                if 'EXPERIENCE' in TEXT_EXTRACTED_FROM_RESUME:
                    SSS.markdown(
                        '''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Experience</h4>''',
                        unsafe_allow_html=True)
                else:
                    SSS.markdown(
                        '''<h5 style='text-align: left; color: #000000;'>[-] Please add Experience. It will help you to stand out from crowd</h4>''',
                        unsafe_allow_html=True)

                if 'INTERNSHIPS' in TEXT_EXTRACTED_FROM_RESUME or 'INTERNSHIP' in TEXT_EXTRACTED_FROM_RESUME:
                    SSS.markdown(
                        '''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Internships</h4>''',
                        unsafe_allow_html=True)
                else:
                    SSS.markdown(
                        '''<h5 style='text-align: left; color: #000000;'>[-] Please add Internships. It will help you to stand out from crowd</h4>''',
                        unsafe_allow_html=True)

                if 'SKILLS' in TEXT_EXTRACTED_FROM_RESUME or 'SKILL' in TEXT_EXTRACTED_FROM_RESUME:
                    SSS.markdown(
                        '''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Skills</h4>''',
                        unsafe_allow_html=True)
                else:
                    SSS.markdown(
                        '''<h5 style='text-align: left; color: #000000;'>[-] Please add Skills. It will help you a lot</h4>''',
                        unsafe_allow_html=True)

                if 'HOBBIES' in TEXT_EXTRACTED_FROM_RESUME:
                    SSS.markdown(
                        '''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Hobbies</h4>''',
                        unsafe_allow_html=True)
                else:
                    SSS.markdown(
                        '''<h5 style='text-align: left; color: #000000;'>[-] Please add Hobbies. It will show your personality to the Recruiters and give the assurance that you are fit for this role or not.</h4>''',
                        unsafe_allow_html=True)

                if 'INTERESTS' in TEXT_EXTRACTED_FROM_RESUME:
                    SSS.markdown(
                        '''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Interest</h4>''',
                        unsafe_allow_html=True)
                else:
                    SSS.markdown(
                        '''<h5 style='text-align: left; color: #000000;'>[-] Please add Interest. It will show your interest other that job.</h4>''',
                        unsafe_allow_html=True)

                if 'ACHIEVEMENTS' in TEXT_EXTRACTED_FROM_RESUME:
                    SSS.markdown(
                        '''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Achievements </h4>''',
                        unsafe_allow_html=True)

                else:
                    SSS.markdown(
                        '''<h5 style='text-align: left; color: #000000;'>[-] Please add Achievements. It will show that you are capable for the required position.</h4>''',
                        unsafe_allow_html=True)

                if 'CERTIFICATIONS' in TEXT_EXTRACTED_FROM_RESUME:
                    SSS.markdown(
                        '''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Certifications </h4>''',
                        unsafe_allow_html=True)

                else:
                    SSS.markdown(
                        '''<h5 style='text-align: left; color: #000000;'>[-] Please add Certifications. It will show that you have done some specialization for the required position.</h4>''',
                        unsafe_allow_html=True)

                if 'PROJECTS' in TEXT_EXTRACTED_FROM_RESUME:
                    SSS.markdown(
                        '''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Projects</h4>''',
                        unsafe_allow_html=True)
                elif 'PROJECT' in TEXT_EXTRACTED_FROM_RESUME:
                    SSS.markdown(
                        '''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Projects</h4>''',
                        unsafe_allow_html=True)
                else:
                    SSS.markdown(
                        '''<h5 style='text-align: left; color: #000000;'>[-] Please add Projects. It will show that you have done work related the required position or not.</h4>''',
                        unsafe_allow_html=True)

                SCORE=RESUME_SCORE(TEXT_EXTRACTED_FROM_RESUME)
                SSS.subheader("**RESUME SCORE 📝**")
                SSS.markdown(
                    """
                    <style>
                        .stProgress > div > div > div > div {
                            background-color: #d73b5c;
                        }
                    </style>""",
                    unsafe_allow_html=True,
                )
# ____________________________________________________________________________________________________________________________________________
                my_bar = SSS.progress(0)
                score = 0
                for percent_complete in range(SCORE):
                    score += 1
                    time.sleep(0.1)
                    my_bar.progress(percent_complete + 1)
                SSS.success('** Your Resume Writing Score: ' + str(score) + '**')
                SSS.warning("**Note: This score is calculated based on the content that you have in your Resume.**")
                ts = time.time()
                cur_date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                cur_time = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                timestamp = str(cur_date + '_' + cur_time)

                CONVERTING_JOBS_INTO_JSON_FORMAT = json.dumps(RECOMMENDED_JOB)
                CONVERTING_Skills_INTO_JSON_FORMAT = json.dumps(RECOMMENDED_SKILS)
                CONVERTING_COURSES_INTO_JSON_FORMAT = json.dumps(REC_COURSE_VIDEO)
# ____________________________________________________________________________________________________________________________________________
# ____________________________________________________________________________________________________________________________________________
                DATA_INSERTION_IN_SQL(STRUCTURED_DTA_FROM_RESUE['name'], STRUCTURED_DTA_FROM_RESUE['email'], STRUCTURED_DTA_FROM_RESUE['mobile_number'], datetime.datetime.now(), score, CONVERTING_JOBS_INTO_JSON_FORMAT,cand_level, STRUCTURED_DTA_FROM_RESUE['skills'], CONVERTING_Skills_INTO_JSON_FORMAT, CONVERTING_COURSES_INTO_JSON_FORMAT)
# ____________________________________________________________________________________________________________________________________________
# ____________________________________________________________________________________________________________________________________________
                SSS.header("**Bonus Video for Resume Writing Tips💡**")
                resume_vid = random.choice(resume_videos)
                SSS.video(resume_vid)
                SSS.header("**Bonus Video for Interview Tips💡**")
                interview_vid = random.choice(interview_videos)
                SSS.video(interview_vid)
                if SSS.button("Thanks for visiting!!!"):
                    SSS.balloons()
# ____________________________________________________________________________________________________________________________________________
            else:
                SSS.error('Something went wrong..')
    elif OPTION == "About":
        SSS.subheader("Programmed By")
        SSS.markdown("""
        <style>
        .team-card {
            width: 300px;
            height: 150px;
            margin: 10px auto;
            padding: 20px;
            border-radius: 10px;
            background: linear-gradient(135deg, #001f3f, #00509e); 
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            text-align: center;
            transition: all 0.3s ease-in-out;
            overflow: hidden;
            cursor: pointer;
        }
        .team-card:hover {
            height: 250px; /* Expands box height */
           background: linear-gradient(135deg, #2979ad, #2979ad);

        }
        .name {
            font-size: 1.5rem;
            font-weight: bold;
            color: #fff;
        }
        .details {
            font-size: 1rem;
            color: #fff;
            margin-top: 10px;
            opacity: 0; /* Initially hidden */
            transition: opacity 0.3s ease-in-out; /* Transition for showing the text */
        }

        .team-card:hover .details {
            opacity: 1; /* Make the details text visible when box expands */
            content: "This is additional text"; /* Change text when hovered */
        }
        </style>

         <div class="team-card">
            <div class="name">Maimoona Alia</div>
            <div class="details">2022-CE-02</div>
        </div>

        <div class="team-card">
            <div class="name">Areej Saqib</div>
            <div class="details">2022-CE-21</div>
        </div>


        """, unsafe_allow_html=True)
    elif OPTION=="Project Overview":
        SSS.subheader("Project Overview")


MAIN()
