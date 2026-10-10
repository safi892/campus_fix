We are building CampusFix AI for a university hackathon.

PRODUCT:
Students submit campus maintenance complaints. Staff review reports, identify similar complaints, prioritize issues, and track resolution.

STACK:

- Python
- Flask
- SQLite
- HTML, CSS, Bootstrap
- scikit-learn
- sentence-transformers using all-MiniLM-L6-v2, running on CPU

WORKING RULES:

1. Inspect the current project before changing anything.
2. We are beginners, so explain new files and important decisions in simple English.
3. Build only one milestone at a time.
4. Never claim a feature works until you have run or tested it.
5. Avoid paid APIs and external services for the core workflow.
6. Keep the application usable if the ML model fails to load.
7. Use parameterized SQL queries, input validation, safe file-upload handling, and clear error messages.
8. Keep credentials and local configuration out of source control.
9. Never delete reports when grouping duplicates.
10. Keep safety and urgency decisions under staff review.
11. Do not create authentication, deployment infrastructure, a mobile app, or unnecessary architecture yet.
12. Use Git checkpoints where possible.

FIRST MILESTONE ONLY:

- Set up a Python virtual environment and Flask.
- Create a simple, polished, responsive landing page for CampusFix AI.
- Add a shared base template and static CSS.
- Add a health-check route.
- Add a README with exact setup and run commands.
- Add a requirements file with compatible dependency versions.
- Run the application and test the landing page and health-check route.

Do not implement the database, AI, duplicate detection, or dashboard yet. First show me the proposed file structure and implementation plan. Then implement this milestone and tell me exactly how to run and verify it.