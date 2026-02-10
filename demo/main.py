# main.py
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from .Modelo_ML import app as modelo_app

app = FastAPI()

# Montamos la app de ML en /demo
app.mount("/demo", modelo_app)

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <html>
    <head>
        <title>Francisco Leonel Luna - Data Engineer</title>
        <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">
        <style>
            body {
                font-family: 'Roboto', sans-serif;
                margin: 0; padding: 0;
                background: #f7f9fc;
                color: #333;
            }
            header {
                background: linear-gradient(90deg, #1E3A8A, #3B82F6);
                color: white;
                padding: 40px 20px;
                text-align: center;
            }
            header h1 {
                margin: 0;
                font-size: 2.5rem;
            }
            header p {
                font-size: 1.2rem;
                margin-top: 5px;
            }
            .container {
                max-width: 1000px;
                margin: 30px auto;
                padding: 0 20px;
            }
            .section {
                margin-bottom: 40px;
            }
            h2 {
                color: #1E3A8A;
                border-bottom: 3px solid #3B82F6;
                display: inline-block;
                padding-bottom: 5px;
                margin-bottom: 15px;
            }
            .card {
                background: white;
                border-radius: 12px;
                padding: 20px;
                margin-bottom: 15px;
                box-shadow: 0 4px 10px rgba(0,0,0,0.08);
                transition: transform 0.2s ease, box-shadow 0.2s ease;
            }
            .card:hover {
                transform: translateY(-5px);
                box-shadow: 0 8px 20px rgba(0,0,0,0.15);
            }
            a.button {
                background: #3B82F6;
                color: white;
                padding: 10px 20px;
                border-radius: 8px;
                text-decoration: none;
                margin-right: 10px;
                font-weight: bold;
                transition: background 0.2s ease;
            }
            a.button:hover {
                background: #1E3A8A;
            }
            ul { margin: 0; padding-left: 20px; }
            .skills span {
                display: inline-block;
                background: #e0f2fe;
                color: #0369a1;
                padding: 5px 10px;
                border-radius: 8px;
                margin: 3px;
                font-size: 0.9rem;
            }
        </style>
    </head>
    <body>
        <header>
            <h1>Francisco Leonel Luna Najera</h1>
            <p>Data Engineer | Mechatronics & Data Science</p>
        </header>

        <div class="container">
            <div class="section card">
                <h2>Contact & Info</h2>
                <p><strong>Age:</strong> 26 | <strong>Address:</strong> Tijuana, B.C., Mexico</p>
                <p><strong>Cellphone:</strong> +52 664 419 0412 | <strong>Email:</strong> <a href="mailto:lunf990517@gmail.com">lunf990517@gmail.com</a></p>
                <p><strong>Valid Visa:</strong> Laser | <strong>Driver License:</strong> Valid</p>
                <a href="/demo" class="button">Try My ML Demo</a>
                <a href="/CV FRANCISCO LEONEL LUNA NAJERA.pdf" class="button" target="_blank">Download CV</a>
            </div>

            <div class="section card">
                <h2>About Me</h2>
                <p>
                    Proactive and results-driven data professional with creativity, persistence, and adaptability.
                    Strong communicator with a collaborative mindset. Delivers high-quality outcomes with analytical thinking
                    and flexibility to meet any project requirements.
                </p>
            </div>

            <div class="section card">
                <h2>Education</h2>
                <ul>
                    <li>2017-2021: Mechatronics Engineer - Universidad Tecnológica de Tijuana</li>
                    <li>2025-Present: Master’s Degree in Data Science - IEXE Universidad</li>
                </ul>
            </div>

            <div class="section card">
                <h2>Projects & Certifications</h2>
                <ul>
                    <li>PLC Certification (EC0304)</li>
                    <li>Power BI Course</li>
                    <li>Software for Discrepant Material Management (Amphenol Thermometrics)</li>
                    <li>GCP Associate Cloud Engineer Course</li>
                    <li>Lean 4.0 Course</li>
                    <li>Machine Learning Sales Forecasting (Master’s Project)</li>
                </ul>
                <p class="skills">
                    <span>Python</span> <span>SQL</span> <span>Machine Learning</span> <span>Web Scraping</span>
                    <span>REST APIs</span> <span>BigQuery</span> <span>Docker</span> <span>Power BI</span> <span>GCP</span>
                </p>
            </div>

            <div class="section card">
                <h2>Work Experience</h2>
                <h3>Bluetab México (Mar 2023 - Present)</h3>
                <ul>
                    <li>Automated data workflows using Apache Airflow, orchestrated on GCP clusters.</li>
                    <li>Optimized SQL queries in BigQuery & Hive for large-scale ETL workloads.</li>
                    <li>Developed interactive dashboards in Power BI & Tableau.</li>
                    <li>Managed data ingestion pipelines via Google Cloud Storage (GCS).</li>
                    <li>Built internal data portals for analytics and reporting.</li>
                    <li>Supported AI/ML initiatives for model training & evaluation.</li>
                </ul>

                <h3>Thermometrics México (Oct 2020 - Mar 2023)</h3>
                <ul>
                    <li>Developed & maintained KPI monitoring software in SQL Server.</li>
                    <li>Implemented company-wide reporting in Power BI.</li>
                    <li>Performed validation protocols and personnel training.</li>
                    <li>Automated processes across departments with custom applications.</li>
                </ul>
            </div>
        </div>
    </body>
    </html>
    """
