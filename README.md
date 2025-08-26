# Student Clustering via Course Keywords and LDA

This project analyzes elective course selections at Columbia Business School (CBS) to uncover **student interest clusters**. By extracting keywords from course titles and descriptions and applying **Latent Dirichlet Allocation (LDA)** (a topic modeling technique), we can identify hidden themes in how students choose their electives.

Think of it as answering: *Do students naturally fall into groups like Finance-heavy, Entrepreneurship-focused, or Analytics-driven, without us pre-defining those labels?*

---

## 📂 Repository

**GitHub Repo:** [CBS-Github-DND](https://github.com/dyuthiii/CBS-Github-DND.git)

The repo contains:
- Jupyter notebooks for preprocessing, keyword extraction, and LDA modeling
- Data cleaning scripts
- CSV artifacts for audit and analysis

---

## 🚀 Project Workflow

### 1. Exploratory Data Analysis (EDA)
- Reviewed most popular electives and instructors  
- Checked changes over time and across student subgroups  
- Built initial correlation heatmaps for electives often taken together  
- Cleaned quirks like bad date formats in course names and missing IDs:contentReference[oaicite:0]{index=0}

---

### 2. Keyword Extraction & NLP Prep
- Created **clean course names** (using SIS and warehouse sources)  
- Split names and descriptions into **unigrams, bigrams, trigrams**  
- Applied **TF-IDF** to highlight distinctive phrases  
- Used **RAKE** and **YAKE** for keyword extraction  
- Manually curated outputs (removing meaningless terms like *“Half Term”*):contentReference[oaicite:1]{index=1}

---

### 3. Student Clustering with LDA
- Standardized keywords with **lemmatization**  
- Built a **student × keyword matrix** (rows = students, columns = keywords, values = counts)  
- Applied **LDA** to discover latent themes ("topics")  
- Assigned each student a distribution of topics (e.g., *60% Finance, 40% Entrepreneurship*)  
- Implemented a **fallback system** so no course is left untagged (title → description → YAKE top candidate):contentReference[oaicite:2]{index=2}

---

## 📊 Key Outputs

- **`lda_student_topic_distribution.csv`** → topic probabilities per student  
- **`lda_topic_term_weights.csv`** → top keywords per topic  
- **`lda_topic_labels_top10.csv`** → compact human-readable topic summaries  
- **`fallback_na_resolution_log.csv`** → audit trail of how missing values were handled  

---

## 💡 Why This Matters
- **Administrators** → track student interest trends across years  
- **Instructors** → see how their courses fit into broader themes  
- **Students** → potential for personalized course recommendations  

---

## 🔧 Tech Stack
- **Python**: Pandas, NumPy, Scikit-learn  
- **NLP**: spaCy, NLTK, RAKE, YAKE  
- **Modeling**: Latent Dirichlet Allocation (LDA)  
- **Visualization**: pyLDAvis, Matplotlib/Seaborn  
- **Environment**: Google Colab + Google Drive integration  

---

## ✅ Next Steps
- Refine the curated **keep map** (approved vocabulary)  
- Experiment with **guided LDA** (seed words for themes like "Finance")  
- Build interactive dashboards to explore clusters visually  

---

## 📜 License
This repository is for research and educational purposes. Please see the `LICENSE` file for details.

---

## 👩‍💻 Author
Dyuthi Dinesh  
M.A. Quantitative Methods in the Social Sciences, Columbia University  
[Personal Website](https://dyuthiii.github.io)

---
