from flask import Flask, request, jsonify, send_file, render_template
import os
import requests
import json
import re
import tempfile
import pprint

app = Flask(__name__)

# Set your Gemini API key here
GEMINI_API_KEY ='AIzaSyD_EKbKOx-EiMKc85H28gMv0ela02lpU1Y'
projects = [
    {
        "title": "Edustaff E-Learning Platform",
        "role": "Cloud Data and DevOps Engineer",
        "scope": "Designed and implemented an e-learning platform tailored for support staff, hosted on AWS EC2 and RDS. Automated deployments using Terraform to ensure infrastructure consistency.",
        "skills": ["Terraform", "AWS EC2", "AWS RDS", "Node.js", "CI/CD pipelines"],
        "impact": "Centralized training processes, leading to increased productivity and continuous learning for support staff."
    },
    {
        "title": "Microcouriers Courier Application",
        "role": "Cloud Data and DevOps Engineer",
        "scope": "Developed a fully functional courier service application with order management capabilities, hosted on Docker and connected to a MySQL database.",
        "skills": ["Docker", "MySQL", "Node.js", "Containerization"],
        "impact": "Streamlined courier order management, reduced manual handling, and enabled efficient service delivery."
    },
    {
        "title": "Social Media Details API",
        "role": "Cloud Data and DevOps Engineer",
        "scope": "Created an API to validate emails and fetch social media details using Flask and Selenium.",
        "skills": ["Flask", "Selenium", "NoSQL Lite", "Web Automation"],
        "impact": "Enhanced email validation processes and improved the accuracy of user data for businesses."
    },
    {
        "title": "Kubernetes Deployment",
        "role": "Cloud Data and DevOps Engineer",
        "scope": "Deployed Node.js and MongoDB applications using Kubernetes on AWS with automated provisioning via Terraform.",
        "skills": ["Kubernetes", "Terraform", "AWS EC2", "Container Orchestration"],
        "impact": "Improved resource utilization, ensured high availability, and reduced downtime for containerized applications."
    },
    {
        "title": "MySQL HA Cluster",
        "role": "Cloud Data and DevOps Engineer",
        "scope": "Engineered a high-availability MySQL cluster with ProxySQL load balancing and replication.",
        "skills": ["MySQL", "ProxySQL", "Load Balancing", "High Availability"],
        "impact": "Ensured uninterrupted database access and reduced downtime for critical services."
    },
    {
        "title": "Prometheus and Grafana for Kubernetes Monitoring",
        "role": "Cloud Data and DevOps Engineer",
        "scope": "Set up Prometheus and Grafana for monitoring Kubernetes clusters, running on Minikube.",
        "skills": ["Prometheus", "Grafana", "Minikube", "Kubernetes"],
        "impact": "Improved observability and proactive maintenance of infrastructure through real-time monitoring."
    },
    {
        "title": "Acten3 ETL",
        "role": "Cloud Data and DevOps Engineer",
        "scope": "Designed an ETL tool for supply chain data tracking using Python, Azure Blob, and TigerGraph.",
        "skills": ["Python", "Azure Blob", "TigerGraph", "ETL Processes", "Terraform"],
        "impact": "Enabled real-time logistics monitoring, optimized fleet management, and reduced operational costs."
    },
    {
        "title": "Scraper Optimization and Containerization Project",
        "role": "Cloud Data and DevOps Engineer",
        "scope": "Optimized a web scraper for Elasticsearch, containerized it with Docker, and automated provisioning with Terraform.",
        "skills": ["Docker", "Terraform", "Elasticsearch", "GitHub Actions"],
        "impact": "Reduced data collection time, improved system performance, and enhanced scalability during peak loads."
    },
    {
        "title": "CloudTrafficMonitor",
        "role": "Cloud Data and DevOps Engineer",
        "scope": "Developed a serverless API for traffic monitoring using AWS API Gateway, Cognito, and Lambda.",
        "skills": ["AWS API Gateway", "AWS Cognito", "AWS Lambda", "Serverless Architecture"],
        "impact": "Streamlined traffic data collection and analysis, enhancing road safety decision-making."
    },
    {
        "title": "SQOR GitLab CI/CD",
        "role": "Cloud Data and DevOps Engineer",
        "scope": "Optimized a SaaS application with AWS Step Functions and implemented CI/CD pipelines using GitLab.",
        "skills": ["AWS Step Functions", "GitLab CI/CD", "Serverless Architecture", "AWS ECS"],
        "impact": "Improved deployment reliability, reduced downtime, and ensured seamless user experiences."
    }
]

def validate_latex(latex_code):
    return '\\begin{document}' in latex_code and '\\end{document}' in latex_code

def remove_comments(latex_code):
    return re.sub(r'(?<!\\)%.*', '', latex_code)

def extract_section(latex_code, section_name):
    cleaned_latex_code = remove_comments(latex_code)
    section_name_escaped = re.escape(section_name)
    pattern = rf'\\section\{{{section_name_escaped}\}}(.*?)(?=\\section|\\end\{{document\}})'
    match = re.search(pattern, cleaned_latex_code, re.DOTALL)
    if match:
        return match.group(1).strip()
    return f"Error: {section_name} section not found."
def match_project_to_job_description(job_description, projects):
    # Extract relevant keywords from the job description (simple example)
    jd_keywords = set(job_description.lower().split())

    matched_projects = []
    for project in projects:
        # Compare the job description keywords with project skills and scope
        project_keywords = set(" ".join([project['title'].lower(), project['role'].lower(), project['scope'].lower()]).split())
        common_keywords = jd_keywords.intersection(project_keywords)

        # If there are common keywords, add the project to matched projects
        if common_keywords:
            matched_projects.append(project)

    return matched_projects
def tailor_section(api_key, section, job_description, sec):
    url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={api_key}'
    matched_projects = match_project_to_job_description(job_description, projects)

    # Step 2: Construct the project details for the LaTeX section
    project_details = "\n".join(
        [f"\\textbf{{{project['title']}}}\n"
         f"\\textit{{{project['role']}}}: {project['scope']} "
         f"\\textit{{Skills Used: {', '.join(project['skills'])}}}. "
         f"\\textbf{{Impact:}} {project['impact']}."
         for project in matched_projects]
    )
    # Construct prompts based on section type
    if section == "workex":
        prompt_text = (
            f"""
            Given the job description: '{job_description}', rewrite the '{sec}' section of your resume based on the following key points and the relevant projects that match the JD. 

            1. **Clarify the Ownership of the Task**: Describe your role in the project. Were you the sole owner of key tasks or did you collaborate with a team? Highlight your leadership, management, or collaborative efforts. If you led the project, mention your role in decision-making and execution. Focus on what you were directly responsible for.

            2. **Scope of Work and Your Role**: Detail the scope of the project. What were the project's objectives and goals? What was the project's scale (e.g., team size, timelines, budget)? Specify your role within the project and the specific tasks you handled. Did you contribute to system design, coding, deployment, etc.?

            3. **Skills and Methods Used**: Share the technical tools, programming languages, and methodologies you used in the project. Focus on the tools and technologies mentioned in the job description such as cloud platforms (AWS, GCP), containerization (Docker, Kubernetes), CI/CD tools (Jenkins, Git), programming languages (Python, JavaScript, Node.js), or frameworks (React, Django). Mention any specific methodologies like Agile, Scrum, or DevOps.

            4. **Results, Impacts, or Figures**: Include quantifiable results from the project. How did the project impact the business or end-users? Did the project increase efficiency, reduce costs, or improve performance? Provide numbers, percentages, or other metrics to highlight the results. For example, "Reduced deployment time by 30% through automation," or "Improved system reliability by 25%."

            **Select the most relevant projects based on the job description and the key technologies required for the role**. 

            The following are the relevant projects that align with the job description:

            {project_details}

            Use the projects above to rewrite the work experience section by:
            - Incorporating keywords, technologies, and methodologies from the job description into the tasks you describe.
            - Ensuring that the rewritten content maintains the original structure, format, and word count, while ensuring a professional and precise tone.
            - Ensuring the output is in LaTeX format for the '{sec}' section, with no extra text outside of the LaTeX code. 
            - Focus on maintaining the word count as close to the original as possible while integrating the job-specific terminology seamlessly.
            """
        )



    elif section == "project":
        prompt_text = (
            f"Revise the '{sec}' section to align with the job description: '{job_description}'. Include all key terms from the job description seamlessly. "
            f"The updated content should remain within the input word count limit, structured to highlight relevant project achievements effectively. "
            f"Provide only the tailored LaTeX code for the '{sec}' section, without any additional text or comments."
         f"and make no other changes or additions. Do not include the 'latex' string. The length of the output should match the length of the input."
     f"Tailor the '{section}' section to reflect the job description: '{job_description}'. "
    f"Incorporate job-specific keywords seamlessly and maintain the original word count. "
    f"Focus on making sure the final output aligns closely with the provided job description, "
    f"without adding or removing content. Ensure all relevant skills, technologies, or responsibilities mentioned are included "
    f"naturally in the section. Provide only the final LaTeX code for the '{section}' section."
    )
        
    elif section == "skills":
        prompt_text = (
            f"Rewrite the '{sec}' section based on the job description: '{job_description}'. Ensure all necessary keywords are incorporated naturally. "
            f"Maintain the word count exactly as in the input, while ensuring the content remains concise and directly aligned with the job description. "
            f"Return only the LaTeX code for the '{sec}' section, with no additional text."
         f"and make no other changes or additions. Do not include the 'latex' string. The length of the output should match the length of the input."
    )
    elif section == "ach":
        prompt_text = (
            f"Tailor the '{section}' section to reflect the job description: '{job_description}'. Seamlessly integrate all relevant keywords while preserving "
            f"the input structure and exact word count. The focus should be on clarity and alignment with job-specific achievements. Return only the updated "
            f"LaTeX code for the '{section}' section without any extraneous text."
 f"and make no other changes or additions. Do not include the 'latex' string. The length of the output should match the length of the input."
    )
    else:
        prompt_text = (
            f"Revise the '{section}' section to match the job description: '{job_description}'. Ensure that all relevant keywords are included naturally and "
            f"appropriately. Maintain the original input word count and focus on readability and relevance. Provide only the LaTeX code for the '{section}' section."
       f"and make no other changes or additions. Do not include the 'latex' string. The length of the output should match the length of the input."
    )

    # Prepare the API payload
    prompt = {
        "contents": [
            {
                "parts": [
                    {"text": prompt_text}
                ]
            }
        ]
    }

    headers = {
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(prompt))

        if response.status_code == 200:
            response_json = response.json()
            print("Full API Response:", json.dumps(response_json, indent=2))

            if 'candidates' in response_json and len(response_json['candidates']) > 0:
                content = response_json['candidates'][0].get('content', {}).get('parts', [])
                
                if content and isinstance(content[0], dict):
                    latex_code = content[0].get('text', "")
                    
                    if latex_code:
                        # Return the LaTeX code directly
                        return latex_code.strip()
                    else:
                        return "Error: No LaTeX code found in content."
                else:
                    return "Error: Invalid content format in response."
            else:
                return "Error: No candidates found in API response."
        else:
            return f"Error: Unable to contact API. Status code: {response.status_code}, Message: {response.text}"

    except requests.exceptions.RequestException as e:
        return f"Error: API request failed. Exception: {str(e)}"

@app.route('/upload', methods=['POST'])
def upload():
    resume_file = request.files['resume']
    job_description = request.form['job_description']
    latex_code = resume_file.read().decode('utf-8')

    work_experience_section = extract_section(latex_code, "Work Experience")
    print("-------------------------")
    projects_section = extract_section(latex_code, "Project Work")
    achievements_section = extract_section(latex_code, "Achievements")
    skills_section = extract_section(latex_code, "Skills")

    if "Error" in work_experience_section:
        return jsonify({"error": "Work Experience section not found in LaTeX."}), 400
    if "Error" in projects_section:
        return jsonify({"error": "Project Work section not found in LaTeX."}), 400
    if "Error" in achievements_section:
        return jsonify({"error": "Achievements section not found in LaTeX."}), 400

    tailored_experience = tailor_section(GEMINI_API_KEY, work_experience_section, job_description, "workex")
    tailored_projects = tailor_section(GEMINI_API_KEY, projects_section, job_description, "project")
    tailored_achievements = tailor_section(GEMINI_API_KEY, achievements_section, job_description, "ach")
    tailored_skills = tailor_section(GEMINI_API_KEY, skills_section, job_description, "skills")

    print("The exp is::", tailored_experience)
    print("----------------------------------------")

    final_latex = f"""
\\documentclass[a4paper,10pt]{{article}}
%---------------------------------------------------------------------------------------- 
% FONT
%---------------------------------------------------------------------------------------- 
% 
% fontspec allows you to use TTF/OTF fonts directly
% \\usepackage{{fontspec}}
% \\defaultfontfeatures{{Ligatures=TeX}}
% 
% modified for ShareLaTeX use
% \\setmainfont[
% SmallCapsFont = Fontin-SmallCaps.otf,
% BoldFont = Fontin-Bold.otf,
% ItalicFont = Fontin-Italic.otf
% ]
% {{Fontin.otf}}

%---------------------------------------------------------------------------------------- 
% PACKAGES
%---------------------------------------------------------------------------------------- 
\\usepackage{{url}}
\\usepackage{{parskip}} %other packages for formatting
\\RequirePackage{{color}}
\\RequirePackage{{graphicx}}
\\usepackage[usenames,dvipsnames]{{xcolor}}
\\usepackage[scale=0.9, top=.1in, bottom=.1in]{{geometry}}

%tabularx environment
\\usepackage{{tabularx}}

%for lists within experience section
\\usepackage{{enumitem}}

% centered version of 'X' col. type
\\newcolumntype{{C}}{{>{{\\centering\\arraybackslash}}X}}

%to prevent spillover of tabular into next pages
\\usepackage{{supertabular}}
\\usepackage{{tabularx}}
\\newlength{{\\fullcollw}}
\\setlength{{\\fullcollw}}{{0.47\\textwidth}}

%custom \\section
\\usepackage{{titlesec}} 
\\usepackage{{multicol}}
\\usepackage{{multirow}}

%CV Sections inspired by: 
%http://stefano.italians.nl/archives/26
\\titleformat{{\\section}}{{\\Large\\scshape\\raggedright}}{{}}{{0em}}{{}}[\\titlerule]
\\titlespacing{{\\section}}{{0pt}}{{5.25pt}}{{5.25pt}}

%for publications
\\usepackage[style=authoryear,sorting=ynt, maxbibnames=2]{{biblatex}}

%Setup hyperref package, and colours for links
\\usepackage[unicode, draft=false]{{hyperref}}
\\definecolor{{linkcolour}}{{rgb}}{{0,0.2,0.6}}
\\hypersetup{{colorlinks,breaklinks,urlcolor=linkcolour,linkcolor=linkcolour}}

\\addbibresource{{citations.bib}}
\\setlength\\bibitemsep{{1em}}

%for social icons
\\usepackage{{fontawesome5}}

%debug page outer frames
%\\usepackage{{showframe}}

%---------------------------------------------------------------------------------------- 
% BEGIN DOCUMENT
%---------------------------------------------------------------------------------------- 
\\begin{{document}}

% non-numbered pages
\\pagestyle{{empty}}

%---------------------------------------------------------------------------------------- 
% TITLE
%---------------------------------------------------------------------------------------- 
\\begin{{tabularx}}{{\\linewidth}}{{@{{}} C @{{}}}}\\\\
\\Huge{{Yash Shah}} \\\\[2pt]
\\href{{https://github.com/yash161}}{{\\raisebox{{-0.05\\height}}\\faGithub\\ yash161}} \\ $|$ 
\\href{{https://www.linkedin.com/in/yash-shah-b7129b1bb/}}{{\\raisebox{{-0.05\\height}}\\faLinkedin\\ yash-shah}} \\ $|$ \\ 
\\href{{mailto:yashshah3698@gmail.com}}{{\\raisebox{{-0.05\\height}}\\faEnvelope \\ yashshah3698@gmail.com}} \\ $|$ \\ 
\\href{{tel:+12133018249}}{{\\raisebox{{-0.05\\height}}\\faMobile \\ 2133018249}} \\ $|$ \\ 
\\href{{https://portfolio-two-liard-51.vercel.app/}}{{\\raisebox{{-0.05\\height}}\\faLink \\ Portfolio}} \\ $|$ \\ 
\\raisebox{{-0.05\\height}}\\faMapMarker \\ los angeles \\\\
\\end{{tabularx}}


%---------------------------------------------------------------------------------------- 
% EXPERIENCE SECTIONS
%---------------------------------------------------------------------------------------- 
\\section{{Education}}
\\begin{{tabularx}}{{\\linewidth}}{{ @{{}}l r@{{}} }}
\\color[HTML]{{1C033C}} \\textbf{{California State University, Los Angeles, United States}} & \\hfill \\color[HTML]{{371e77}} August 2024 - August 2026 \\\\
\\color[HTML]{{371e77}} M.S. in Computer Science & \\hfill \\color[HTML]{{4B28A4}} \\\\
\\multicolumn{{2}}{{@{{}}X@{{}}}}{{Relevant Coursework: Advanced AI, Advanced Software Engineering, Computer and Network Security}}
\\end{{tabularx}}

\\setlength{{\\parskip}}{{2pt}}

\\begin{{tabularx}}{{\\linewidth}}{{ @{{}}l r@{{}} }}
\\color[HTML]{{1C033C}} \\textbf{{Ganpat University, Gujarat, India}} & \\hfill \\color[HTML]{{371e77}} July 2019 - June 2023 \\\\
\\color[HTML]{{371e77}} B.Tech. in Computer Science \\& Engineering (Cloud-Based Applications) & \\hfill \\color[HTML]{{4B28A4}} \\textit{{\\textbf{{CGPA: 8.99/10}}}} \\\\
\\multicolumn{{2}}{{@{{}}X@{{}}}}{{Relevant Coursework: Cloud Computing, Machine Learning, Cloud Security, Data Mining \\& Warehousing, Software Engineering, Computer Networks, Algorithm Design, Microservices, Virtualization, Operating Systems, DBMS, Data Structures, Compiler Design, IT Infrastructure Management, Web App Development}}
\\end{{tabularx}}

\\vspace{{-3mm}}

\\section{{Work Experience}}
{tailored_experience}

\\vspace{{-5mm}}

\\section{{Project Work}}
{tailored_projects}

\\vspace{{-1mm}}

\\section{{Skills}}
{tailored_skills}

\\vspace{{-4mm}}

%---------------------------------------------------------------------------------------- 
% PUBLICATIONS
%---------------------------------------------------------------------------------------- 
\\section{{Achievements}}
{tailored_achievements}

\\end{{document}}
"""

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.tex', mode='w', encoding='utf-8')
    latex_filename = temp_file.name
    with open(latex_filename, 'w', encoding='utf-8') as f:
        f.write(final_latex)

    return send_file(latex_filename, as_attachment=True, download_name='final_resume.tex')

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
