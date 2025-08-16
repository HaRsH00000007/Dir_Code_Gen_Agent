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
