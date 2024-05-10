import json
from difflib import get_close_matches
import re
import time
import logging

logging.basicConfig(filename='chatbot.log', level=logging.DEBUG)

#Cleans the user input by removing special characters
def clean_user_input(user_input: str) -> str:
    cleaned_input = re.sub(r"[^\w\s]", "", user_input.lower())  # Remove special characters
    return cleaned_input

#validates the knowledge base by checking if the question and answer keys are present in the knowledge base
def validate_knowledge_base(knowledge_base: dict) -> bool:
    for entry in knowledge_base["question"]:
        if not all(key in entry for key in ("question", "answer")):
            return False
    return True

#Loads the knowledge base JSON file
def load_knowledge_base(file_path: str) -> dict:
    with open(file_path, 'r') as file:
        data: dict = json.load(file)
        if not validate_knowledge_base(data):
            raise ValueError("Invalid knowledge base format")
        return data

#Saves the knowledge base to a JSON file. Creates a backup file before saving
def save_knowledge_base(file_path: str, data: dict):
    timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")  # Create unique timestamped filename
    backup_file = f"{file_path}.bak.{timestamp}"
    with open(backup_file, 'w') as backup:  # Create backup before saving
        json.dump(data, backup, indent=2)

    with open(file_path, 'w') as file:
        json.dump(data, file, indent=2)

#Finds the best match for the user input in the knowledge base
def find_best_match(user_input: str, knowledge_base: dict) -> str | None:
    cleaned_input = clean_user_input(user_input)
    logging.debug(f"Cleaned user input: {cleaned_input}")

    matches = get_close_matches(cleaned_input, [q["question"] for q in knowledge_base["question"]], n=1, cutoff=0.6)
    return matches[0] if matches else None

#retreives the answer for the question from the knowledge base
def get_answer_for_question(question: str, knowledge_base: dict) -> str | None:
    for q in knowledge_base["question"]:
        if q["question"] == question:
            return q["answer"]

#Chatbot main function that runs the chatbot
def chat_bot():
    try:
        knowledge_base = load_knowledge_base('knowledge_base.json')
        while True:
            user_input: str = input("You: ")

            if user_input.lower() == "quit":
                break

            best_match: str | None = find_best_match(user_input, knowledge_base)
            logging.debug(f"Best match: {best_match}")

            if best_match:
                answer: str = get_answer_for_question(best_match, knowledge_base)
                print(f"Bot: {answer}")
            else:
                print("Bot: Sorry, I don't understand the answer. Can you teach me?")
                new_answer: str = input('Type the answer or "skip" to skip:')

                if new_answer.lower() != "skip":
                    knowledge_base["question"].append({"question": user_input, "answer": new_answer})
                    save_knowledge_base("knowledge_base.json", knowledge_base)
                    print("Bot: Thanks for teaching me!")

    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    chat_bot()
