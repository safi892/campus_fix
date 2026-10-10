CampusFix AI: Review, Hurdles, Features and Presentation Plan

Overview
The roadmap is solid, and its strongest rules are what judges read as engineering maturity rather than AI slop.
• Never delete reports when grouping duplicates.
• Staff stay in the loop on every AI suggestion.
• The app keeps working even if the ML model fails to load.
Below are the stack decision, the hurdles you are likely to hit, features worth adding, and how to present.
Tech stack: Next.js + Flask
Next.js + Flask works, but it conflicts with your own roadmap, which says HTML + Bootstrap + Flask. It means two apps, two servers, and an API between them.
What you gain: a more modern look and a more impressive-looking product.
What you pay:
• CORS issues, API contracts, and two things to run and deploy
• Slower iteration, because every feature touches both sides
• Hours lost to integration bugs instead of building features
Recommendation, by team skill:
• At least two of you know React/Next.js well: keep Next.js and use Flask purely as a JSON API. Agree on the API shape (endpoints and fields) on day one and write it down.
• Frontend skills are shaky: stay with Flask + Jinja templates + Bootstrap or Tailwind. A well-designed server-rendered app beats a broken, half-integrated Next.js app every time.
Flask vs FastAPI: with a separate frontend, FastAPI is worth considering because it auto-generates interactive API docs, which makes frontend/backend coordination easier. Flask is fine too; pick whichever your ML person knows better.
Database: SQLite is right for a hackathon. Don't change it.
Hurdles you will likely face
Hurdle
Why it hurts
What to do
Scope creep
The biggest killer; everyone wants "just one more feature"
Freeze the feature list at the halfway point
MiniLM setup pain
First run downloads the model (needs internet); PyTorch is heavy
Download and test early; keep a TF-IDF similarity fallback
No real data
Duplicate detection and classification need examples
Write 50-100 realistic labelled complaints; assign this early
Threshold tuning
A cutoff that works on 3 examples falls apart on 30
Build a small labelled test set and report an honest accuracy number
Git chaos
Merge conflicts and "works on my machine"
Agree on branches, small commits, and one integrator
Demo-day failure
Wi-Fi dies, the model won't load, the database is empty
Pre-load sample data and record a backup demo
Photo uploads
Look simple but bring file validation, storage and security issues
Make them a stretch goal
Believability
Judges ask "who actually uses this?" and "how accurate is the AI?"
Prepare answers and real evaluation numbers
Features that make it stand out
High impact, achievable
• Duplicate clusters with an "N students reported this" counter. Your core differentiator. The count becomes the priority signal: ten reports about one broken AC outrank one loose chair.
• Explainable suggestions. Show why something was flagged ("similar to Report #12, same building, 0.84 similarity"), and let staff accept or reject. This transparency separates a real product from a chatbot wrapper.
• Safety escalation rules. Keywords like "exposed wire," "sparks," "gas smell" and "flooding" trigger a visible urgent flag. Simple, memorable, and shows responsible AI.
• Student-facing tracking. After submitting, the student gets a reference code and a status page. Closing the loop for the reporter is something most teams forget.
• Duplicate prevention at submission time. While the student types, show "similar issue already reported, add your voice instead?" It cuts staff workload at the source and makes a great live demo moment.
• Hotspot view. A chart or heatmap-style table of which buildings generate the most issues, so staff can plan maintenance proactively.
• Honest evaluation slide. "We tested on 60 labelled reports: duplicate detection precision was X%, and here are the failure cases." Almost no team does this, and judges notice.
Nice if time allows
• Priority score combining duplicate count, safety flags, and age of the issue
• Multilingual reports: students may write in Urdu or Roman Urdu, and an English MiniLM model will struggle, so be honest about the limit or test a multilingual model
• Staff assignment ("assigned to electrician team")
• Email or notification on status change, even simulated
Skip these
• Authentication systems
• Mobile apps
• Chatbots
• Anything needing paid APIs
Presentation advice
The presentation is half of winning.
• Open with a story, not the tech. "A student reports a broken cooler. So do 14 others. Staff see 15 separate tickets." Then show the fix.
• Rehearse the demo. Run the scenario from your roadmap at least 10 times.
• Prepare a backup. Keep a screen recording of the full demo and a pre-loaded database with sample data.
• Be upfront about limitations. "Here is where our AI fails and how staff stay in control" scores higher than claiming 99% accuracy.
• Have one number ready: reports in, unique issues out, workload reduction percentage, labelled as based on sample data.
Prepare for likely questions
• Why not just use a form or spreadsheet?
• How accurate is it?
• What about privacy?
• How would a university adopt it?
Suggested priority order
Reserve the last 20% of your time for testing and presentation only, with no new features.
1. Working submit, dashboard and status flow (with the stack decision made)
2. Seeded realistic demo data
3. Duplicate detection with staff accept/reject
4. Safety escalation and category suggestion
5. Student tracking page and duplicate warning at submit time
6. Metrics and evaluation numbers
7. Polish, pitch, and backup recording
All four of you should read the code Kiro produces. If you can't explain a part during judging, expect to be asked about exactly that part.
Two open questions would let me tighten the stack choice and trim the roadmap: how long the hackathon is, and how comfortable your team is with React.