# Conversational App with Bujji

### Checkout the Demo: [ratlai-agent-bujji.streamlit.app](https://ratlai-agent-bujji.streamlit.app/)

This project implements a multi-agent system using LangChain, Streamlit, and OpenAI's GPT model. The main agent, Bujji, coordinates multiple sub-agents to handle various tasks like research, email sending, and API testing. The system is designed to respond to user queries and delegate tasks to appropriate sub-agents.

## Features

- **Multi-Agent Coordination**: Bujji, the main agent, coordinates tasks among various sub-agents.
- **Research Agent**: Handles queries using the Tavily API.
- **Email Agent**: Sends emails as required (optional, only if credentials.json is present).
- **API Test Agent**: Generates and executes API test code using the PythonREPLTool.
- **User Interaction**: Provides a user-friendly interface for interacting with the agents.

## Technologies Used

- **LangChain**: For building and managing the multi-agent system.
- **Streamlit**: For creating the web interface.
- **OpenAI GPT**: For natural language processing.
- **Tavily API**: For handling research queries.
- **PythonREPLTool**: For executing API test code.

## Project Structure

```
.
├── README.md
├── agent.py
├── demo
│   └── demo.mov
├── image
│   ├── ratl.png
│   └── user.png
├── main.py
├── requirements.txt
```

### `agent.py`

Contains the main logic for handling user inputs, delegating tasks to sub-agents, and processing their responses.

### `main.py`

Sets up the Streamlit interface, handles user inputs, and displays messages from agents.

### `.env`

Stores environment variables such as API keys.

### `requirements.txt`

Lists all Python dependencies required for the project.

### `images`

Contains avatars for different agents.

## Setup

### Prerequisites

- Python 3.8+
- OpenAI API Key
- Tavily API Key

### Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/ratlai/agents-demo.git
    cd agents-demo
    ```

2. Install the required dependencies:

    ```bash
    pip install -r requirements.txt
    ```

3. Set up environment variables:

    Create a `.env` file in the project root and add your API keys and other necessary credentials:

    ```env
    OPENAI_API_KEY=your_openai_api_key
    TAVILY_API_KEY=your_tavily_api_key
    USER_EMAIL=your_email
    MODEL=gpt-4o
    ```

4. (Optional) Add Gmail Credentials:

    To use the Gmail API for sending emails, follow these steps:

    1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
    2. Create a new project (or select an existing one).
    3. Enable the Gmail API for your project.
    4. Create credentials for a service account:
        - Go to the "Credentials" page.
        - Click on "Create credentials" and select "Service account".
        - Fill in the necessary details and create the service account.
        - Download the `credentials.json` file and save it in the root directory of your project.

### Running the Application

1. Start the Streamlit application:

    ```bash
    streamlit run main.py
    ```

2. Open your web browser and navigate to `http://localhost:8501`.

## Usage

1. Interact with Bujji by typing your queries into the chat input.
2. Bujji will delegate tasks to appropriate sub-agents and return their responses.
3. View responses from agents in the chat interface.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the ratl.ai.

---

**Contact**

For any questions or inquiries, please contact [Amit Kumar Das] at [amitkumardas@gofynd.com].

Enjoy interacting with Bujji and exploring the capabilities of this multi-agent system!
