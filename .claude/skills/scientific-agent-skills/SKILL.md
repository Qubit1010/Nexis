---
name: scientific-agent-skills
description: >
  Router for 147 scientific and research skills from K-Dense-AI. Use this when the user
  mentions a specific scientific tool, library, or domain — e.g., "use scanpy", "help with
  PyTorch Lightning", "run a literature review", "analyze this PDF", "do exploratory data
  analysis", "write a research paper", "quantum circuit with Qiskit", "molecular docking",
  "single-cell RNA-seq", "SHAP values", "Polars dataframe", "bulk RNA-seq", "Nextflow pipeline",
  or any scientific computing, bioinformatics, chemistry, ML/DL, or research task that matches
  a known library or tool. Trigger on tool names, task descriptions, or domain keywords.
---

# Scientific Agent Skills Router

You have access to 147 specialized scientific skills. When a user request matches one of them:

1. Identify the best matching skill(s) from the catalog below
2. Read its SKILL.md: `.claude/skills/scientific-agent-skills/<name>/SKILL.md`
3. Follow those instructions exactly — they contain setup, usage patterns, and tool-specific guidance

If multiple skills apply, read all relevant ones and integrate their guidance.

---

## Skill Catalog

### ML / Deep Learning
- **scikit-learn** — Supervised/unsupervised ML: classification, regression, clustering, pipelines, cross-validation
- **pytorch-lightning** — Deep learning with PyTorch Lightning: LightningModules, multi-GPU, DDP/FSDP, W&B logging
- **transformers** — Hugging Face Transformers: Hub models, pipeline inference, text generation, Trainer fine-tuning
- **stable-baselines3** — Reinforcement learning (PPO, SAC, DQN, TD3, A2C) with scikit-learn-like API
- **pufferlib** — High-performance parallel RL framework for speed and scale
- **torchdrug** — GNNs for molecules and proteins; drug discovery with PyTorch-native graph architectures
- **torch-geometric** — PyTorch Geometric: GCN, GAT, GraphSAGE for node/link/graph tasks
- **umap-learn** — UMAP for nonlinear dimensionality reduction, 2D/3D embeddings, clustering preprocessing
- **shap** — SHAP values for model interpretability and explainability across any ML model
- **hugging-science** — Hugging Face ecosystem in scientific domains: biology, chemistry, physics, climate
- **timesfm-forecasting** — Zero-shot time series forecasting with Google's TimesFM foundation model
- **aeon** — Time series ML: classification, regression, clustering, forecasting, anomaly detection
- **autoskill** — Screen-aware workflow detection and scientific skill routing via screenpipe
- **hypogenic** — LLM-driven hypothesis generation and testing on tabular datasets
- **optimize-for-gpu** — GPU-accelerate Python: CuPy, Numba CUDA, cuDF, cuML, cuGraph

### Data Science & Statistics
- **polars** — High-performance DataFrames for ETL, analytics, pandas migration
- **dask** — Distributed computing for larger-than-RAM pandas/NumPy workflows
- **vaex** — Lazy evaluation for billions of rows that exceed RAM
- **statsmodels** — OLS, GLM, mixed models, ARIMA, time series models with p-values and confidence intervals
- **pymc** — Bayesian modeling with PyMC: hierarchical models, MCMC (NUTS), variational inference
- **sympy** — Exact symbolic math: algebra, calculus, equation solving, symbolic linear algebra
- **matplotlib** — Low-level plotting for full customization, publication figures, complex layouts
- **seaborn** — Statistical visualization with pandas integration: distributions, relationships, categories
- **networkx** — Complex network analysis and visualization in Python
- **simpy** — Process-based discrete-event simulation for queuing, resources, logistics
- **statistical-analysis** — Guided test selection and reporting: t-tests, ANOVA, chi-square, non-parametric
- **statistical-power** — Sample-size and power calculations for study planning
- **exploratory-data-analysis** — Comprehensive EDA across 200+ file formats
- **experimental-design** — Study design before data collection: randomization, blocking, factorial design
- **pymoo** — Multi-objective optimization: NSGA-II, NSGA-III, Pareto fronts

### Single-Cell / Omics
- **scanpy** — Standard scRNA-seq pipeline: QC, normalization, PCA/UMAP, clustering, DE analysis
- **scvi-tools** — Deep generative models: scVI batch correction, scANVI, totalVI, DestVI
- **anndata** — Annotated matrix data structure (.h5ad) for scverse ecosystem
- **cellxgene-census** — Query CZ CELLxGENE Census for public single-cell and spatial transcriptomics data
- **scvelo** — RNA velocity: cell state transitions from unspliced/spliced mRNA dynamics
- **bulk-rnaseq** — End-to-end bulk RNA-seq: FastQC, STAR, DESeq2/edgeR, pathway enrichment
- **pydeseq2** — Differential expression with PyDESeq2: Wald tests, FDR correction
- **pathway-enrichment** — Pathway and gene-set enrichment: GSEA, ORA, KEGG, Reactome, MSigDB
- **arboreto** — Gene regulatory network inference: GRNBoost2, GENIE3
- **lamindb** — Lineage-native lakehouse for biological datasets, models, and artifacts
- **polars-bio** — High-performance genomic interval operations and bioinformatics I/O on Polars DataFrames
- **gtars** — Fast genomic interval analysis with Rust-backed Python bindings
- **tiledbvcf** — Scalable VCF/BCF ingestion and retrieval with TileDB
- **pysam** — SAM/BAM/CRAM/VCF toolkit: alignments, variants, region extraction
- **deeptools** — NGS analysis: BAM→bigWig, QC (correlation, PCA, fingerprint), heatmaps, TSS profiles
- **geniml** — Genomic interval machine learning on BED files: training, embedding, search
- **pyhealth** — Clinical deep-learning pipelines: EHR/signal/imaging datasets (MIMIC-III/IV, eICU)
- **flowio** — Parse FCS files (v2.0–3.1): flow cytometry events as NumPy arrays

### Bioinformatics
- **biopython** — Molecular biology toolkit: sequence manipulation, FASTA/GenBank/PDB parsing, BLAST
- **bioservices** — Unified Python interface to 40+ bioinformatics databases (UniProt, KEGG, ChEMBL)
- **gget** — Fast CLI/Python queries to 20+ databases: gene info, BLAST, viral sequences
- **etetoolkit** — Phylogenetic tree manipulation, evolutionary events, orthology/paralogy (ETE)
- **phylogenetics** — Build phylogenetic trees: MAFFT alignment, IQ-TREE 2, FastTree, tree visualization
- **scikit-bio** — Biological sequence analysis, alignments, diversity metrics (alpha/beta, UniFrac)
- **histolab** — WSI tile extraction and preprocessing: tissue detection, tile extraction
- **pathml** — Computational pathology: multiplexed IF, whole-slide image analysis
- **bids** — BIDS (Brain Imaging Data Structure) standard for neuroimaging datasets
- **neuropixels-analysis** — Neuropixels recordings with SpikeInterface: spike sorting, SpikeGLX/Open Ephys
- **neurokit2** — Biosignal processing: ECG, EEG, EDA, RSP, PPG, EMG
- **pacsomatic** — nf-core/pacsomatic tumor-normal BAM workflows

### Chemistry & Drug Discovery
- **rdkit** — Cheminformatics: SMILES/SDF parsing, fingerprints, scaffold analysis, substructure search
- **deepchem** — Molecular ML: ADMET/toxicity prediction with diverse featurizers
- **molfeat** — Molecular featurization (100+ featurizers): ECFP, MACCS, ChemBERTa
- **datamol** — Pythonic RDKit wrapper with sensible defaults for standard drug discovery tasks
- **medchem** — Medicinal chemistry filters: Lipinski, Veber, CNS, structural alerts, triage
- **matchms** — Spectral similarity and compound ID for metabolomics: MS/MS comparison
- **rowan** — Cloud molecular modeling: pKa, solubility, redox, conformers via Rowan API
- **pytdc** — Therapeutics Data Commons: AI-ready drug discovery datasets and benchmarks
- **diffdock** — DiffDock protein-small molecule docking: pose prediction from PDB/sequence + SMILES
- **pyopenms** — Mass spectrometry: feature detection, peptide/metabolite quantification
- **cobrapy** — Constraint-based metabolic modeling: FBA, FVA, knockouts, SBML
- **pymatgen** — Materials science: crystal structures, phase diagrams, band structure, Materials Project
- **molecular-dynamics** — MD simulations with OpenMM and MDAnalysis: protein/ligand systems, force fields
- **glycoengineering** — Protein glycosylation analysis: N/O-glycosylation site prediction and engineering
- **esm** — ESM3/ESMC protein language models via Forge/Biohub inference clients
- **adaptyv** — Adaptyv Bio Foundry API: protein experiment design, BLI/SPR/thermostability assays

### Quantum Computing
- **qiskit** — IBM Quantum: circuits, Qiskit Runtime, pulse-level control, quantum error correction
- **pennylane** — Hardware-agnostic quantum ML with automatic differentiation, VQE, QAOA
- **cirq** — Google Quantum AI: noise-aware circuits, device topology, Cirq Simulator
- **qutip** — Quantum physics simulation: master equations, Lindblad dynamics, density matrices

### Lab Automation & Integration
- **opentrons-integration** — Opentrons OT-2 and Flex robot protocol API
- **pylabrobot** — Vendor-agnostic lab automation: Hamilton, Tecan, Opentrons, liquid handlers
- **ginkgo-cloud-lab** — Ginkgo Bioworks Cloud Lab: protocol submission and autonomous lab management
- **omero-integration** — OMERO microscopy platform: image access, datasets, ROIs via Python
- **labarchive-integration** — LabArchive ELN API: notebooks, entries, attachments
- **latchbio-integration** — Latch bioinformatics workflows: @workflow/@task decorators, serverless deployment
- **dnanexus-integration** — DNAnexus cloud genomics: apps/applets, dxpy SDK, data management
- **benchling-integration** — Benchling registry, inventory, ELN, and workflow API
- **protocolsio-integration** — protocols.io API: manage, fork, and publish scientific protocols
- **pyzotero** — Zotero reference management: retrieve, create, update items via pyzotero client

### Documents & Writing
- **docx** — Create, read, edit Word documents (.docx)
- **pptx** — Any .pptx task: create slides, edit presentations, extract content
- **pdf** — PDF tasks: text extraction, tables, annotations, splitting, merging
- **xlsx** — Excel spreadsheets: create, edit, analyze, convert (.xlsx, .xlsm)
- **latex-posters** — Research posters in LaTeX: beamerposter, tikzposter, conference formats
- **pptx-posters** — Research posters via HTML/CSS exported to PDF or PPTX
- **scientific-writing** — Write scientific manuscripts: full paragraphs, sections, methods, results
- **markdown-mermaid-writing** — Scientific documents with Mermaid diagrams: flowcharts, sequence, ER
- **liteparse** — Local PDF/DOCX parsing with spatial text and bounding boxes
- **markitdown** — Convert PDF, DOCX, PPTX, XLSX, images, audio to Markdown
- **scientific-slides** — Build slide decks and presentations for research talks and conferences

### Research & Literature
- **literature-review** — Systematic reviews via PubMed, arXiv, bioRxiv, Semantic Scholar; formatted docs with citations
- **paper-lookup** — Search 10 academic databases (PubMed, arXiv, Semantic Scholar, CrossRef, OpenAlex)
- **bgpt-paper-search** — Scientific papers and structured experimental data via BGPT MCP
- **exa-search** — Exa-powered web search tuned for scientific and technical content
- **parallel-web** — parallel-cli web toolkit emphasizing academic and scientific sources
- **citation-management** — Search Google Scholar/PubMed, extract accurate BibTeX, format citations
- **research-grants** — Write NSF, NIH, DOE, DARPA grant proposals with agency-specific formatting
- **paperzilla** — Chat about projects and canonical papers in the Paperzilla knowledge base
- **research-lookup** — parallel-cli + Parallel Chat API for deep research questions
- **database-lookup** — Query 78 public databases: biomedical, materials, regulatory, finance, demographics
- **depmap** — Cancer Dependency Map: CRISPR dependency scores, drug sensitivity, cell line data
- **primekg** — Precision Medicine Knowledge Graph: genes, drugs, diseases, pathways
- **usfiscaldata** — U.S. Treasury Fiscal Data API: national debt, federal spending, revenue
- **imaging-data-commons** — NCI Imaging Data Commons: public cancer imaging data via idc-index
- **open-notebook** — Self-hosted alternative to NotebookLM for AI-powered research and document analysis

### Visualization & Design
- **scientific-visualization** — Publication-ready multi-panel figures for journal submission
- **scientific-schematics** — Publication-quality scientific diagrams via Nano Banana 2 AI
- **infographics** — Professional infographics via Nano Banana Pro AI with iterative refinement
- **generate-image** — AI image generation and editing (FLUX, Nano Banana 2)

### Scientific Process
- **hypothesis-generation** — Structured hypothesis formulation from observations and data
- **scientific-brainstorming** — Creative research ideation, interdisciplinary connection, open-ended exploration
- **scientific-critical-thinking** — Evaluate scientific claims, experimental design validity, biases, statistical issues
- **peer-review** — Structured manuscript/grant review with checklist-based evaluation
- **scholar-evaluation** — Systematic scholarly work evaluation using the ScholarEval framework
- **experimental-design** — Study design before data collection: randomization, blocking, controls
- **what-if-oracle** — Structured What-If scenario analysis with 4-6 branch possibility exploration

### Clinical & Medical
- **clinical-decision-support** — Clinical decision support documents for pharmaceutical and clinical research
- **clinical-reports** — Clinical reports: case reports (CARE), radiology, pathology, discharge summaries
- **treatment-plans** — Medical treatment plans (3-4 pages, LaTeX/PDF) for any clinical specialty
- **pydicom** — DICOM file reading, writing, and manipulation for medical imaging
- **iso-13485-certification** — ISO 13485 QMS documentation for medical device certification

### Geospatial & Earth Science
- **geopandas** — Geospatial vector data: shapefiles, GeoJSON, spatial joins, projections
- **geomaster** — Remote sensing, GIS, spatial analysis, ML for earth observation and mapping
- **astropy** — Astronomy and astrophysics: units, coordinates, FITS, time, WCS

### Simulation & Optimization
- **fluidsim** — Computational fluid dynamics simulations in Python
- **simpy** — Discrete-event simulation: queuing, resources, logistics, factories
- **pymoo** — Multi-objective optimization: NSGA-II, NSGA-III, Pareto fronts, constraint handling
- **arbor** — Iterative artifact improvement (code, training recipe, data pipeline) against an objective

### Other Scientific Computing
- **matlab** — MATLAB and GNU Octave: matrix operations, data analysis, scientific computing
- **nextflow** — Nextflow pipelines and nf-core workflows: build, run, debug, deploy
- **modal** — Serverless cloud Python with on-demand GPUs: deploy, scale, run jobs
- **pi-agent** — Pi terminal coding harness: install, configure providers/models, run agents
- **consciousness-council** — Multi-perspective deliberation for complex decisions or creative challenges
- **dhdna-profiler** — Extract cognitive patterns and thinking fingerprints from text
- **get-available-resources** — Detect available compute resources (CPU, GPU, RAM) before intensive tasks
- **venue-templates** — LaTeX templates and formatting for major scientific publication venues
- **research-grants** — NSF, NIH, DOE, DARPA, NSTC grant proposal writing with review criteria

---

## How to Route

When the user's request matches a skill above:

```
Read the file at:
.claude/skills/scientific-agent-skills/<skill-name>/SKILL.md
```

Then follow the instructions in that file. The sub-skill SKILL.md contains specific:
- Tool setup and imports
- Recommended workflows
- Code patterns and examples
- API usage notes

If no specific skill matches but the request is scientific in nature, use `literature-review`, `exploratory-data-analysis`, `hypothesis-generation`, or `scientific-writing` as appropriate defaults.
