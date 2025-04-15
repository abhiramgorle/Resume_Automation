import streamlit as st
import json
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_LINE_SPACING
from io import BytesIO
from openai import OpenAI

def load_docx(file):
    """Load a docx file into a Document object"""
    return Document(file)

def find_section(doc, section_title):
    """Find the paragraph index where a section begins"""
    for i, para in enumerate(doc.paragraphs):
        if section_title.upper() in para.text.strip().upper():
            return i
    return -1

def add_content_to_section(doc, section_title, content_json):
    """Add all content from JSON to a specific section"""
    section_idx = find_section(doc, section_title)
    
    if section_idx == -1:
        st.error(f"Could not find section: {section_title}")
        return False
    
    # Add JSON content after the section title
    current_idx = section_idx + 1
    
    # For each role/project in the JSON
    for item in content_json:
        for title, bullets in item.items():
            # Add the title
            title_para = doc.add_paragraph()
            title_run = title_para.add_run(title)
            
            # Format the title
            title_run.font.name = "Times New Roman"
            title_run.font.size = Pt(11)
            title_run.bold = True
            
            # Remove space after paragraph for title
            title_para.paragraph_format.space_after = Pt(0)
            
            # Insert at current position
            p = title_para._element
            doc.paragraphs[current_idx]._p.addprevious(p)
            current_idx += 1
            
            # Add bullet points with proper formatting
            for bullet in bullets:
                # Create a new paragraph
                bullet_para = doc.add_paragraph()
                
                # Add text with proper bullet formatting
                run = bullet_para.add_run(f"• {bullet}")  # Unicode bullet point
                
                # Set font to Times New Roman, size 11pt
                run.font.name = "Times New Roman"
                run.font.size = Pt(11)
                
                # Set line spacing to 1.0 (single spacing)
                paragraph_format = bullet_para.paragraph_format
                paragraph_format.line_spacing = 1.0
                
                # Remove space after paragraph
                paragraph_format.space_after = Pt(0)
                
                # Insert at current position
                p = bullet_para._element
                doc.paragraphs[current_idx]._p.addprevious(p)
                current_idx += 1
    
    return True

def save_docx(doc):
    """Save document to BytesIO object for downloading"""
    output = BytesIO()
    doc.save(output)
    output.seek(0)
    return output

def process_job_description(resume_json, job_description, model="gpt-3.5-turbo-0125"):
    """Process job description with OpenAI API and get enhanced resume content"""
    keymain = "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"
    client = OpenAI(api_key=keymain)
    
    system_prompt = """
    You are a resume optimization assistant. Extract keywords from job descriptions and 
    enhance resume bullet points to match job requirements. Focus on metrics, actions, 
    and relevant skills. Return JSON only.
    """
    
    user_prompt = f"""
    JOB DESCRIPTION:
    {job_description}
    
    RESUME DATA TO ENHANCE:
    {json.dumps(resume_json)}
    
    INSTRUCTIONS:
    1. Extract key skills and terms from the job description
    2. Modify bullet points to incorporate these terms, Add any kind of technology that you think is valid for the role and that is needed for the job description
    3. Add/enhance metrics where possible
    4. Return only valid JSON in this format: 
       {{
         "experience": [
           {{"role_name": ["bullet_point1", "bullet_point2", ...]}},
           ...
         ],
         "projects": [
           {{"project_name": ["bullet_point1", "bullet_point2", ...]}},
           ...
         ]
       }}
    """
    
    try:
        response = client.chat.completions.create(
            model=model,
            response_format={"type": "json_object"},  # Force JSON response
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3  # Lower temperature for more consistent outputs
        )
        
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        st.error(f"Error calling OpenAI API: {str(e)}")
        return None

# Streamlit App
def main():
    st.title("📝 Resume Builder from JSON")
    st.write("Add experience and projects to your resume template from JSON data")

    # Sidebar for API key
    model_option = "gpt-4.1-nano"

    # File uploader for resume template
    uploaded_file = "new_resume_half.docx"
    
    
    
    
    job_description = st.text_area("Paste job description here", height=150)

    if uploaded_file :
        try:
            # Parse JSON input
            resume_data = {
  "experience": [
    {
      "Software Developer | College of Education, University of Florida": [
        "Engineered robust infrastructure for educational platform using Python and ReactJS within an agile organization, implementing secure database queries serving 5,000+ concurrent users",
        "Built automated ETL pipelines with Python that integrate with business management systems, improving data processing efficiency by 35% and enabling seamless data flow",
        "Developed reusable backend services implementing agile methodologies for data protection and user identity management in a product-driven environment",
        "Collaborated with cross-functional teams to design scalable database architecture using PostgreSQL, creating accessible educational resources that improved EEO compliance."
      ]
    },
    {
      "Software Engineer Intern | AlcoveX Product Studio": [
        "Designed and developed backend systems using agile methodologies in a product-driven environment, increasing overall system reliability by 40%",
        "Built business intelligence pipelines for analytics processing, implementing AI-powered visualization tools and OOP design patterns for modular code",
        "Created comprehensive test cases for information systems components, ensuring accessibility and EEO compliance in user interfaces",
        "Implemented CI/CD pipelines for automated warehouse management system testing in a collaborative organization, achieving 99.9% deployment success rates."
      ]
    },
    {
      "QA Intern | Medha International": [
        "Developed test automation framework using Python and OOP principles for business management system validation in an agile environment",
        "Built performance testing tools to analyze systems under high load conditions, implementing Slack notifications for real-time alerts",
        "Established streamlined bug reporting workflows to identify software design issues, improving organizational communication",
        "Created data analysis scripts using Python to optimize materials management systems and identify business process improvements."
      ]
    }
  ],
  "projects": [
    {
      "G-Community: Business Networking Platform for College Entrepreneurs": [
        "Architected and developed a reusable backend infrastructure for business management platform supporting 15,000+ active users",
        "Engineered a robust real-time communication system implementing MySQL and database queries for user identity management",
        "Integrated with Slack for notifications and business systems to create seamless information flow between sales and operations."
      ]
    },
    {
      "Dermatological Diagnostics: Deep Learning Framework": [
        "Engineered a CNN-based automated system for classifying nine skin pathologies, creating a distributed architecture that processed 1.2TB of medical images",
        "Implemented distributed training architecture on Amazon Web Services to process large medical datasets, reducing training time by 65%",
        "Achieved 85% diagnostic accuracy with optimized model architecture that reduced inference time by 72% for real-time customer applications",
        "Designed fault-tolerant distributed storage solutions that maintained 99.9% data integrity while meeting HIPAA security requirements."
      ]}
      
      ]
  }
            
            if st.button("Build Resume"):
                with st.spinner("Processing..."):
                    # Load document
                    doc = load_docx(uploaded_file)
                    
                    # If using OpenAI, get optimized content
                    if job_description :
                        enhanced_data = process_job_description(resume_data, job_description, model_option)
                        if enhanced_data:
                            resume_data = enhanced_data
                            st.success("Resume content optimized for job description!")
                    
                    # Add experience section
                    if "experience" in resume_data and resume_data["experience"]:
                        success = add_content_to_section(doc, "EXPERIENCE", resume_data["experience"])
                        if success:
                            st.success("✅ Added experience section")
                        else:
                            st.error("❌ Failed to add experience section")
                    
                    # Add projects section
                    if "projects" in resume_data and resume_data["projects"]:
                        success = add_content_to_section(doc, "PROJECTS", resume_data["projects"])
                        if success:
                            st.success("✅ Added projects section")
                        else:
                            st.error("❌ Failed to add projects section")
                    
                    # Save and offer download
                    output_docx = save_docx(doc)
                    st.download_button("📥 Download Complete Resume", 
                                      data=output_docx, 
                                      file_name="Complete_Resume.docx",
                                      mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        except json.JSONDecodeError:
            st.error("Invalid JSON format. Please check your input.")

if __name__ == "__main__":
    main()