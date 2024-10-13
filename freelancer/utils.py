import fitz  # PyMuPDF
import spacy
import json
import re
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from io import BytesIO
from .models import Document, Template  # Adjust import based on your project structure

# Load spaCy's English NLP model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    # Download the model if it isn't found
    from spacy.cli import download
    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# Function to clean unnecessary icons and whitespace
def clean_text(text):
    text = text.replace('\uf0b7', '')  # Remove unnecessary icons
    text = text.strip()
    return text

# Step 1: Extract text from PDF resume
def extract_text_from_pdf(pdf_stream):
    pdf_document = fitz.open(stream=pdf_stream, filetype="pdf")
    text = ""
    for page_num in range(pdf_document.page_count):
        page = pdf_document.load_page(page_num)
        text += page.get_text()
    return text

# Step 2: Process resume text to extract structured information using NLP
def process_resume_text(resume_text):
    doc = nlp(resume_text)
    headings = ["Experience", "Education", "Technical Skills", "Personal Skills", "Projects", "Certifications", "Achievements", "Hobbies", "Internships", "Contact"]
    extracted_info = {heading: "" for heading in headings}
    current_heading = None

    for line in resume_text.split("\n"):
        line = clean_text(line)
        line_lower = line.lower()

        # Check if the line is a section heading
        if any(line_lower.startswith(heading.lower()) for heading in headings):
            current_heading = next(heading for heading in headings if line_lower.startswith(heading.lower()))
        elif current_heading:
            extracted_info[current_heading] += line + "\n"

    return extracted_info

def parse_internships(internships_text):
    internships_entries = []
    entries = internships_text.split('•')  # Split on bullet points
    
    for entry in entries:
        if entry.strip():
            lines = entry.strip().split('|')  # Split by '|'
            if len(lines) >= 3:
                job_title = lines[0].strip()
                duration = lines[1].strip()
                start_date = lines[2].strip() if len(lines) > 2 else ""
                location = lines[3].strip() if len(lines) > 3 else ""
                
                description = f"{job_title} | {duration} | {start_date} {location}"
                internships_entries.append({"details": description})
    
    return internships_entries

def parse_experience(experience_text):
    experience_entries = []
    
    # Split entries by double newlines to handle separate experiences
    entries = experience_text.split('\n\n')
    
    for entry in entries:
        if entry.strip():
            lines = entry.split('\n')
            
            if len(lines) >= 2:  # Ensure there are at least job title/company and dates
                # Extract job title, company, and dates from the first two lines
                details_line = lines[0].strip()
                dates_line = lines[1].strip()
                
                # Use regular expression to split by common separators like , | or -
                details_parts = re.split(r'[,\|/-]', details_line)
                
                # Strip extra spaces and assign values based on detected parts
                job_title = details_parts[0].strip() if len(details_parts) > 0 else ""
                company_name = details_parts[1].strip() if len(details_parts) > 1 else ""
                
                # Extract start and end dates from the second line using regex
                date_matches = re.findall(r'\b\w+\s\d{4}\b', dates_line)
                start_date, end_date = (date_matches[0], date_matches[1]) if len(date_matches) >= 2 else ("", "")
                
                # The rest of the lines form the description (join them)
                description = '\n'.join(lines[2:]).strip() if len(lines) > 2 else ""
                
                # Maintain any bullet points and preserve formatting in the description
                description_lines = description.split('\n')
                formatted_description = ""
                for desc_line in description_lines:
                    formatted_description += f"• {desc_line.strip()}\n" if desc_line.strip().startswith('•') else f"{desc_line.strip()}\n"
                
                # Append experience entry as a dictionary
                experience_entries.append({
                    "details": {
                        "job_title": job_title,
                        "company_name": company_name,
                        "start_date": start_date,
                        "end_date": end_date
                    },
                    "description": formatted_description.strip()  # Remove trailing newline
                })
    
    return experience_entries

def parse_education(education_text):
    education_entries = []
    entries = re.split(r'\n(?=\•)', education_text)  # Split on new lines followed by a bullet point

    for entry in entries:
        if entry.strip():
            lines = entry.split('\n')
            degree = ""
            institution = ""
            university_board = ""
            description = ""

            if len(lines) > 0:
                degree = lines[0].strip()
            if len(lines) > 1:
                institution = lines[1].strip()
            if len(lines) > 2:
                university_board = lines[2].strip()
            if len(lines) > 3:
                description = ' '.join(line.strip() for line in lines[3:])

            if degree and institution and university_board:
                education_entries.append({
                    "degree": degree,
                    "institution": institution,
                    "university_board": university_board,
                    "description": description
                })

    return education_entries

def parse_achievements(achievements_text):
    achievement_entries = [clean_text(ach).strip() for ach in achievements_text.split('\n\n') if ach.strip()]
    return achievement_entries

def parse_projects(projects_text):
    project_entries = [clean_text(proj).strip() for proj in projects_text.split('\n\n') if proj.strip()]
    return project_entries

def parse_skills(skills_text):
    # Split skills based on common delimiters such as commas, bullets, or newlines
    skill_entries = re.split(r'[,\n•|]', skills_text)
    skill_entries = [skill.strip() for skill in skill_entries if skill.strip()]
    return skill_entries

# Parsing contact details such as phone, email, and links (e.g., LinkedIn)
def parse_contact(contact_text):
    contact_details = {
        "email": "",
        "phone": "",
        "linkedin": "",
        "other_links": [],
        "address": ""
    }

    # Print the input for debugging
    print("Input contact text:", contact_text)

    # Extract email address
    email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', contact_text)
    if email_match:
        contact_details["email"] = email_match.group(0)
        print("Extracted email:", contact_details["email"])

    # Extract phone number (assuming a standard format)
    phone_match = re.search(r'(\+?\d{1,3})?\s?-?\(?\d{2,4}?\)?\s?\d{3,4}[\s-]?\d{3,4}', contact_text)
    if phone_match:
        contact_details["phone"] = phone_match.group(0)
        print("Extracted phone:", contact_details["phone"])

    # Extract LinkedIn profile
    linkedin_match = re.search(r'https?://(?:www\.)?linkedin\.com/in/[A-Za-z0-9_-]+', contact_text)
    if linkedin_match:
        contact_details["linkedin"] = linkedin_match.group(0)
        print("Extracted LinkedIn:", contact_details["linkedin"])

    # Extract other social links (Twitter, GitHub, etc.)
    other_links = re.findall(r'\b(?:https?://|www\.)[^\s]+', contact_text)
    for link in other_links:
        if "linkedin.com" not in link:
            contact_details["other_links"].append(link)
            print("Extracted other link:", link)

    # Extract address by joining lines excluding email, phone, and links
    address_lines = []
    for line in contact_text.splitlines():
        line = line.strip()
        if line and not (line.startswith('+') or re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', line) or 'linkedin.com' in line):
            address_lines.append(line)

    contact_details["address"] = ', '.join(address_lines).strip()
    print("Extracted address:", contact_details["address"])

    return contact_details


# Process and display structured data in JSON format
def print_extracted_info_as_json(extracted_info):
    extracted_info["Experience"] = parse_experience(extracted_info.get("Experience", ''))
    extracted_info["Education"] = parse_education(extracted_info.get("Education", ''))
    extracted_info["Achievements"] = parse_achievements(extracted_info.get("Achievements", ''))
    extracted_info["Projects"] = parse_projects(extracted_info.get("Projects", ''))
    extracted_info["Technical Skills"] = parse_skills(extracted_info.get("Technical Skills", ''))
    extracted_info["Personal Skills"] = parse_skills(extracted_info.get("Personal Skills", ''))
    extracted_info["Contact"] = parse_contact(extracted_info.get("Contact", ''))

    json_data = json.dumps(extracted_info, indent=4)
    print("Extracted Resume Information (JSON):")
    print(json_data)