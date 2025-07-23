"""
Setup configuration for MkDocs Free Text Questions Plugin
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="mkdocs-freetext",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A MkDocs plugin for adding interactive free text questions to documentation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/mkdocs-freetext",
    project_urls={
        "Bug Tracker": "https://github.com/your-username/mkdocs-freetext/issues",
        "Documentation": "https://your-username.github.io/mkdocs-freetext/",
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Documentation",
        "Topic :: Software Development :: Documentation",
        "Topic :: Text Processing :: Markup :: Markdown",
    ],
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={
        "mkdocs.plugins": [
            "freetext = mkdocs_freetext.plugin:FreeTextQuestionsPlugin",
        ]
    },
    include_package_data=True,
    zip_safe=False,
)
