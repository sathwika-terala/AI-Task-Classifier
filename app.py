import streamlit as st
import json
import os
from google import genai

client = genai.Client(api_key=os.environ["Gemini_API_Key"])

categories = {
    "TECHNOLOGY": ["PHONE", "LAPTOP", "COMPUTER"],
    "HOME_REPAIR": ["PLUMBING", "ELECTRICAL", "CARPENTRY"],
    "CLEANING": ["HOUSE_CLEANING", "DEEP_CLEANING"],
    "GARDENING": ["PLANTS", "LEAVES", "SOIL", "WEEDS"],
    "BEAUTY": ["FACIAL", "MAKEUP", "HAIR", "NAILS"],
    "PET_CARE": ["GROOMING"],
    "SERVICES": ["PHOTOGRAPHY"],
    "EDUCATION": ["TUTORING"],
    "EMPLOYMENT": ["JOB_SEARCH", "WORKPLACE_INFO"]
}
if os.path.exists("categories.json"):
    with open("categories.json", "r") as file:
        categories = json.load(file)
else:
    with open("categories.json", "w") as file:
        json.dump(categories, file, indent=4)

if "categories" not in st.session_state:
    st.session_state.categories = categories

categories = st.session_state.categories


def build_prompt(task):
    return f"""
    You are a task classification assistant.
    Classify the given task using ONLY these categories:
    {categories}

    Rules:
    1. Select the most relevant category and subcategory from the available categories.
    2. Do not invent categories or subcategories when an existing category matches.
    3. If no existing category matches, use UNCLASSIFIED / NONE and suggest a new category and subcategory.
    4. If an existing category matches, set suggested_category and suggested_subcategory to null.
    5. Use uppercase letters and underscores for category names.
    6. Return strict JSON with four keys:
       category, subcategory, suggested_category, suggested_subcategory.
    7. Do not include explanations outside JSON.
    8. Classify based on intent, not just keywords.
    9. Learning a skill or receiving instruction means EDUCATION / TUTORING.
    10. Technical assistance, repair, or development should use the relevant technical category.

    MULTIPLE SERVICE RULES:
    - Multiple problems within the same subcategory can receive that subcategory.
    - Multiple distinct services or subcategories mean UNCLASSIFIED / NONE.
    - Any service outside the taxonomy means UNCLASSIFIED / NONE.
    - Evaluate every part of the request.

    Examples:
    "Remove weeds and plant flowers" -> UNCLASSIFIED / NONE.
    "Dog grooming and treatment for a skin problem" -> UNCLASSIFIED / NONE.
    "Fix my phone screen and battery" -> TECHNOLOGY / PHONE.

    Task: {task}
    """

def classify(prompt):
    interaction = client.interactions.create(
        model="gemini-3.1-flash-lite",
        input=prompt
    )
    return interaction.output_text

def process_response(response_text):
    response_text = response_text.replace("```json", "")
    response_text = response_text.replace("```", "")
    return response_text.strip()

def predict_task(task):
    prompt = build_prompt(task)
    response_text = classify(prompt)
    return json.loads(process_response(response_text))

st.title("AI Task Classifier")
st.write("Enter a task below to identify its category and subcategory.")

if "prediction" not in st.session_state:
    st.session_state.prediction = None

if "approval_message" not in st.session_state:
    st.session_state.approval_message = None

with st.form("task_form"):
    task = st.text_input("What do you need help with?")
    submitted = st.form_submit_button("Classify Task")

if submitted:
    if task:
        try:
            with st.spinner("Classifying your task..."):
                st.session_state.prediction = predict_task(task)
            st.session_state.approval_message = None
        except Exception as e:
            st.error(f"Something went wrong: {e}")
    else:
        st.warning("Please enter a task.")
prediction = st.session_state.prediction

if prediction:
    st.write("**Category:**", prediction["category"])
    st.write("**Subcategory:**", prediction["subcategory"])

    if prediction["category"] == "UNCLASSIFIED":
        suggested_category = prediction["suggested_category"]
        suggested_subcategory = prediction["suggested_subcategory"]

        st.write("**Suggested Category:**", suggested_category)
        st.write("**Suggested Subcategory:**", suggested_subcategory)

        st.write("Would you like to approve this suggestion?")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Approve", key="approve"):
                if suggested_category and suggested_subcategory:
                    categories.setdefault(suggested_category, [])

                    if suggested_subcategory not in categories[suggested_category]:
                        categories[suggested_category].append(suggested_subcategory)
                    with open("categories.json", "w") as file:
                        json.dump(categories, file, indent=4)
                    st.session_state.approval_message = "Suggestion approved and added!"
                else:
                    st.session_state.approval_message = "Invalid suggestion."

                st.session_state.prediction = None
                st.rerun()

        with col2:
            if st.button("Reject", key="reject"):
                st.session_state.approval_message = "Suggestion rejected."
                st.session_state.prediction = None
                st.rerun()

if st.session_state.approval_message:
    st.info(st.session_state.approval_message)
