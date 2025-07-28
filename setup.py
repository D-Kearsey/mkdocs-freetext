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
    version="1.2.0",
    author="Drew Kearsey",
    author_email="drew.kearsey@kubrickgroup.com",
    description="A comprehensive MkDocs plugin for adding interactive free-text questions and assessments",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/D-Kearsey/mkdocs-freetext",
    project_urls={
        "Bug Tracker": "https://github.com/D-Kearsey/mkdocs-freetext/issues",
        "Documentation": "https://github.com/D-Kearsey/mkdocs-freetext",
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
