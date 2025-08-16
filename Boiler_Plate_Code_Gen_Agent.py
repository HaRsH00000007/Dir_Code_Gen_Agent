#!/usr/bin/env python3
"""
Code Generation Agent
====================
An intelligent code scaffolding generator that analyzes directory structures
and creates appropriate project templates with Git workflow recommendations.

Author: AI Assistant
License: MIT
"""

import json
import os
import zipfile
import tempfile
import shutil
import re
import argparse
from typing import Dict, List, Tuple, Any
from pathlib import Path
from datetime import datetime
import gradio as gr
#from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class GitWorkflowDetector:
    """
    Analyzes project structure to recommend appropriate Git workflows.
    """
    
    def __init__(self):
        self.workflows = {
            'centralized': 'Centralized Workflow',
            'feature_branch': 'Feature Branch Workflow', 
            'gitflow': 'Gitflow Workflow',
            'forking': 'Forking Workflow',
            'trunk_based': 'Trunk Based Development',
            'monorepo': 'Monorepo Management',
            'multirepo': 'Multirepo Management'
        }
    
    def analyze_structure(self, directory_json: Dict) -> Tuple[str, str, Dict]:
        """
        Analyze directory structure and recommend Git workflow.
        
        Args:
            directory_json: JSON structure of the project
            
        Returns:
            Tuple of (workflow_key, workflow_name, analysis_details)
        """
        analysis = {
            'total_files': 0,
            'directories': 0,
            'languages': set(),
            'has_microservices': False,
            'has_multiple_apps': False,
            'complexity_score': 0,
            'project_indicators': []
        }
        
        # Recursively analyze structure
        self._analyze_recursive(directory_json, analysis)
        
        # Convert set to list for JSON serialization
        analysis['languages'] = list(analysis['languages'])
        
        # Determine workflow based on analysis
        workflow_key = self._determine_workflow(analysis)
        
        return workflow_key, self.workflows[workflow_key], analysis
    
    def _analyze_recursive(self, structure: Dict, analysis: Dict, depth: int = 0):
        """Recursively analyze directory structure."""
        if isinstance(structure, dict):
            for key, value in structure.items():
                if isinstance(value, dict):
                    analysis['directories'] += 1
                    
                    # Check for microservices indicators
                    if any(indicator in key.lower() for indicator in 
                          ['service', 'microservice', 'api', 'backend', 'frontend']):
                        analysis['has_microservices'] = True
                        analysis['project_indicators'].append(f"Microservice: {key}")
                    
                    # Check for multiple apps
                    if any(indicator in key.lower() for indicator in 
                          ['app', 'application', 'module', 'package']):
                        analysis['has_multiple_apps'] = True
                        analysis['project_indicators'].append(f"Application: {key}")
                    
                    self._analyze_recursive(value, analysis, depth + 1)
                    
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, str):
                            analysis['total_files'] += 1
                            self._analyze_file(item, analysis)
                        elif isinstance(item, dict):
                            self._analyze_recursive(item, analysis, depth + 1)
        
        # Calculate complexity score
        analysis['complexity_score'] = (
            analysis['total_files'] * 0.1 +
            analysis['directories'] * 0.5 +
            len(analysis['languages']) * 2 +
            (10 if analysis['has_microservices'] else 0) +
            (5 if analysis['has_multiple_apps'] else 0)
        )
    
    def _analyze_file(self, filename: str, analysis: Dict):
        """Analyze individual file and update analysis."""
        ext = Path(filename).suffix.lower()
        
        # Language detection
        language_map = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.java': 'Java',
            '.cpp': 'C++',
            '.c': 'C',
            '.go': 'Go',
            '.rs': 'Rust',
            '.php': 'PHP',
            '.rb': 'Ruby',
            '.cs': 'C#',
            '.html': 'HTML',
            '.css': 'CSS',
            '.scss': 'SCSS',
            '.vue': 'Vue',
            '.jsx': 'React',
            '.tsx': 'React/TypeScript'
        }
        
        if ext in language_map:
            analysis['languages'].add(language_map[ext])
        
        # Special file indicators
        special_files = {
            'docker-compose.yml': 'Docker Compose',
            'dockerfile': 'Docker',
            'kubernetes': 'Kubernetes',
            'package.json': 'Node.js',
            'requirements.txt': 'Python',
            'pom.xml': 'Maven',
            'build.gradle': 'Gradle'
        }
        
        filename_lower = filename.lower()
        for special, tech in special_files.items():
            if special in filename_lower:
                analysis['project_indicators'].append(f"Technology: {tech}")
    
    def _determine_workflow(self, analysis: Dict) -> str:
        """Determine the most appropriate Git workflow."""
        complexity = analysis['complexity_score']
        has_microservices = analysis['has_microservices']
        has_multiple_apps = analysis['has_multiple_apps']
        file_count = analysis['total_files']
        
        # Decision logic
        if has_microservices and complexity > 20:
            return 'monorepo' if file_count > 50 else 'multirepo'
        elif complexity > 30:
            return 'gitflow'
        elif has_multiple_apps or complexity > 15:
            return 'feature_branch'
        elif any('open' in indicator.lower() for indicator in analysis['project_indicators']):
            return 'forking'
        elif complexity < 5:
            return 'centralized'
        else:
            return 'trunk_based'


class CodeTemplateGenerator:
    """
    Generates code templates and scaffolding for different file types.
    """
    
    def __init__(self):
        self.templates = self._initialize_templates()
        # Initialize Groq client
        self.groq_client = Groq(api_key=os.getenv('GROQ_API_KEY'))
    
    def _initialize_templates(self) -> Dict[str, str]:
        """Initialize code templates for different file types."""
        return {
            '.py': self._python_template,
            '.js': self._javascript_template,
            '.ts': self._typescript_template,
            '.html': self._html_template,
            '.css': self._css_template,
            '.md': self._markdown_template,
            '.json': self._json_template,
            '.yml': self._yaml_template,
            '.yaml': self._yaml_template,
            '.dockerfile': self._dockerfile_template,
            '.gitignore': self._gitignore_template,
            'requirements.txt': self._requirements_template,
            'package.json': self._package_json_template
        }
    
    def generate_file_content(self, filename: str, file_path: str = "", project_context: Dict = None) -> str:
        """
        Generate appropriate content for a file based on its type and context.
        
        Args:
            filename: Name of the file
            file_path: Full path of the file in project
            project_context: Context about the project
            
        Returns:
            Generated file content
        """
        ext = Path(filename).suffix.lower()
        filename_lower = filename.lower()
        
        # Special handling for specific filenames
        if filename_lower == 'readme.md':
            return self._generate_readme(project_context or {})
        elif filename_lower == 'requirements.txt':
            return self._requirements_template(project_context or {})
        elif filename_lower == 'package.json':
            return self._package_json_template(project_context or {})
        elif 'dockerfile' in filename_lower:
            return self._dockerfile_template(project_context or {})
        elif filename_lower == '.gitignore':
            return self._gitignore_template(project_context or {})
        
        # Use extension-based templates
        if ext in self.templates:
            template_func = self.templates[ext]
            if callable(template_func):
                return template_func(filename, file_path, project_context or {})
            else:
                return template_func
        
        # Use Groq for intelligent code generation
        return self._generate_with_groq(filename, file_path, project_context or {})
    
    def _generate_with_groq(self, filename: str, file_path: str, context: Dict) -> str:
        """Generate code using Groq LLM for unknown file types."""
        try:
            ext = Path(filename).suffix.lower()
            
            prompt = f"""
            Generate appropriate code content for a file named '{filename}' with extension '{ext}'.
            File path in project: {file_path}
            Project context: {json.dumps(context, indent=2)}
            
            Please provide:
            1. Appropriate boilerplate code for this file type
            2. Meaningful comments and documentation
            3. Best practices for the language/framework
            4. Template structure that can be easily extended
            
            Return only the code content, no explanations.
            """
            
            response = self.groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are an expert code generator. Generate clean, well-documented boilerplate code."},
                    {"role": "user", "content": prompt}
                ],
                model="mixtral-8x7b-32768",
                temperature=0.3,
                max_tokens=2000
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            # Fallback to basic template
            return f"""# {filename}
# Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# TODO: Implement functionality for {filename}

# Error generating with Groq: {str(e)}
# Please implement the required functionality here.
"""
    
    def _python_template(self, filename: str, file_path: str, context: Dict) -> str:
        """Generate Python file template."""
        module_name = Path(filename).stem
        
        return f'''#!/usr/bin/env python3
"""
{module_name.replace('_', ' ').title()} Module
{'-' * (len(module_name) + 7)}

This module provides functionality for {module_name.replace('_', ' ')}.

Author: Generated by Code Generation Agent
Date: {datetime.now().strftime('%Y-%m-%d')}
"""

import logging
from typing import Any, Dict, List, Optional, Union

# Configure logging
logger = logging.getLogger(__name__)


class {module_name.replace('_', '').title()}:
    """
    Main class for {module_name.replace('_', ' ')} functionality.
    """
    
    def __init__(self):
        """Initialize the {module_name.replace('_', ' ')} instance."""
        logger.info(f"Initializing {module_name.replace('_', ' ')}")
        self._initialized = True
    
    def process(self, data: Any) -> Any:
        """
        Process the input data.
        
        Args:
            data: Input data to process
            
        Returns:
            Processed data
            
        Raises:
            ValueError: If data is invalid
        """
        if not self._initialized:
            raise RuntimeError("Instance not properly initialized")
        
        # TODO: Implement processing logic
        logger.info("Processing data")
        return data


def main():
    """Main function for standalone execution."""
    # TODO: Implement main functionality
    print(f"Running {module_name.replace('_', ' ')}")


if __name__ == "__main__":
    main()
'''
    
    def _javascript_template(self, filename: str, file_path: str, context: Dict) -> str:
        """Generate JavaScript file template."""
        module_name = Path(filename).stem
        
        return f'''/**
 * {module_name.replace('_', ' ').title()} Module
 * {'-' * (len(module_name) + 7)}
 * 
 * This module provides functionality for {module_name.replace('_', ' ')}.
 * 
 * @author Generated by Code Generation Agent
 * @date {datetime.now().strftime('%Y-%m-%d')}
 */

'use strict';

/**
 * Main class for {module_name.replace('_', ' ')} functionality.
 */
class {module_name.replace('_', '').title()} {{
    /**
     * Initialize the {module_name.replace('_', ' ')} instance.
     */
    constructor() {{
        this.initialized = true;
        console.log(`Initializing ${{'{module_name.replace('_', ' ')}'}}`);</small>
    }}
    
    /**
     * Process the input data.
     * @param {{any}} data - Input data to process
     * @returns {{any}} Processed data
     * @throws {{Error}} If data is invalid
     */
    process(data) {{
        if (!this.initialized) {{
            throw new Error('Instance not properly initialized');
        }}
        
        // TODO: Implement processing logic
        console.log('Processing data');
        return data;
    }}
}}

/**
 * Main function for standalone execution.
 */
function main() {{
    // TODO: Implement main functionality
    console.log('Running {module_name.replace('_', ' ')}');
}}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {{
    module.exports = {module_name.replace('_', '').title()};
}}

// Run main if this is the entry point
if (require.main === module) {{
    main();
}}
'''
    
    def _typescript_template(self, filename: str, file_path: str, context: Dict) -> str:
        """Generate TypeScript file template."""
        module_name = Path(filename).stem
        class_name = module_name.replace('_', '').title()
        
        return f'''/**
 * {module_name.replace('_', ' ').title()} Module
 * {'-' * (len(module_name) + 7)}
 * 
 * This module provides functionality for {module_name.replace('_', ' ')}.
 * 
 * @author Generated by Code Generation Agent
 * @date {datetime.now().strftime('%Y-%m-%d')}
 */

/**
 * Interface for {module_name.replace('_', ' ')} configuration.
 */
interface {class_name}Config {{
    enabled: boolean;
    options?: Record<string, any>;
}}

/**
 * Interface for {module_name.replace('_', ' ')} data.
 */
interface {class_name}Data {{
    id: string;
    value: any;
    timestamp: Date;
}}

/**
 * Main class for {module_name.replace('_', ' ')} functionality.
 */
export class {class_name} {{
    private initialized: boolean = false;
    private config: {class_name}Config;
    
    /**
     * Initialize the {module_name.replace('_', ' ')} instance.
     * @param config Configuration options
     */
    constructor(config: {class_name}Config = {{ enabled: true }}) {{
        this.config = config;
        this.initialized = true;
        console.log(`Initializing ${{'{module_name.replace('_', ' ')}'}}`);</small>
    }}
    
    /**
     * Process the input data.
     * @param data Input data to process
     * @returns Processed data
     * @throws Error if data is invalid
     */
    public process(data: {class_name}Data): {class_name}Data {{
        if (!this.initialized) {{
            throw new Error('Instance not properly initialized');
        }}
        
        // TODO: Implement processing logic
        console.log('Processing data');
        return data;
    }}
    
    /**
     * Get current configuration.
     * @returns Current configuration
     */
    public getConfig(): {class_name}Config {{
        return {{ ...this.config }};
    }}
}}

/**
 * Main function for standalone execution.
 */
function main(): void {{
    // TODO: Implement main functionality
    console.log('Running {module_name.replace('_', ' ')}');
}}

// Run main if this is the entry point
if (require.main === module) {{
    main();
}}

export default {class_name};
'''
    
    def _html_template(self, filename: str, file_path: str, context: Dict) -> str:
        """Generate HTML file template."""
        title = Path(filename).stem.replace('_', ' ').replace('-', ' ').title()
        
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{title} - Generated by Code Generation Agent">
    <meta name="author" content="Code Generation Agent">
    <title>{title}</title>
    
    <!-- Styles -->
    <link rel="stylesheet" href="styles.css">
    
    <!-- Favicon -->
    <link rel="icon" type="image/x-icon" href="favicon.ico">
</head>
<body>
    <header>
        <nav>
            <h1>{title}</h1>
            <!-- Navigation items -->
        </nav>
    </header>
    
    <main>
        <section class="hero">
            <h2>Welcome to {title}</h2>
            <p>This is a generated HTML template. Customize it according to your needs.</p>
        </section>
        
        <section class="content">
            <!-- Main content goes here -->
            <div class="container">
                <p>TODO: Add your content here</p>
            </div>
        </section>
    </main>
    
    <footer>
        <p>&copy; {datetime.now().year} {title}. Generated by Code Generation Agent.</p>
    </footer>
    
    <!-- Scripts -->
    <script src="script.js"></script>
</body>
</html>
'''
    
    def _css_template(self, filename: str, file_path: str, context: Dict) -> str:
        """Generate CSS file template."""
        return f'''/*
 * {Path(filename).stem.replace('_', ' ').title()} Stylesheet
 * Generated by Code Generation Agent
 * Date: {datetime.now().strftime('%Y-%m-%d')}
 */

/* Reset and Base Styles */
* {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}

html {{
    font-size: 16px;
    scroll-behavior: smooth;
}}

body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
    line-height: 1.6;
    color: #333;
    background-color: #fff;
}}

/* Layout */
.container {{
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
}}

/* Header */
header {{
    background-color: #f8f9fa;
    padding: 1rem 0;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}}

nav h1 {{
    color: #2c3e50;
    font-size: 2rem;
    font-weight: 600;
}}

/* Main Content */
main {{
    min-height: calc(100vh - 120px);
    padding: 2rem 0;
}}

.hero {{
    text-align: center;
    padding: 3rem 0;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    margin-bottom: 2rem;
}}

.hero h2 {{
    font-size: 2.5rem;
    margin-bottom: 1rem;
}}

.content {{
    padding: 2rem 0;
}}

/* Footer */
footer {{
    background-color: #2c3e50;
    color: white;
    text-align: center;
    padding: 1rem 0;
    margin-top: auto;
}}

/* Utilities */
.text-center {{ text-align: center; }}
.mt-1 {{ margin-top: 0.25rem; }}
.mt-2 {{ margin-top: 0.5rem; }}
.mt-3 {{ margin-top: 1rem; }}
.mb-1 {{ margin-bottom: 0.25rem; }}
.mb-2 {{ margin-bottom: 0.5rem; }}
.mb-3 {{ margin-bottom: 1rem; }}

/* Responsive Design */
@media (max-width: 768px) {{
    .container {{
        padding: 0 15px;
    }}
    
    .hero h2 {{
        font-size: 2rem;
    }}
    
    nav h1 {{
        font-size: 1.5rem;
    }}
}}

/* TODO: Add your custom styles here */
'''
    
    def _markdown_template(self, filename: str, file_path: str, context: Dict) -> str:
        """Generate Markdown file template."""
        title = Path(filename).stem.replace('_', ' ').replace('-', ' ').title()
        
        return f'''# {title}

Generated by Code Generation Agent on {datetime.now().strftime('%Y-%m-%d')}

## Overview

This document provides information about {title.lower()}.

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [Features](#features)
- [Contributing](#contributing)
- [License](#license)

## Installation

```bash
# TODO: Add installation instructions
npm install
# or
pip install -r requirements.txt
```

## Usage

```bash
# TODO: Add usage examples
python main.py
# or
npm start
```

## Features

- [ ] Feature 1
- [ ] Feature 2
- [ ] Feature 3

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

*Generated by Code Generation Agent*
'''
    
    def _json_template(self, filename: str, file_path: str, context: Dict) -> str:
        """Generate JSON file template."""
        filename_lower = filename.lower()
        
        if 'package.json' in filename_lower:
            return self._package_json_template(context)
        elif 'tsconfig' in filename_lower:
            return '''{{
  "compilerOptions": {{
    "target": "ES2020",
    "module": "commonjs",
    "lib": ["ES2020"],
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true
  }},
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}}'''
        else:
            return f'''{{
  "name": "{Path(filename).stem}",
  "version": "1.0.0",
  "description": "Generated configuration file",
  "generated": "{datetime.now().isoformat()}",
  "config": {{
    "TODO": "Add your configuration here"
  }}
}}'''
    
    def _yaml_template(self, filename: str, file_path: str, context: Dict) -> str:
        """Generate YAML file template."""
        filename_lower = filename.lower()
        
        if 'docker-compose' in filename_lower:
            return '''version: '3.8'

services:
  app:
    build: .
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
    volumes:
      - .:/app
      - /app/node_modules
    depends_on:
      - db
  
  db:
    image: postgres:13
    environment:
      POSTGRES_DB: myapp
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
'''
        elif 'github' in file_path or 'workflow' in filename_lower:
            return f'''name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup
      run: |
        # TODO: Add setup commands
        echo "Setting up environment"
    
    - name: Run Tests
      run: |
        # TODO: Add test commands
        echo "Running tests"
    
    - name: Build
      run: |
        # TODO: Add build commands
        echo "Building application"
'''
        else:
            return f'''# {Path(filename).stem.replace('_', ' ').title()} Configuration
# Generated on {datetime.now().strftime('%Y-%m-%d')}

config:
  name: "{Path(filename).stem}"
  version: "1.0.0"
  
  # TODO: Add your configuration here
  settings:
    debug: false
    port: 3000
    
  # TODO: Add environment-specific settings
  environments:
    development:
      debug: true
    production:
      debug: false
'''
    
    def _dockerfile_template(self, context: Dict) -> str:
        """Generate Dockerfile template."""
        languages = context.get('languages', [])
        
        if 'Python' in languages:
            return '''# Use Python base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Create non-root user
RUN useradd --create-home --shell /bin/bash app && chown -R app:app /app
USER app

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \\
  CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["python", "main.py"]
'''
        elif 'JavaScript' in languages or 'Node.js' in str(context.get('project_indicators', [])):
            return '''# Use Node.js base image
FROM node:16-alpine

# Set working directory
WORKDIR /app

# Copy package files first (for better caching)
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy application code
COPY . .

# Expose port
EXPOSE 3000

# Create non-root user
RUN addgroup -g 1001 -S nodejs && adduser -S nextjs -u 1001
USER nextjs

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \\
  CMD curl -f http://localhost:3000/health || exit 1

# Run application
CMD ["npm", "start"]
'''
        else:
            return '''# Multi-stage build template
FROM alpine:latest as builder

# Install build dependencies
RUN apk add --no-cache build-base

# Set working directory
WORKDIR /app

# Copy source code
COPY . .

# Build application
RUN echo "TODO: Add build commands"

# Production stage
FROM alpine:latest

# Install runtime dependencies
RUN apk add --no-cache ca-certificates

# Set working directory
WORKDIR /app

# Copy built application from builder stage
COPY --from=builder /app/dist ./

# Create non-root user
RUN adduser -D -s /bin/sh appuser
USER appuser

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \\
  CMD wget --no-verbose --tries=1 --spider http://localhost:8080/health || exit 1

# Run application
CMD ["./app"]
'''
    
    def _gitignore_template(self, context: Dict) -> str:
        """Generate .gitignore template."""
        languages = context.get('languages', [])
        
        gitignore_content = '''# Generated .gitignore
# Code Generation Agent

# IDE and Editor files
.vscode/
.idea/
*.swp
*.swo
*~

# OS generated files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Logs
logs
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Environment variables
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# Temporary files
tmp/
temp/
'''
        
        if 'Python' in languages:
            gitignore_content += '''
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST
.pytest_cache/
.coverage
htmlcov/
.tox/
.nox/
.coverage
.pytest_cache/
.mypy_cache/
.dmypy.json
dmypy.json
.pyre/
'''
        
        if 'JavaScript' in languages or 'Node.js' in str(context.get('project_indicators', [])):
            gitignore_content += '''
# Node.js
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.npm
.eslintcache
.yarn-integrity
.next
.nuxt
dist
.cache
.parcel-cache
'''
        
        if 'Java' in languages:
            gitignore_content += '''
# Java
*.class
*.jar
*.war
*.ear
*.zip
*.tar.gz
*.rar
target/
.mvn/
mvnw
mvnw.cmd
.gradle/
build/
'''
        
        return gitignore_content
    
    def _requirements_template(self, context: Dict) -> str:
        """Generate requirements.txt template."""
        base_requirements = [
            "# Generated requirements.txt",
            "# Code Generation Agent",
            "",
            "# Core dependencies",
            "requests>=2.25.1",
            "python-dotenv>=0.19.0",
            ""
        ]
        
        # Add context-specific requirements
        if 'Flask' in str(context) or 'flask' in str(context).lower():
            base_requirements.extend([
                "# Flask web framework",
                "Flask>=2.0.0",
                "Flask-CORS>=3.0.10",
                ""
            ])
        
        if 'Django' in str(context) or 'django' in str(context).lower():
            base_requirements.extend([
                "# Django web framework",
                "Django>=4.0.0",
                "djangorestframework>=3.14.0",
                ""
            ])
        
        if 'FastAPI' in str(context) or 'fastapi' in str(context).lower():
            base_requirements.extend([
                "# FastAPI framework",
                "fastapi>=0.70.0",
                "uvicorn>=0.15.0",
                ""
            ])
        
        if 'data' in str(context).lower() or 'analysis' in str(context).lower():
            base_requirements.extend([
                "# Data analysis",
                "pandas>=1.3.0",
                "numpy>=1.21.0",
                "matplotlib>=3.4.0",
                ""
            ])
        
        if 'ml' in str(context).lower() or 'machine' in str(context).lower():
            base_requirements.extend([
                "# Machine Learning",
                "scikit-learn>=1.0.0",
                "tensorflow>=2.7.0",
                ""
            ])
        
        base_requirements.extend([
            "# Development dependencies",
            "pytest>=6.2.0",
            "black>=21.9.0",
            "flake8>=4.0.0",
            "mypy>=0.910",
            "",
            "# TODO: Add your specific dependencies here"
        ])
        
        return "\n".join(base_requirements)
    
    def _package_json_template(self, context: Dict) -> str:
        """Generate package.json template."""
        project_name = context.get('project_name', 'generated-project')
        
        package_json = {
            "name": project_name.lower().replace(' ', '-'),
            "version": "1.0.0",
            "description": f"Generated project: {project_name}",
            "main": "index.js",
            "scripts": {
                "start": "node index.js",
                "dev": "nodemon index.js",
                "test": "jest",
                "build": "webpack --mode production",
                "lint": "eslint .",
                "format": "prettier --write ."
            },
            "keywords": ["generated", "project"],
            "author": "Code Generation Agent",
            "license": "MIT",
            "dependencies": {
                "express": "^4.18.0",
                "dotenv": "^16.0.0"
            },
            "devDependencies": {
                "nodemon": "^2.0.0",
                "jest": "^28.0.0",
                "eslint": "^8.0.0",
                "prettier": "^2.7.0",
                "webpack": "^5.0.0",
                "webpack-cli": "^4.0.0"
            },
            "engines": {
                "node": ">=14.0.0",
                "npm": ">=6.0.0"
            }
        }
        
        # Add React dependencies if detected
        if 'React' in context.get('languages', []):
            package_json["dependencies"].update({
                "react": "^18.2.0",
                "react-dom": "^18.2.0"
            })
            package_json["devDependencies"].update({
                "@babel/core": "^7.18.0",
                "@babel/preset-react": "^7.18.0",
                "babel-loader": "^8.2.0"
            })
        
        # Add TypeScript dependencies if detected
        if 'TypeScript' in context.get('languages', []):
            package_json["devDependencies"].update({
                "typescript": "^4.7.0",
                "@types/node": "^18.0.0",
                "ts-node": "^10.8.0"
            })
            package_json["scripts"]["build"] = "tsc"
            package_json["scripts"]["start"] = "ts-node index.ts"
        
        return json.dumps(package_json, indent=2)
    
    def _generate_readme(self, context: Dict) -> str:
        """Generate comprehensive README.md."""
        project_name = context.get('project_name', 'Generated Project')
        workflow = context.get('workflow', 'Feature Branch Workflow')
        languages = context.get('languages', [])
        
        readme_content = f'''# {project_name}

[![Generated](https://img.shields.io/badge/Generated%20by-Code%20Generation%20Agent-blue.svg)](https://github.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*

## 📋 Overview

{project_name} is an automatically generated project with proper structure and best practices. This project follows the **{workflow}** Git workflow for optimal development collaboration.

## 🛠 Technologies

'''
        
        if languages:
            readme_content += "**Languages & Frameworks:**\n"
            for lang in languages:
                readme_content += f"- {lang}\n"
            readme_content += "\n"
        
        readme_content += f'''## 📁 Project Structure

```
{project_name.lower().replace(' ', '-')}/
├── src/                 # Source code
├── tests/              # Test files
├── docs/               # Documentation
├── config/             # Configuration files
├── scripts/            # Build and utility scripts
├── .github/            # GitHub workflows
├── README.md           # Project documentation
├── .gitignore          # Git ignore rules
└── LICENSE             # License file
```

## 🚀 Quick Start

### Prerequisites

'''
        
        if 'Python' in languages:
            readme_content += """- Python 3.8 or higher
- pip package manager

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd """ + project_name.lower().replace(' ', '-') + """

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\\Scripts\\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Application

```bash
# Development mode
python main.py

# Run tests
pytest

# Format code
black .

# Lint code
flake8 .
```
"""
        
        if 'JavaScript' in languages or 'Node.js' in str(context.get('project_indicators', [])):
            readme_content += """- Node.js 14 or higher
- npm or yarn package manager

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd """ + project_name.lower().replace(' ', '-') + """

# Install dependencies
npm install
# or
yarn install
```

### Running the Application

```bash
# Development mode
npm run dev

# Production mode
npm start

# Run tests
npm test

# Build for production
npm run build

# Lint code
npm run lint
```
"""
        
        readme_content += f'''
## 🔄 Git Workflow: {workflow}

This project uses the **{workflow}** approach:

'''
        
        # Add workflow-specific instructions
        workflow_instructions = {
            'Centralized Workflow': '''- All developers work on the main branch
- Simple workflow suitable for small teams
- Commands:
  ```bash
  git pull origin main
  # Make changes
  git add .
  git commit -m "Your changes"
  git push origin main
  ```''',
            
            'Feature Branch Workflow': '''- Create feature branches for new development
- Merge back to main via pull requests
- Commands:
  ```bash
  git checkout -b feature/new-feature
  # Make changes
  git add .
  git commit -m "Add new feature"
  git push origin feature/new-feature
  # Create pull request
  ```''',
            
            'Gitflow Workflow': '''- Uses main, develop, feature, release, and hotfix branches
- Structured workflow for release management
- Commands:
  ```bash
  git flow init
  git flow feature start new-feature
  # Make changes
  git flow feature finish new-feature
  ```''',
            
            'Forking Workflow': '''- Each developer works on their own fork
- Suitable for open source projects
- Commands:
  ```bash
  # Fork the repository on GitHub
  git clone <your-fork-url>
  git remote add upstream <original-repo-url>
  # Make changes and push to your fork
  # Create pull request to original repository
  ```''',
            
            'Trunk Based Development': '''- Short-lived branches merged frequently to trunk
- Emphasizes continuous integration
- Commands:
  ```bash
  git checkout -b short-lived-branch
  # Make small changes
  git add .
  git commit -m "Small change"
  git push origin short-lived-branch
  # Quick merge to main
  ```''',
            
            'Monorepo Management': '''- Single repository containing multiple projects
- Shared tooling and dependencies
- Use tools like Lerna, Nx, or Rush for management''',
            
            'Multirepo Management': '''- Multiple repositories for different services
- Independent versioning and deployment
- Coordinate releases across repositories'''
        }
        
        readme_content += workflow_instructions.get(workflow, '- Follow standard Git practices')
        
        readme_content += '''

## 🧪 Testing

```bash
# Run all tests
npm test
# or
pytest

# Run with coverage
npm run test:coverage
# or
pytest --cov

# Run specific test file
npm test -- --testPathPattern=specific-test
# or
pytest tests/specific_test.py
```

## 📖 Documentation

- [API Documentation](docs/api.md)
- [Development Guide](docs/development.md)
- [Deployment Guide](docs/deployment.md)
- [Contributing Guidelines](CONTRIBUTING.md)

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## 🔧 Configuration

Copy `.env.example` to `.env` and configure your environment variables:

```env
# Database
DATABASE_URL=your_database_url

# API Keys
API_KEY=your_api_key

# Environment
NODE_ENV=development
```

## 📦 Deployment

### Docker

```bash
# Build image
docker build -t ''' + project_name.lower().replace(' ', '-') + ''' .

# Run container
docker run -p 3000:3000 ''' + project_name.lower().replace(' ', '-') + '''
```

### Using Docker Compose

```bash
docker-compose up -d
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Generated by Code Generation Agent
- Built with modern best practices
- Follows industry standards

## 📞 Support

If you have any questions or need help, please:

1. Check the [documentation](docs/)
2. Search existing [issues](../../issues)
3. Create a new [issue](../../issues/new)

---

*This README was automatically generated. Please update it with your specific project details.*
'''
        
        return readme_content


class ProjectGenerator:
    """
    Main class that orchestrates the project generation process.
    """
    
    def __init__(self):
        self.workflow_detector = GitWorkflowDetector()
        self.template_generator = CodeTemplateGenerator()
    
    def generate_project(self, directory_json: Dict, project_name: str = None) -> str:
        """
        Generate complete project from directory JSON.
        
        Args:
            directory_json: JSON structure of the project
            project_name: Optional project name
            
        Returns:
            Path to the generated zip file
        """
        # Validate input
        if not directory_json:
            raise ValueError("Directory JSON cannot be empty")
        
        # Analyze structure and determine workflow
        workflow_key, workflow_name, analysis = self.workflow_detector.analyze_structure(directory_json)
        
        # Create temporary directory for project generation
        temp_dir = tempfile.mkdtemp(prefix="generated_project_")
        project_dir = os.path.join(temp_dir, project_name or "generated_project")
        
        try:
            # Create project structure
            os.makedirs(project_dir, exist_ok=True)
            
            # Generate project context
            project_context = {
                'project_name': project_name or "Generated Project",
                'workflow': workflow_name,
                'workflow_key': workflow_key,
                'languages': analysis['languages'],
                'project_indicators': analysis['project_indicators'],
                'analysis': analysis
            }
            
            # Recursively create files and directories
            self._create_structure_recursive(directory_json, project_dir, project_context)
            
            # Generate additional files
            self._generate_additional_files(project_dir, project_context)
            
            # Create zip file
            zip_path = self._create_zip(project_dir, project_name or "generated_project")
            
            return zip_path, workflow_name, analysis
            
        finally:
            # Clean up temporary directory
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def _create_structure_recursive(self, structure: Dict, base_path: str, context: Dict, current_path: str = ""):
        """Recursively create directory structure and files."""
        if isinstance(structure, dict):
            for key, value in structure.items():
                full_path = os.path.join(base_path, key)
                relative_path = os.path.join(current_path, key) if current_path else key
                
                if isinstance(value, dict):
                    # Create directory
                    os.makedirs(full_path, exist_ok=True)
                    self._create_structure_recursive(value, full_path, context, relative_path)
                    
                elif isinstance(value, list):
                    # Create directory and process files
                    os.makedirs(full_path, exist_ok=True)
                    for item in value:
                        if isinstance(item, str):
                            # Create file
                            file_path = os.path.join(full_path, item)
                            content = self.template_generator.generate_file_content(
                                item, 
                                os.path.join(relative_path, item),
                                context
                            )
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.write(content)
                        elif isinstance(item, dict):
                            self._create_structure_recursive(item, full_path, context, relative_path)
                
                elif isinstance(value, str):
                    # Create file directly
                    content = self.template_generator.generate_file_content(
                        key, 
                        relative_path,
                        context
                    )
                    with open(full_path, 'w', encoding='utf-8') as f:
                        f.write(content)
    
    def _generate_additional_files(self, project_dir: str, context: Dict):
        """Generate additional project files like README, .gitignore, etc."""
        
        # Generate README.md
        readme_path = os.path.join(project_dir, "README.md")
        if not os.path.exists(readme_path):
            readme_content = self.template_generator._generate_readme(context)
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(readme_content)
        
        # Generate .gitignore
        gitignore_path = os.path.join(project_dir, ".gitignore")
        if not os.path.exists(gitignore_path):
            gitignore_content = self.template_generator._gitignore_template(context)
            with open(gitignore_path, 'w', encoding='utf-8') as f:
                f.write(gitignore_content)
        
        # Generate LICENSE
        license_path = os.path.join(project_dir, "LICENSE")
        if not os.path.exists(license_path):
            license_content = f'''MIT License

Copyright (c) {datetime.now().year} {context.get('project_name', 'Generated Project')}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''
            with open(license_path, 'w', encoding='utf-8') as f:
                f.write(license_content)
        
        # Generate CONTRIBUTING.md
        contributing_path = os.path.join(project_dir, "CONTRIBUTING.md")
        if not os.path.exists(contributing_path):
            contributing_content = f'''# Contributing to {context.get('project_name', 'Generated Project')}

Thank you for your interest in contributing! This document provides guidelines for contributing to this project.

## Development Setup

1. Fork the repository
2. Clone your fork: `git clone <your-fork-url>`
3. Install dependencies (see README.md)
4. Create a new branch: `git checkout -b feature/your-feature`

## Git Workflow: {context.get('workflow', 'Feature Branch Workflow')}

This project follows the {context.get('workflow', 'Feature Branch Workflow')} approach. Please:

1. Create descriptive branch names
2. Write clear commit messages
3. Test your changes thoroughly
4. Update documentation as needed

## Code Style

- Follow the existing code style
- Run linters before committing
- Add comments for complex logic
- Write tests for new features

## Pull Request Process

1. Ensure all tests pass
2. Update documentation if needed
3. Fill out the pull request template
4. Request review from maintainers

## Reporting Issues

- Use the issue template
- Provide clear reproduction steps
- Include relevant system information
- Be respectful and constructive

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Help others learn and grow
- Report inappropriate behavior

Thank you for contributing!
'''
            with open(contributing_path, 'w', encoding='utf-8') as f:
                f.write(contributing_content)
    
    def _create_zip(self, project_dir: str, project_name: str) -> str:
        """Create zip file of the generated project."""
        zip_path = os.path.join(tempfile.gettempdir(), f"{project_name}.zip")
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(project_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, os.path.dirname(project_dir))
                    zipf.write(file_path, arcname)
        
        return zip_path


def create_gradio_interface():
    """Create and configure the Gradio interface."""
    
    generator = ProjectGenerator()
    
    def process_project(json_file, project_name):
        """Process uploaded JSON and generate project."""
        try:
            if json_file is None:
                return None, "Please upload a JSON file", ""
            
            # Read and parse JSON
            with open(json_file.name, 'r', encoding='utf-8') as f:
                directory_json = json.load(f)
            
            # Generate project
            zip_path, workflow_name, analysis = generator.generate_project(
                directory_json, 
                project_name or "generated_project"
            )
            
            # Create summary
            summary = f"""
## Project Generation Summary

**Project Name:** {project_name or "generated_project"}
**Recommended Git Workflow:** {workflow_name}
**Total Files:** {analysis['total_files']}
**Directories:** {analysis['directories']}
**Languages Detected:** {', '.join(analysis['languages']) if analysis['languages'] else 'None'}
**Complexity Score:** {analysis['complexity_score']:.1f}

### Project Indicators:
{chr(10).join(f"- {indicator}" for indicator in analysis['project_indicators'][:10])}

### Workflow Recommendation Reasoning:
The system analyzed your project structure and recommended **{workflow_name}** based on:
- Project complexity and size
- Number of services/modules detected
- Language diversity
- File organization patterns

Your generated project includes:
- ✅ Complete file structure with appropriate templates
- ✅ Language-specific boilerplate code
- ✅ README.md with project documentation
- ✅ .gitignore with appropriate rules
- ✅ LICENSE file (MIT)
- ✅ CONTRIBUTING.md guidelines
- ✅ Git workflow recommendations
- ✅ Build and configuration files

**Download your generated project using the link below!**
"""
            
            return zip_path, summary, ""
            
        except json.JSONDecodeError as e:
            return None, f"❌ Invalid JSON file: {str(e)}", ""
        except Exception as e:
            return None, f"❌ Error generating project: {str(e)}", ""
    
    # Create Gradio interface
    with gr.Blocks(
        title="Code Generation Agent",
        theme=gr.themes.Soft(),
        css="""
        .gradio-container {
            max-width: 1200px !important;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        .summary-box {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
        }
        """
    ) as iface:
        
        gr.HTML("""
        <div class="header">
            <h1>🚀 Code Generation Agent</h1>
            <p>Transform your directory structure JSON into a complete, ready-to-use project with intelligent Git workflow recommendations!</p>
        </div>
        """)
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.HTML("<h3>📁 Upload Your Project Structure</h3>")
                
                json_file = gr.File(
                    label="Directory Structure JSON",
                    file_types=[".json"],
                    file_count="single"
                )
                
                project_name = gr.Textbox(
                    label="Project Name (Optional)",
                    placeholder="my-awesome-project",
                    value=""
                )
                
                generate_btn = gr.Button(
                    value="🔥 Generate Project",
                    variant="primary",
                    size="lg"
                )
                
                gr.HTML("""
<div style="margin-top: 20px; padding: 15px; background-color: #1e1e1e; border-radius: 8px; color: #f0f0f0;">
    <h4 style="color: #ffffff;">📋 JSON Format Example:</h4>
    <pre style="background: #2c2c2c; color: #f8f8f2; padding: 10px; border-radius: 4px; overflow-x: auto;">
{
  "src": {
    "components": ["Button.js", "Header.js"],
    "pages": ["Home.js", "About.js"],
    "utils": ["helpers.py", "config.py"]
  },
  "tests": ["test_main.py"],
  "docs": ["api.md"],
  "package.json": "",
  "README.md": ""
}</pre>
</div>
""")

            
            with gr.Column(scale=2):
                gr.HTML("<h3>📊 Generation Results</h3>")
                
                download_file = gr.File(
                    label="📦 Download Generated Project",
                    visible=True
                )
                
                summary_output = gr.Markdown(
                    label="Project Summary",
                    value="Upload a JSON file and click 'Generate Project' to see the results here."
                )
                
                error_output = gr.Textbox(
                    label="Errors",
                    visible=False
                )
        
        # Event handlers
        generate_btn.click(
            fn=process_project,
            inputs=[json_file, project_name],
            outputs=[download_file, summary_output, error_output]
        )
        
        gr.HTML("""
<div style="margin-top: 40px; text-align: center; padding: 20px; background-color: #1e1e1e; border-radius: 10px; color: #f0f0f0;">
    <h3 style="color: #ffffff;">🎯 Supported Git Workflows</h3>
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-top: 20px;">
        <div style="padding: 10px; background: #2c2c2c; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.3); color: #ffffff;">
            <strong>Centralized</strong><br>
            <small>Simple, single-branch workflow</small>
        </div>
        <div style="padding: 10px; background: #2c2c2c; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.3); color: #ffffff;">
            <strong>Feature Branch</strong><br>
            <small>Feature-based development</small>
        </div>
        <div style="padding: 10px; background: #2c2c2c; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.3); color: #ffffff;">
            <strong>Gitflow</strong><br>
            <small>Structured release management</small>
        </div>
        <div style="padding: 10px; background: #2c2c2c; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.3); color: #ffffff;">
            <strong>Forking</strong><br>
            <small>Open source collaboration</small>
        </div>
        <div style="padding: 10px; background: #2c2c2c; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.3); color: #ffffff;">
            <strong>Trunk-based</strong><br>
            <small>Continuous integration focused</small>
        </div>
        <div style="padding: 10px; background: #2c2c2c; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.3); color: #ffffff;">
            <strong>Monorepo</strong><br>
            <small>Single repo, multiple projects</small>
        </div>
    </div>
</div>

<div style="margin-top: 20px; text-align: center; color: #aaaaaa;">
    <p>💡 <strong>Pro Tip:</strong> The system automatically detects the best Git workflow based on your project structure, complexity, and detected technologies!</p>
    <p>🔧 Built with ❤️ by Code Generation Agent | Powered by Groq AI</p>
</div>
""")

    
    return iface


def main():
    """Main function to run the Gradio application."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Code Generation Agent - Transform directory JSON into complete projects')
    parser.add_argument('--port', '-p', type=int, default=None, help='Port to run the server on (default: auto-detect)')
    parser.add_argument('--host', default='127.0.0.1', help='Host to bind to (default: 127.0.0.1)')
    parser.add_argument('--share', action='store_true', help='Create a public shareable link')
    parser.add_argument('--debug', action='store_true', help='Run in debug mode')
    
    args = parser.parse_args()
    
    print("🚀 Starting Code Generation Agent...")
    print("📋 Loading templates and initializing AI models...")
    
    # Check for Groq API key
    if not os.getenv('GROQ_API_KEY'):
        print("⚠️  Warning: GROQ_API_KEY not found in environment variables.")
        print("   The agent will still work but advanced AI features may be limited.")
    
    # Create and launch Gradio interface
    iface = create_gradio_interface()
    
    print("✅ Code Generation Agent is ready!")
    
    if args.port:
        # Use specified port
        print(f"🔌 Starting server on {args.host}:{args.port}")
        try:
            iface.launch(
                server_name=args.host,
                server_port=args.port,
                share=args.share,
                debug=args.debug,
                show_error=True,
                inbrowser=True
            )
        except Exception as e:
            print(f"❌ Failed to start on port {args.port}: {str(e)}")
            print("🔄 Trying auto port detection...")
            iface.launch(
                server_name=args.host,
                server_port=None,
                share=args.share,
                debug=args.debug,
                show_error=True,
                inbrowser=True
            )
    else:
        # Try different ports if the default one fails
        ports_to_try = [8080, 8000, 3000, 5000, 8888, 9000, 7861, 7860]
        
        print("🌐 Access the interface at the URL shown below:")
        
        for port in ports_to_try:
            try:
                print(f"🔌 Trying to start server on {args.host}:{port}...")
                iface.launch(
                    server_name=args.host,
                    server_port=port,
                    share=args.share,
                    debug=args.debug,
                    show_error=True,
                    prevent_thread_lock=False,
                    inbrowser=True
                )
                print(f"✅ Server successfully started on {args.host}:{port}")
                break
            except Exception as e:
                print(f"❌ Port {port} failed: {str(e)}")
                if port == ports_to_try[-1]:  # Last port in list
                    print("⚠️  All predefined ports failed. Trying with auto port selection...")
                    iface.launch(
                        server_name=args.host,
                        server_port=None,  # Let Gradio choose an available port
                        share=args.share,
                        debug=args.debug,
                        show_error=True,
                        inbrowser=True
                    )


if __name__ == "__main__":
    main()