# PhishGuardXAI 🛡️

An Explainable AI-based phishing detection system that uses machine learning and deep learning models to identify malicious URLs and provide understandable explanations for predictions.

## 📌 Overview

Phishing attacks are one of the most common cybersecurity threats where attackers use fake websites and URLs to steal sensitive information.

**PhishGuardXAI** aims to detect phishing websites using Artificial Intelligence while also explaining why a URL is classified as safe or malicious using Explainable AI (XAI) techniques.

The system combines multiple AI approaches:

* Machine Learning-based detection
* Deep Learning models
* Graph-based learning
* Ensemble prediction
* Explainable AI methods

## 🚀 Features

* Detects phishing and legitimate URLs
* Extracts URL-based security features
* Uses machine learning models for classification
* Provides explainable predictions
* Supports multiple model architectures:

  * LightGBM
  * BERT
  * Graph Neural Network (GNN)
  * Ensemble Model

## 🏗️ Project Structure

```
PhishGuardXAI
│
├── backend
│   └── API services
│
├── browser_extension
│   └── Browser-based phishing detection
│
├── database
│   └── Database configurations
│
├── datasets
│   ├── raw
│   │   └── Original datasets
│   └── processed
│       └── Preprocessed datasets
│
├── frontend
│   └── User interface
│
├── models
│   ├── lightgbm
│   │   ├── train.py
│   │   └── lightgbm_model.pkl
│   │
│   ├── bert
│   ├── gnn
│   └── ensemble
│
├── xai
│   └── Explainable AI components
│
└── README.md
```

## 🧠 Models

### 1. LightGBM Model

The LightGBM model detects phishing URLs using extracted URL-based features.

### Features Used:

* URL Length
* Number of dots
* Number of hyphens
* Number of digits
* HTTPS presence
* Number of slashes
* Number of underscores
* Number of question marks
* Number of equal signs
* Presence of '@'
* IP address detection

### Performance

Current LightGBM model:

* Accuracy: **87%**

## 🔄 Machine Learning Pipeline

```
Dataset
   |
   ↓
Data Cleaning
   |
   ↓
Feature Extraction
   |
   ↓
Train-Test Split
   |
   ↓
LightGBM Training
   |
   ↓
Prediction
   |
   ↓
Explainable Output
```

## 🛠️ Technologies Used

### Programming Language

* Python

### Machine Learning

* LightGBM
* Scikit-learn
* Pandas
* NumPy

### Deep Learning (Planned/Integrated)

* BERT
* Graph Neural Networks

### Development Tools

* Git & GitHub
* Google Colab
* VS Code

## ⚙️ Installation

Clone the repository:

```bash
git clone <repository-url>
```

Navigate to the project folder:

```bash
cd PhishGuardXAI
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## ▶️ Running LightGBM Model

Train the model:

```bash
python models/lightgbm/train.py
```

The trained model will be saved as:

```
models/lightgbm/lightgbm_model.pkl
```

## 📊 Dataset

The project uses phishing URL datasets containing:

* URL information
* URL labels:

  * Good (0)
  * Bad/Phishing (1)

The dataset undergoes:

* Missing value removal
* Duplicate removal
* Label encoding
* URL feature extraction

## 🔮 Future Enhancements

* Integrate BERT-based URL/text analysis
* Implement Graph Neural Network-based detection
* Combine models using ensemble learning
* Add real-time browser extension detection
* Improve phishing recall using advanced techniques
* Add XAI explanations using SHAP/LIME

## 👥 Contributors

* PhishGuardXAI Development Team

## 📄 License

This project is developed for academic and research purposes.
