# CBS Projects

This repository brings together three connected projects exploring **PRofessors' evaluations**, **student club enrollment**,**student elective course choices for LDA** at Columbia Business School (CBS). The overarching goal is to understand patterns in how students pick courses, and whether we can group them into **interest clusters** (e.g., Finance, Entrepreneurship, Analytics) without manually defining categories. Also built a dashboard on Tableau for **Peer School Comparisons** from 2019-2024. 

The repo is divided into three main components:

1. **Clean Historical Evaluation Data**
2. **Clean Historical Club Data**
3. **Update Peer School Comparison Charts**
4. **Student Clustering with LDA (Latent Dirichlet Allocation)**  

---
For Data and .csv,.xlsx files (only for authorized users from CBS): [GDrive](https://drive.google.com/drive/u/0/folders/1vyTL_F1gp1o8eD8DEUh9YKCQru8hwUa-) 
(This is a private gDrive link- only request access if you are Authorized by CBS, and email me: dnd2129@columbia.edu
## 📂 Repository Structure

## Repository Structure
(Note that this structure was AI generated due to the size of the repo-- some names or descriptions might be slightly inaccurate.)
```plaintext
CBS-Github-DND/                                                     # Root repo
├── Student Cluster Analysis and LDA-20250714T173604Z-1-001/        # Main project folder
│   ├── Student Cluster Analysis and LDA/                     # Cluster analysis + LDA work
|   |   ├── Student Cluster Analysis GDrive                      #All code on colab-- mostly used for NLP and LDA porcesses as large processing couldn't be handled locally
│   │   |  ├── code/                                                   # LDA + clustering notebooks/scripts
│   │   |  │   ├── LDA_final.ipynb
│   │   |  │   ├── NLP_LDA_coursenames_colab.ipynb
│   │   |  │   └── Student Cluster Analysis: Course Correlations.ipynb
│   │   |  ├── output/final/                                           # Final outputs-- these are in the form of .xlsx/.csv/google sheets. Cannot be accessed unless you have GDrive access.
│   │   |  └── 5 component topic_clusters.png                          # Topic cluster visualization
│   |   ├── Student Cluster Analysis and LDA.spyder/                    # Spyder IDE projects-- codes were simple initial explorations-- like EDA, and initial KMeans (which can be ignored)
│   │   |  ├── code/                                                   # Scripts for data prep, clustering, EDA
│   │   |  │   ├── EDA.py
│   │   |  │   ├── kmeans clustering.py
│   │   |  │   ├── course correlations_heatmap...py
│   │   |  │   ├── course name processing for NLP.py
│   │   |  │   ├── data wrangling.py
│   │   |  │   ├── merging indiv datasets.py
│   │   |  │   ├── merging raw course descriptions.py
│   │   |  │   ├── merging with clubpy
│   │   |  │   ├── new data combined course names.py
│   │   |  │   ├── NLP_LDA_coursenames_colab.ipynb
│   │   |  │   └── utils.py
│   │   |  ├── plots/                                                  # Visual outputs
│   │   │     ├── courses cor heatmap.png                                      
│   │   │     └── Student Cluster Analysis EDA.pbix                          #EDA on PowerBI 
│   │   ├── LDA README.md                                           # Notes on LDA
│   │   ├── EDA.docx                                                # EDA documentation
│   │   ├── LDA.docx                                                # LDA writeup
│   │   ├── NLP data prep.docx                                      # Data prep notes
│   ├── Project MasterDoc.docx                                  # Master project doc- links to Github and GDrive.
│   │     └── ~SP (data prep).docx                                    # Data prep notes (temp/backup)
│   └── .spyproject/config/                                         # IDE config
│
├── Task - Clean Clubs for Student Journey/                         # Club dataset cleaning
│   ├── code/                                                       # Scripts for club data processing
│   │   ├── Clubs Final dataset compilation.py
│   │   ├── club membership comparison.py
│   │   └── club officer comparison.py
│   ├── process/                                                    # Process documentation
│   │   └── club cleaning process.docx
│   └── .spyproject/config/                                         # IDE config
│
├── Task - Clean Historical Evaluation Data/                        # Course evaluation cleaning + matching
│   ├── UNI Matching/                                               # Instructor UNI mapping
│   │   ├── Cleaning Evaluations.py
│   │   ├── ensemble matching model.py
│   │   ├── multiple profs-- splitting to rows and mapping uni.py
│   │   └── uni matching process.docx
│   ├── deduplicated evals one row per prof per course per term/    # Deduplication of evals
│   │   ├── Cleaning final_evals...py
│   │   └── Process for one row per course.docx
│   ├── missing SIS courses/                                        # Handle SIS course mismatches
│   │   ├── Missing SIS courses from course evals.py
│   │   └── Missing SIS courses process.docx
│   ├── older versions/                                             # Archived scripts/processes-- can ignore
│   │   ├── matching tcdb and evals ratings.py
│   │   └── ratings comparison process.docx
│   ├── process/                                                    # Process documentation
│   │   └── Cleaning Historical Evaluation Data.docx
│   └── .spyproject/config/                                         # IDE config
│
├── Task - Update Peer School Comparison Data Charts/               # Tableau peer school analysis
│   ├── 2025 Top 30 Peer Schools Board Book Charts.twbx             # 2025 packaged workbook
│   ├── Peer Schools Board Book Charts.twbx                         # Main workbook
│   └── ~Peer Schools Board Book Charts__15448.twbx                 # Tableau temp file
│
├── .gitattributes                                                  # Git attributes config
├── .gitignore                                                      # Ignore rules
└── README.md                                                       # Repo-level README

Note: "old" directories refer to Archived scripts/processes-- can ignore. It's only there for documentation purposes. 
