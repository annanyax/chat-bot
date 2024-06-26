import json
from difflib import get_close_matches
import re
import time
import logging
from http.server import BaseHTTPRequestHandler, HTTPServer

logging.basicConfig(filename='chatbot.log', level=logging.DEBUG)

# Cleans the user input by removing special characters
def clean_user_input(user_input: str) -> str:
    cleaned_input = re.sub(r"[^\w\s]", "", user_input.lower())  # Remove special characters
    return cleaned_input

# Validates the knowledge base by checking if the question and answer keys are present in the knowledge base
def validate_knowledge_base(knowledge_base: dict) -> bool:
    for entry in knowledge_base["knowledge_base"]:
        if not all(key in entry for key in ("question", "answer")):
            return False
    return True

# Loads the knowledge base JSON file
def load_knowledge_base(file_path: str) -> dict:
    with open(file_path, 'r') as file:
        data: dict = json.load(file)
        if not validate_knowledge_base(data):
            raise ValueError("Invalid knowledge base format")
        return data

# Saves the knowledge base to a JSON file. Creates a backup file before saving
def save_knowledge_base(file_path: str, data: dict):
    timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")  # Create unique timestamped filename
    backup_file = f"{file_path}.bak.{timestamp}"
    with open(backup_file, 'w') as backup:  # Create backup before saving
        json.dump(data, backup, indent=2)

    with open(file_path, 'w') as file:
        json.dump(data, file, indent=2)

# Finds the best match for the user input in the knowledge base
def find_best_match(user_input: str, knowledge_base: dict) -> str | None:
    cleaned_input = clean_user_input(user_input)
    logging.debug(f"Cleaned user input: {cleaned_input}")

    all_questions = [q for entry in knowledge_base["knowledge_base"] for q in entry["question"]]
    matches = get_close_matches(cleaned_input, all_questions, n=1, cutoff=0.6)
    return matches[0] if matches else None

# Retrieves the answer for the question from the knowledge base
def get_answer_for_question(question: str, knowledge_base: dict) -> str | None:
    for entry in knowledge_base["knowledge_base"]:
        if question in entry["question"]:
            return entry["answer"]
    return None

# HTTP request handler
class ChatbotHTTPRequestHandler(BaseHTTPRequestHandler):
    def _set_response(self, content_type='text/html'):
        self.send_response(200)
        self.send_header('Content-type', content_type)
        self.end_headers()

    def do_GET(self):
        if self.path == '/':
            self._set_response()
            with open('index.html', 'rb') as file:
                self.wfile.write(file.read())

    def do_POST(self):
        if self.path == '/chat':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)
            user_input = data.get('user_input', '')

            knowledge_base = load_knowledge_base('knowledge_base.json')

            best_match = find_best_match(user_input, knowledge_base)
            logging.debug(f"Best match: {best_match}")

            if best_match:
                answer = get_answer_for_question(best_match, knowledge_base)
                response = f" {answer}"
            else:
                response = " Sorry, I don't understand the question. Can you teach me?"
                # Add teaching logic here if needed

            self._set_response('application/json')
            self.wfile.write(json.dumps({'response': response}).encode('utf-8'))

def run(server_class=HTTPServer, handler_class=ChatbotHTTPRequestHandler, port=5000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting httpd server on port {port}...')
    httpd.serve_forever()

if __name__ == "__main__":
    run()
