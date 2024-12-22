
def RESUME_SCORE(resume_text):
    resume_score=0
    resume_text=resume_text.upper()
    if 'Objective' or 'Summary' in resume_text:
        resume_score = resume_score + 6
    if 'Education' or 'School' or 'College' in resume_text:
        resume_score = resume_score + 12

    if 'EXPERIENCE' in resume_text:
        resume_score = resume_score + 16

    if 'INTERNSHIPS' in resume_text:
        resume_score = resume_score + 6

    elif 'INTERNSHIP' in resume_text:
        resume_score = resume_score + 6

    if 'SKILLS' in resume_text:
        resume_score = resume_score + 7

    elif 'SKILL' in resume_text:
        resume_score = resume_score + 7

    if 'HOBBIES' in resume_text:
        resume_score = resume_score + 4


    if 'INTERESTS' in resume_text:
        resume_score = resume_score + 5


    if 'ACHIEVEMENTS' in resume_text:
        resume_score = resume_score + 13


    if 'CERTIFICATIONS' in resume_text:
        resume_score = resume_score + 12

    if 'PROJECTS' in resume_text:
        resume_score = resume_score + 19

    elif 'PROJECT' in resume_text:
        resume_score = resume_score + 19
    return resume_score

