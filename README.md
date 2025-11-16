Skillgap – Final Year Project (TU Dublin)

Student: Adam Kerslake Hearst
Student Number: C22370983
Degree: BSc (Hons) Computer Science, TU Dublin

Overview:
Skillgap is a web-based application designed to analyse a user’s CV and a provided Job Description to identify skill-gaps and recommend targeted courses to help the user upskill.
The aim is to bridge the gap between job-seekers and relevant online learning resources by giving personalised, data-driven guidance.

What Skillgap Does:
After the user creates a profile (email, password, personal details) and uploads a copy of their current CV, Skillgap performs:

1. Skill-Gap Analysis
Uses NLP to extract competencies, qualifications, and experience from:
- The user’s uploaded CV
- A job description for the role they are applying to

It then highlights:
- Skills/qualifications the user already meets
- Missing or weak areas
- Overall “match score” (planned)

2. Personalised Upskilling Recommendations
Using ML and online learning provider APIs (e.g., Udemy, edX), Skillgap suggests:
- Free and paid online courses
- Certifications
Recommendations adapt to the user’s profile and the job’s requirements.

Technologies Used (Planned / In Development)
Frontend - React.js / Next.js
Backend API	- FastAPI (Python)
Natural Language Processor/Machine Learning -	spaCy, scikit-learn, custom models
Database - PostgreSQL (with SQLAlchemy)
Document Parsing - Python-docx, PyPDF2
Course Provider Integrations -	edX API, Udemy API, other e-learning APIs
Deployment (Planned) - Docker for containerisation, GitHub Actions CI/CD

Features (Core + Optional)
Core Features
- User registration and login
- CV and Job Description upload
- NLP-powered parsing of competencies
- Skill-gap analysis
- Course recommendation engine
- Clean UI to show missing skills and suggested upskilling paths

Optional / Future Features
- Profile dashboards
- Predictive job-fit scoring

How Skillgap Works (High-Level Flow)
1. User uploads CV and Job Description
2. Backend extracts key entities (skills, qualifications, experience)
3. Matching algorithm calculates gaps
4. Recommendation engine queries course APIs
5. User receives a personalised upskilling plan

Continuous Integration (Planned)
- The GitHub repository will include:
- Automated testing via GitHub Actions
- Linting (flake8 / black)
- Automatic build + docker image validation
- CI workflow files will be added as the backend and frontend mature.

Academic Context
This project is completed as part of the TU Dublin Final Year Project module.
Skillgap demonstrates real-world software engineering practices including:
- Requirement analysis
- Architecture design
- Machine Learning integration
- API-driven system design
- Database modelling
- CI/CD and version control best practices
