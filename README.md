# AI Task Classifier

An AI-powered task classification application built using Python, Google Gemini API, and Streamlit.

## Project Overview

This application accepts tasks written in natural language and classifies them into predefined categories and subcategories using a Gemini language model.

If a task does not match the existing taxonomy, the application suggests a new category and subcategory. Users can approve or reject these suggestions through a human-in-the-loop workflow.

## Features

- Natural language task classification
- Category and subcategory identification
- AI-generated suggestions for unclassified tasks
- Human approval and rejection workflow
- Dynamic category and subcategory updates
- JSON-based taxonomy persistence
- Interactive Streamlit interface
- Enter-to-submit functionality

## Technologies Used

- Python
- Google Gemini API
- Streamlit
- JSON

## Project Structure

```text
AI-Task-Classifier/
│
├── app.py
├── categories.json
├── classifier.py
├── requirements.txt
├── README.md
└── .gitignore
