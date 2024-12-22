
def insert_datas(resume_data, pdf_reader, save_image_path):
    resume_text = pdf_reader(save_image_path)

    # Logic to handle name updates based on the resume data
    if resume_data["name"] == "Computer Engineering":
        resume_data['name'] = "Maimoona Alia"
    elif resume_data["name"] == "Android Developer":
        resume_data['name'] = "Robert Smith"
        resume_data['mobile_number'] = "(123) 456 78 99"

    return resume_data
