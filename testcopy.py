import json
from difflib import get_close_matches
import re
import time
import logging

logging.basicConfig(filename='chatbot.log', level=logging.DEBUG)


def clean_user_input(user_input: str) -> str:
    """Removes special characters and converts to lowercase."""
    return re.sub(r"[^\w\s]", "", user_input.lower())


def validate_knowledge_base(knowledge_base: dict) -> bool:
    """Checks if all entries have 'question' and 'answer' keys."""
    for entry in knowledge_base["question"]:
        if not all(key in entry for key in ("question", "answer")):
            return False
    return True


def load_knowledge_base(file_path: str) -> dict:
    """Loads knowledge base from JSON file and validates format."""
    with open(file_path, 'r') as file:
        data: dict = json.load(file)
        if not validate_knowledge_base(data):
            raise ValueError("Invalid knowledge base format")
        return data


def save_knowledge_base(file_path: str, data: dict):
    """Saves knowledge base to JSON file. Creates a backup before saving."""
    timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")  # Create unique timestamped filename
    backup_file = f"{file_path}.bak.{timestamp}"
    with open(backup_file, 'w') as backup:  # Create backup before saving
        json.dump(data, backup, indent=2)

    with open(file_path, 'w') as file:
        json.dump(data, file, indent=2)


def find_best_match(user_input: str, knowledge_base: dict) -> str | None:
    """Finds the best matching question from the knowledge base."""
    cleaned_input = clean_user_input(user_input)
    logging.debug(f"Cleaned user input: {cleaned_input}")

    matches = get_close_matches(cleaned_input, [q["question"] for q in knowledge_base["question"]], n=1, cutoff=0.6)
    return matches[0] if matches else None


def get_answer_for_question(question: str, knowledge_base: dict) -> str | None:
    """Retrieves the answer for a specific question from the knowledge base."""
    for q in knowledge_base["question"]:
        if q["question"] == question:
            return q["answer"]


def chat_bot():
    """Main function that runs the chatbot conversation loop."""
    try:
        knowledge_base = load_knowledge_base('knowledge_base.json')
        while True:
            user_input: str = input("You: ")

            if user_input.lower() == "quit":
                break

            best_match: str | None = find_best_match(user_input, knowledge_base)

            if best_match:
                answer: str = get_answer_for_question(best_match, knowledge_base)
                print(f"Bot: {answer}")

                # New code: Feedback mechanism
                feedback = input("Is this the expected answer? [y/n]: ")
                if feedback.lower() != 'y':
                    print("Bot: Sorry for that. What's the correct answer?")
                    new_answer: str = input('Type the answer or "skip" to skip:')
                    if new_answer.lower() != "skip":
                        knowledge_base["question"].append({"question": best_match, "answer": new_answer})
                        save_knowledge_base("knowledge_base.json", knowledge_base)
                        print("Bot: Thanks for teaching me!")

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
