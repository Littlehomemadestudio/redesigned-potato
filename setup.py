#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
فایل نصب ربات شبیه‌سازی جنگ
Setup script for war simulation bot
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="war-simulation-bot",
    version="1.0.0",
    author="War Bot Developer",
    author_email="developer@example.com",
    description="ربات شبیه‌سازی جنگ پیشرفته برای بله",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/war-simulation-bot",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Communications :: Chat",
        "Topic :: Games/Entertainment",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "war-bot=war_simulation_bot:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.txt", "*.md", "*.yml", "*.yaml"],
    },
    keywords="bale bot war simulation game strategy military",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/war-simulation-bot/issues",
        "Source": "https://github.com/yourusername/war-simulation-bot",
        "Documentation": "https://github.com/yourusername/war-simulation-bot/wiki",
    },
)