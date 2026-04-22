# ML Tasks — Library Cheatsheet & Quick Reference

## Library Recommendations by Task

### EDA — Image Dataset
```
Pillow (PIL)       — open, read, resize images; check channels and modes
numpy              — pixel array conversion, mean/std/histogram
matplotlib         — plotting: grid of sample images, bar charts, histograms
collections        — Counter for class distribution
hashlib (md5)      — detect duplicate images by file hash
pathlib            — traverse directories cleanly
```

**Typical class structure:** Either flat (all images in one folder, labeled by filename)
or subfolders-per-class (most common — each class = one folder).

**Corrupted image detection:** Wrap `Image.open(path).verify()` in a try/except.
`verify()` must be called on a freshly opened image — it closes the file after running.

**Duplicate detection:** MD5 hash of raw file bytes. Same hash = same file.
Do NOT compare pixel arrays — too slow for large datasets.

### EDA — Tabular / CSV
```
pandas             — load, inspect, describe, null counts, dtypes
seaborn            — heatmap (correlations), boxplot, pairplot, countplot
matplotlib         — histograms, bar charts
scipy.stats        — skewness, kurtosis if needed
```

### Data Preprocessing
```
sklearn.preprocessing    — StandardScaler, MinMaxScaler, LabelEncoder, OneHotEncoder
sklearn.model_selection  — train_test_split, StratifiedKFold
sklearn.impute           — SimpleImputer, KNNImputer
Pillow / torchvision     — image augmentation (flip, rotate, crop, normalize)
albumentations           — fast, rich image augmentation library
numpy                    — array ops, normalization
```

### Classification — Traditional ML
```
sklearn.ensemble         — RandomForestClassifier, GradientBoostingClassifier
sklearn.svm              — SVC
sklearn.linear_model     — LogisticRegression
sklearn.neighbors        — KNeighborsClassifier
sklearn.metrics          — classification_report, confusion_matrix, roc_auc_score
xgboost / lightgbm       — for tabular data with high performance needs
```

### Classification — Deep Learning
```
PyTorch + torchvision    — preferred for CV tasks; flexible
TensorFlow / Keras       — simpler API, good for quick prototypes
torchvision.datasets     — ImageFolder for standard image classification
torchvision.transforms   — standard augmentation pipeline
torch.utils.data         — DataLoader, Dataset
```

### Regression
```
sklearn.linear_model     — LinearRegression, Ridge, Lasso, ElasticNet
sklearn.ensemble         — RandomForestRegressor, GradientBoostingRegressor
sklearn.metrics          — mean_squared_error, mean_absolute_error, r2_score
statsmodels              — detailed regression stats, p-values, confidence intervals
```

### Clustering
```
sklearn.cluster          — KMeans, DBSCAN, AgglomerativeClustering, MeanShift
sklearn.metrics          — silhouette_score, davies_bouldin_score
sklearn.decomposition    — PCA (for visualization before/after clustering)
matplotlib               — scatter plots with cluster color labels
```

### NLP
```
transformers (HuggingFace) — BERT, GPT-2, sentiment analysis, zero-shot, etc.
nltk                       — tokenization, stopwords, stemming (quick tasks)
spacy                      — NER, dependency parsing, fast production NLP
sklearn.feature_extraction — TfidfVectorizer, CountVectorizer
gensim                     — Word2Vec, Doc2Vec, topic modeling
```

### Computer Vision (beyond basic image loading)
```
torchvision                — pretrained models (ResNet, EfficientNet, ViT)
OpenCV (cv2)               — image transforms, contour detection, video
Pillow                     — simple image I/O and manipulation
CLIP (OpenAI)              — image-text matching, zero-shot classification
```

### Model Evaluation
```
sklearn.metrics            — classification_report, confusion_matrix,
                             roc_curve, auc, precision_recall_curve,
                             mean_squared_error, r2_score
matplotlib                 — plot confusion matrix heatmap, ROC curve, PR curve
seaborn                    — heatmap for confusion matrix (nicer than raw matplotlib)
```

---

## Common Pitfalls — Avoid These in Generated Code

**Data leakage**
- Never fit scalers/encoders on the full dataset before splitting. Fit on train, transform test.
- Never include the target column in feature selection based on post-split stats.

**Forgetting to split**
- Always create train/val/test splits unless the task explicitly says otherwise.
- Use `stratify=y` in `train_test_split` for classification to preserve class ratios.

**Class imbalance blindness**
- Always check and report class distribution. Flag if any class is < 10% of the dataset.
- In classification, check `class_weight='balanced'` or use SMOTE for severe imbalance.

**plt.show() in scripts**
- Never call `plt.show()` in a script. It blocks execution. Always use `plt.savefig()`.
- Always call `plt.close()` after saving to free memory.

**Hardcoded paths**
- Dataset path and output directory must be variables at the top of the script.

**No error handling on file I/O**
- Always check that the dataset path exists before processing.
- For image loading, wrap in try/except to catch corrupted files.

**Ignoring stdout structure**
- Print section headers (e.g., `--- Dataset Overview ---`) so captured output is readable.
- Use `print()` after each major step, not just at the end.

---

## Evaluation Metrics Quick Reference

| Task | Primary Metrics | Notes |
|------|----------------|-------|
| Binary classification | Accuracy, Precision, Recall, F1, AUC-ROC | Use F1 + AUC for imbalanced data |
| Multi-class classification | Macro/Weighted F1, Confusion matrix | Macro F1 treats all classes equally |
| Regression | MAE, RMSE, R² | RMSE penalizes large errors more |
| Clustering | Silhouette score, Davies-Bouldin | Silhouette: -1 to 1, higher is better |
| Ranking/retrieval | MAP, NDCG, MRR | Used in recommendation systems |

---

## Image Dataset Format Reference

**Subfolder-per-class (most common):**
```
dataset/
├── class_a/
│   ├── img001.jpg
│   └── img002.png
├── class_b/
│   └── img003.jpg
└── class_c/
    └── img004.jpeg
```
Detection: `[d for d in Path(dataset_path).iterdir() if d.is_dir()]`

**Flat with label file:**
```
dataset/
├── img001.jpg
├── img002.jpg
└── labels.csv  (filename, label)
```
Detection: look for a CSV/JSON alongside images.

Use `torchvision.datasets.ImageFolder` for the subfolder structure — it handles
class detection and indexing automatically.
