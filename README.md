# Dir_Code_Gen_Agent

## 📋 Overview

### Directory Structure Agent
- **Purpose**: Suggests standardized project directory structures based on project description, tech stack, team roles, and best practices.
- **Features**:
  - AI-powered structure generation using OpenAI
  - Customizable preferences (docs, tests, Docker, CI/CD, custom folders)
  - Similarity matching with example repositories
  - JSON and tree view outputs
  - Gradio web interface

### Code Generation Agent
- **Purpose**: Generates complete project templates from directory structures, including boilerplate code and Git workflow recommendations.
- **Features**:
  - Git workflow detection (Centralized, Feature Branch, Gitflow, Forking, Trunk-based, Monorepo, Multirepo)
  - Language-specific code templates (Python, JavaScript, TypeScript, HTML, CSS, YAML, Docker, etc.)
  - Intelligent file content generation using Groq AI
  - Project analysis and complexity scoring
  - Ready-to-download project ZIPs

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- OpenAI API key (for Directory Structure Agent)
- Groq API key (for advanced code generation, optional)

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/your-repo.git
   cd your-repo

Install dependencies:
 Copypip install -r requirements.txt


Set up environment variables:
 Copycp .env.example .env
Edit .env and add your API keys:
 CopyOPENAI_API_KEY=your_openai_key
GROQ_API_KEY=your_groq_key


Run the agents:
 Copypython directory_structure_agent.py  # For Directory Structure Agent
python code_generation_agent.py      # For Code Generation Agent



🛠 Usage
Directory Structure Agent

Launch the Gradio interface:
 Copypython directory_structure_agent.py

Enter your project description, tech stack, and preferences.
Get a JSON or tree view of your project structure.

Example Input:

Project Description: "A full-stack e-commerce web application with user authentication, payment processing, and admin dashboard"
Tech Stack: "React, TypeScript, Node.js, Express, PostgreSQL, Redis"
Preferences: "include docker, tests, docs, folder: uploads, folder: logs"

Example Output:

JSON structure
Tree view
Ready-to-use project skeleton

Code Generation Agent

Launch the Gradio interface:
 Copypython code_generation_agent.py

Upload a directory structure JSON (or use the output from the Directory Structure Agent).
Enter a project name (optional).
Download the generated project as a ZIP file.

Example JSON Input:
 Copy{
  "src": {
    "components": ["Button.js", "Header.js"],
    "pages": ["Home.js", "About.js"],
    "utils": ["helpers.py", "config.py"]
  },
  "tests": ["test_main.py"],
  "docs": ["api.md"],
  "package.json": "",
  "README.md": ""
}
Example Output:

Complete project with all files and folders
Boilerplate code for each file
README.md with setup and workflow instructions
.gitignore, LICENSE, CONTRIBUTING.md
Git workflow recommendation


📂 Project Structure
 Copyyour-repo/
├── directory_structure_agent.py  # Directory Structure Agent
├── code_generation_agent.py      # Code Generation Agent
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment variables template
├── README.md                     # This file
└── examples/                     # Example JSON structures
