# Quick Start - Security Features

## 🚀 Get Started in 5 Minutes

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Test Phishing Detection

```bash
# Check a suspicious URL
cybershield phishing check --url "http://paypa1-login.xyz"

# See examples
cybershield phishing examples
```

### 3. Take the Quiz

```bash
# Start the awareness quiz
cybershield awareness quiz --questions 10
```

---

## 📋 Common Commands

### Phishing Detection

```bash
# Basic check
cybershield phishing check --url "http://suspicious-site.com"

# Detailed analysis
cybershield phishing check --url "http://suspicious-site.com" --verbose

# Batch check
cybershield phishing batch --file urls.txt --output results.json
```

### Awareness Training

```bash
# Full quiz
cybershield awareness quiz

# Quick quiz (10 questions)
cybershield awareness quiz --questions 10

# Easy questions only
cybershield awareness quiz --difficulty easy

# View topics
cybershield awareness topics

# Security tips
cybershield awareness tips
```

---

## 🧪 Run Tests

```bash
# Test phishing detection
python test_phishing.py

# Test awareness quiz
python test_awareness_quiz.py

# Run complete demo
python demo_security_features.py
```

---

## 💻 Python API

### Phishing Detection

```python
from cybershield.phishing.detector import PhishingDetector

detector = PhishingDetector()
result = detector.detect("http://paypa1-login.xyz")

print(f"Risk Level: {result['risk_level']}")
print(f"Risk Score: {result['risk_score']}/10")
print(f"Is Phishing: {result['is_phishing']}")
```

### Awareness Quiz

```python
from cybershield.awareness.quiz import run_quiz

# Start quiz
run_quiz(num_questions=10, difficulty="easy")
```

---

## 🌐 Frontend

The frontend now includes:
- Interactive phishing URL checker
- Quiz preview with topics
- Security-focused design

To run the frontend:

```bash
cd frontend
npm install
npm run dev
```

---

## 📚 Documentation

- **Full Documentation:** [PHISHING_AND_AWARENESS.md](PHISHING_AND_AWARENESS.md)
- **Implementation Details:** [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)
- **Main README:** [README.md](README.md)

---

## 🎯 Example Workflow

### 1. Check Email Links

```bash
# Someone sent you a suspicious link
cybershield phishing check --url "http://paypa1-secure-login.xyz/verify"

# Output shows HIGH risk - don't click!
```

### 2. Train Your Team

```bash
# Run awareness quiz for team members
cybershield awareness quiz

# They learn about phishing, passwords, malware, etc.
```

### 3. Batch Check URLs

```bash
# Create a file with URLs to check
cat > urls.txt << EOF
http://paypa1-login.xyz
https://www.paypal.com
http://amaz0n-secure.tk
https://www.amazon.com
EOF

# Check all URLs
cybershield phishing batch --file urls.txt --output results.json

# View results
cat results.json
```

---

## 🔥 Quick Tips

### Phishing Detection
- URLs with IP addresses are highly suspicious
- Check for typos in domain names (paypa1 vs paypal)
- HTTPS doesn't guarantee safety
- Excessive hyphens are a red flag

### Awareness Quiz
- Take the quiz regularly to stay sharp
- Share with team members
- Focus on weak categories
- Review explanations carefully

---

## 🆘 Troubleshooting

### Import Errors

```bash
# Make sure you're in the project directory
cd /path/to/cybershield

# Install in development mode
pip install -e .
```

### Missing Dependencies

```bash
# Install all requirements
pip install -r requirements.txt

# Or install individually
pip install tldextract python-whois rich click
```

### CLI Not Found

```bash
# Install the package
pip install -e .

# Or run directly
python -m cybershield.cli phishing check --url "http://example.com"
```

---

## 📞 Support

For help:
1. Check [PHISHING_AND_AWARENESS.md](PHISHING_AND_AWARENESS.md)
2. Run `cybershield --help`
3. Run `cybershield phishing --help`
4. Run `cybershield awareness --help`

---

**Ready to protect yourself and your team! 🛡️**
