from pydantic import BaseModel
from typing import List, Optional

class ResumeData(BaseModel):
    # Personal Information
    full_name: Optional[str] = None
    current_position: Optional[str] = None
    
    # Contact Information
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    address: Optional[str] = None
    
    # Professional Summary
    professional_summary: Optional[str] = None
    
    # Work Experience (list of dictionaries)
    work_experience: List[str]  = []
    
    # Education (list of dictionaries)
    education: List[str] = []
    
    # Skills
    technical_skills: List[str] = []
    soft_skills: List[str] = []
    
    # Additional Sections
    certifications: List[str] = []
    projects: List[str] = []
    languages: List[str] = []
    achievements: List[str] = []

RESUME_EXTRACTION_PROMPT = """
You are a resume information extraction specialist. You will receive a list of strings from OCR (Optical Character Recognition) processing of a resume document.

IMPORTANT: OCR data often contains errors such as:
- Words concatenated without spaces (e.g., "scalableAWSinfrastructuresupportingLLMoperationsthrough")
- Missing spaces between words, sentences, or sections
- Words cut off or split incorrectly
- Inconsistent formatting and spacing
- Some text may be garbled or incomplete

Your task is to extract structured information from this imperfect OCR data and return a JSON object that matches the provided schema.

INSTRUCTIONS:
1. Carefully read through all OCR text lines to understand the resume structure
2. Use context clues to separate concatenated words and fix spacing issues
3. Extract information even if it's imperfect - do your best to interpret the meaning
4. For work experience, try to identify job titles, company names, dates, and responsibilities
5. Look for education information including degrees and institutions
6. Extract technical skills, programming languages, tools, and technologies mentioned
7. If information is unclear or missing, set the field to null or empty list as appropriate
8. Return only valid JSON - no additional text or explanations

OCR Data to process:
{ocr_data}

Return the extracted information as a JSON object:
"""

RESUME_MATCHING_AGENT_PROMPT = """
You are a resume matching agent with access to retrieve_resumes tool. Find the best candidates for job opportunities.

PROCESS:
1. Analyze job requirements - extract key skills, experience level, domain needs
2. Use the tool with targeted queries:
   - Technology-specific: "React", "Python", "AWS" 
   - Role-based: "Frontend Developer", "Senior Engineer"
   - Combined skills: "React Redux", "Python Django"
3. Evaluate and rank candidates based on job fit

You must return:
- A text justification explaining why each candidate was ranked in that order, it can be in markdown format.
- A list of the file names used to answer the question (these are the resumes retrieved).

SEARCH STRATEGY:
- Make multiple targeted searches with different keywords
- Start with must-have skills, then explore related technologies
- Consider experience levels and domain expertise
- Search for complementary skills mentioned in requirements

JUSTIFICATION FORMAT:
Write a clear explanation covering:
- Why the top candidate is the best fit (specific skills/experience that match)
- Why the second candidate ranks second (strengths and any gaps compared to #1)
- Continue for remaining candidates
- Mention any standout qualifications or concerns for each person
"""