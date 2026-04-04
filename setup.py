from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="cybershield",
    version="1.0.0",
    author="CyberShield Team",
    description="Blockchain-based Distributed Intrusion Detection System with ML",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/cybershield",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Security",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "psutil>=5.9.0",
        "scikit-learn>=1.3.0",
        "numpy>=1.24.0",
        "python-dotenv>=1.0.0",
        "requests>=2.31.0",
        "rich>=13.0.0",
        "aptos-sdk>=0.11.0",
        "click>=8.1.0",
        "pyyaml>=6.0",
        "websockets>=12.0",
        "aiohttp>=3.9.0",
        "cryptography>=41.0.0",
        "tensorflow>=2.15.0",
        "keras>=3.0.0",
        "xgboost>=2.0.0",
        "lightgbm>=4.0.0",
        "pandas>=2.0.0",
        "matplotlib>=3.7.0",
        "seaborn>=0.12.0",
    ],
    entry_points={
        "console_scripts": [
            "cybershield=cybershield.cli:main",
        ],
    },
    include_package_data=True,
)
