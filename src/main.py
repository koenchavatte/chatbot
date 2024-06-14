import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from tqdm import tqdm
import os
import json
from flask import Flask, request, jsonify
import openai

# Create the directory if it doesn't exist
os.makedirs("erasmus-site-parsed", exist_ok=True)

# Base URL
base_url = "https://www.erasmushogeschool.be/nl/opleidingen"

# Make a request to the website
r = requests.get(base_url)
r.content

# Use the 'html.parser' to parse the page
soup = BeautifulSoup(r.content, 'html.parser')

# Find all links on page
links = soup.findAll('a')

# Filter the links
filtered_links = []
for link in links:
    href = link.get('href')
    # select the relative links to 'opleidingen'
    if href and href.startswith('/nl/opleidingen/'):
        full_url = urljoin(base_url, href)  # Join the base URL with the relative URL
        if full_url not in filtered_links:
            filtered_links.append(full_url)
    # select the absolute links 1 level deeper than 'https://www.erasmushogeschool.be/nl/'
    elif href and href.startswith('https://www.erasmushogeschool.be/nl/') and not href.startswith('https://www.erasmushogeschool.be/nl/opleidingen') and href.count('/') == 4:
        if href not in filtered_links:
            filtered_links.append(href)

# Save the links to HTML files
for link in tqdm(filtered_links):
    # Make a request to the website
    r = requests.get(link)

    # Use the 'html.parser' to parse the page
    soup = BeautifulSoup(r.content, 'html.parser')

    # Generate the file name
    file_name = link.replace('https://www.erasmushogeschool.be/nl/', '').replace('/', '_') + '.html'

    # Write the parsed content to a file
    with open(f"erasmus-site-parsed/{file_name}", "w", encoding='utf-8') as file:
        file.write(str(soup.prettify()))

# Absolute path to your chatsetup.json file
CHAT_SETUP_PATH = os.path.join(os.path.dirname(__file__), 'chatsetup.json')

# Function to load chat setup configuration
def load_chat_setup():
    with open(CHAT_SETUP_PATH, 'r', encoding='utf-8') as f:
        chat_config = json.load(f)
    
    # Extract the parameters
    system_prompt = chat_config['systemPrompt']
    chat_parameters = chat_config['chatParameters']
    
    return system_prompt, chat_parameters

# Function to initialize OpenAI API key
def initialize_openai_api():
    openai.api_key = 'your-openai-api-key'  # Replace with your actual API key

# Define the Chatbot class
class Chatbot:
    def __init__(self, system_prompt, chat_parameters):
        self.system_prompt = system_prompt
        self.chat_parameters = chat_parameters
        self.conversation_history = []

    def get_response(self, user_input):
        self.conversation_history.append({"role": "user", "content": user_input})
        
        # Prepare the messages for the API
        messages = [{"role": "system", "content": self.system_prompt}] + self.conversation_history[-self.chat_parameters['pastMessagesToInclude']:]
        
        # Call the OpenAI API using the new interface
        response = openai.Completion.create(
            engine="text-davinci-003",  # Adjust engine name as necessary
            prompt=" ".join([msg['content'] for msg in messages]),
            max_tokens=self.chat_parameters['maxResponseLength'],
            temperature=self.chat_parameters['temperature'],
            top_p=self.chat_parameters['topProbablities'],
            stop=self.chat_parameters['stopSequences']
        )
        
        # Extract and return the response
        response_message = response.choices[0].text.strip()
        self.conversation_history.append({"role": "assistant", "content": response_message})
        return response_message

# Initialize Flask app
app = Flask(__name__)

# Load chat setup configuration and initialize the chatbot
system_prompt, chat_parameters = load_chat_setup()
initialize_openai_api()  # Initialize OpenAI API key here
chatbot = Chatbot(system_prompt, chat_parameters)

# Define Flask route for chatbot interaction
@app.route('/api/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message')
    response = chatbot.get_response(user_input)
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(port=5000)
