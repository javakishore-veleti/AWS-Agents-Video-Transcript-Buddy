# AWS-Agents-Video-Transcript-Buddy

AI-powered video transcript query system using AWS Bedrock AgentCore with support for multiple LLM providers (OpenAI, Ollama, LM Studio).

---

## 🚀 Quick Start

```bash
# Clone the repo
git clone https://github.com/javakishore-veleti/AWS-Agents-Video-Transcript-Buddy.git
cd AWS-Agents-Video-Transcript-Buddy

# Setup everything (auto-detects your OS)
npm run setup

# Start the backend server
npm run dev

# In another terminal, start the UI
npm run ui
```

**That's it!** Open http://localhost:4200 for the UI and http://localhost:8000/docs for the API.

---

# 📋 NPM Commands Reference

---

## 🆕 FIRST-TIME SETUP (Run Once)

Commands you only need to run when setting up a new development environment.

### Core Setup

| Command | Description |
|---------|-------------|
| `npm run setup` | 🔧 **One command setup** - Creates venv, installs all dependencies (auto-detects OS) |
| `npm run verify` | ✅ Verify all dependencies are installed correctly |
| `npm run ui:install` | 📦 Install Angular UI dependencies |

### Optional: Local LLM Setup (Ollama)

| Command | Description |
|---------|-------------|
| `npm run install:ollama` | 📦 Install Ollama for local LLM support |
| `npm run pull:model` | 📥 Pull default Ollama model (llama3.2) |

### Ollama Management

| Command | Description |
|---------|-------------|
| `npm run ollama:start` | ▶️ Start Ollama service in background |
| `npm run ollama:stop` | ⏹️ Stop Ollama service |
| `npm run ollama:restart` | 🔄 Restart Ollama service |
| `npm run ollama:status` | 📊 Check Ollama status and list models |

### Optional: Cloud Provider Setup

#### AWS Profile (macOS/Linux)
| Command | Description |
|---------|-------------|
| `npm run aws:profile:setup:mac` | Configure AWS profile interactively |
| `npm run aws:s3:create:mac` | Create S3 bucket for transcripts |

#### AWS Profile (Windows)
| Command | Description |
|---------|-------------|
| `npm run aws:profile:setup:win` | Configure AWS profile interactively |
| `npm run aws:s3:create:win` | Create S3 bucket for transcripts |

#### OpenAI API Key (macOS/Linux)
| Command | Description |
|---------|-------------|
| `npm run openai:setup:mac` | Show instructions for setting up OpenAI key |
| `npm run openai:export:mac` | Interactively add OpenAI key to shell config |

#### OpenAI API Key (Windows)
| Command | Description |
|---------|-------------|
| `npm run openai:setup:win` | Show instructions for setting up OpenAI key |

### Environment File Setup

| Command | Description |
|---------|-------------|
| `npm run env:setup:mac` | Copy .env.example to .env (macOS/Linux) |
| `npm run env:setup:win` | Copy .env.example to .env (Windows) |

### Portal Installation (if using other portals)

| Command | Description |
|---------|-------------|
| `npm run portal:hub:install` | Install Hub portal dependencies |
| `npm run portal:admin:install` | Install Admin Center dependencies |
| `npm run portal:itops:install` | Install IT Ops Center dependencies |
| `npm run portal:aiml:install` | Install AI/ML Center dependencies |
| `npm run portal:integrations:install` | Install Integrations Center dependencies |
| `npm run portals:install:all` | Install ALL portal dependencies |

---

## 🔄 EVERYDAY COMMANDS (Run Frequently)

Commands you'll use regularly during development.

### Start Development Servers

| Command | Description |
|---------|-------------|
| `npm run dev` | 🚀 Start backend server with hot reload (auto-detects OS) |
| `npm run ui` | 🎨 Start Angular UI (port 4200) |
| `npm run start` | 🚀 Start backend in production mode |

### API Testing

| Command | Description |
|---------|-------------|
| `npm run test:api` | Run all API tests |
| `npm run test:auth` | Test authentication endpoints |
| `npm run test:health` | Test health check endpoint |
| `npm run test:query` | Test query endpoints |
| `npm run test:transcripts` | Test transcript endpoints |
| `npm run test:usage` | Test usage tracking endpoints |

### Data Cleanup (Reset Data Without Reinstalling)

| Command | Description |
|---------|-------------|
| `npm run clean:db` | Delete SQLite database |
| `npm run clean:vector` | Delete FAISS vector store |
| `npm run clean:transcripts` | Delete uploaded transcript files |
| `npm run clean:data` | Delete all data (db + vectors + transcripts) |

### Verification

| Command | Description |
|---------|-------------|
| `npm run verify` | ✅ Verify all dependencies are working |
| `npm run aws:profile:verify:mac` | Verify AWS credentials (macOS/Linux) |
| `npm run aws:profile:verify:win` | Verify AWS credentials (Windows) |
| `npm run openai:verify:mac` | Verify OpenAI key is set (macOS/Linux) |
| `npm run openai:verify:win` | Verify OpenAI key is set (Windows) |

### Portal Development

| Command | Description |
|---------|-------------|
| `npm run portal:hub:dev` | Start Hub portal dev server (port 4200) |
| `npm run portal:admin:dev` | Start Admin Center dev server |
| `npm run portal:itops:dev` | Start IT Ops Center dev server |
| `npm run portal:aiml:dev` | Start AI/ML Center dev server |
| `npm run portal:integrations:dev` | Start Integrations Center dev server |

### Build for Production

| Command | Description |
|---------|-------------|
| `npm run ui:build` | Build UI for production |
| `npm run portal:hub:build:prod` | Build Hub portal for production |
| `npm run portals:build:all` | Build ALL portals for production |

### Help

| Command | Description |
|---------|-------------|
| `npm run help` | Show command summary |
| `npm run run:help` | Show cross-platform command help |

---

## 🔧 MAINTENANCE COMMANDS (Occasional Use)

Commands for troubleshooting, cleanup, or resetting your environment.

### Full Reset

| Command | Description |
|---------|-------------|
| `npm run reset` | 🔄 **Full reset** - Clean everything and re-setup |
| `npm run clean:all` | Delete everything (venv + all data) |
| `npm run clean:venv` | Remove virtual environment only |

### Platform-Specific Cleanup

#### macOS / Linux
| Command | Description |
|---------|-------------|
| `npm run clean:venv:mac` | Remove venv |
| `npm run clean:vectors:mac` | Clear vector store |

#### Windows
| Command | Description |
|---------|-------------|
| `npm run clean:venv:win` | Remove venv |
| `npm run clean:vectors:win` | Clear vector store |

### Platform-Specific Backend Commands

#### macOS / Linux
| Command | Description |
|---------|-------------|
| `npm run backend:dev:mac` | Start backend with hot reload |
| `npm run backend:start:mac` | Start backend (production) |
| `npm run backend:check:mac` | Verify Python dependencies |
| `npm run test:backend:mac` | Run pytest tests |
| `npm run test:backend:cov:mac` | Run tests with coverage |

#### Windows
| Command | Description |
|---------|-------------|
| `npm run backend:dev:win` | Start backend with hot reload |
| `npm run backend:start:win` | Start backend (production) |
| `npm run backend:check:win` | Verify Python dependencies |
| `npm run test:backend:win` | Run pytest tests |
| `npm run test:backend:cov:win` | Run tests with coverage |

### Platform-Specific Venv Commands

#### macOS / Linux
| Command | Description |
|---------|-------------|
| `npm run venv:create:mac` | Create Python venv |
| `npm run venv:install:mac` | Install Python dependencies |
| `npm run venv:setup:mac` | Create venv + install dependencies |
| `npm run venv:activate:mac:help` | Show venv activation command |

#### Windows
| Command | Description |
|---------|-------------|
| `npm run venv:create:win` | Create Python venv |
| `npm run venv:install:win` | Install Python dependencies |
| `npm run venv:setup:win` | Create venv + install dependencies |
| `npm run venv:activate:win:help` | Show venv activation command |

### AWS Commands

#### macOS / Linux
| Command | Description |
|---------|-------------|
| `npm run aws:profile:list:mac` | List all AWS profiles |
| `npm run aws:s3:list:mac` | List S3 buckets |

#### Windows
| Command | Description |
|---------|-------------|
| `npm run aws:profile:list:win` | List all AWS profiles |
| `npm run aws:s3:list:win` | List S3 buckets |

### Environment File

| Command | Description |
|---------|-------------|
| `npm run env:edit:mac` | Edit .env file in terminal editor |

---

## 🤖 Supported LLM Providers

| Provider | Type | Status | Configuration |
|----------|------|--------|---------------|
| **OpenAI** | Cloud | ✅ Available | Set `OPENAI_API_KEY` env variable |
| **Ollama** | Local | ✅ Available | `npm run install:ollama && npm run pull:model` |
| **LM Studio** | Local | ✅ Available | Run LM Studio server on port 1234 |
| **Google Gemini** | Cloud | 🔜 Coming Soon | Q2 2026 |
| **Anthropic Claude** | Cloud | 🔜 Coming Soon | Q2 2026 |
| **Microsoft Copilot** | Cloud | 🔜 Coming Soon | Q3 2026 |
| **n8n Agentic** | Integration | 🔜 Coming Soon | Q3 2026 |
| **MCP Servers** | Custom | 🔜 Coming Soon | Q4 2026 |

---

## 📁 Project Setup Commands

```shell
# Clone the repo
git clone https://github.com/javakishore-veleti/AWS-Agents-Video-Transcript-Buddy.git
cd AWS-Agents-Video-Transcript-Buddy

# Create core instruction folders
mkdir -p .github/instructions/aws-core
mkdir -p .github/instructions/aws-s3
mkdir -p .github/instructions/aws-bedrock-agentcore
mkdir -p .github/instructions/agents
mkdir -p .github/instructions/tools
mkdir -p .github/instructions/vector-store
mkdir -p .github/instructions/backend-deployment
mkdir -p .github/instructions/aws-api-gateway
mkdir -p .github/instructions/aws-cloudwatch
mkdir -p .github/instructions/angular-ui
mkdir -p .github/instructions/DevOps

# Create optional instruction folders
mkdir -p .github/instructions/aws-rds
mkdir -p .github/instructions/aws-quicksight
mkdir -p .github/instructions/aws-cognito
mkdir -p .github/instructions/aws-lambda
mkdir -p .github/instructions/aws-appsync
mkdir -p .github/instructions/aws-dynamodb
mkdir -p .github/instructions/aws-sqs
mkdir -p .github/instructions/aws-sns
mkdir -p .github/instructions/aws-eventbridge
mkdir -p .github/instructions/aws-secrets-manager
mkdir -p .github/instructions/aws-ecr
mkdir -p .github/instructions/aws-route53
mkdir -p .github/instructions/aws-cloudfront
mkdir -p .github/instructions/aws-waf
mkdir -p .github/instructions/aws-kms
mkdir -p .github/instructions/aws-step-functions
mkdir -p .github/instructions/aws-kinesis
mkdir -p .github/instructions/aws-opensearch
mkdir -p .github/instructions/cicd-github-actions
mkdir -p .github/instructions/testing

# Create source code folders
mkdir -p backend/app/routers
mkdir -p backend/app/services
mkdir -p backend/app/models
mkdir -p frontend/src/app
mkdir -p agents/query_validator
mkdir -p agents/query_resolver
mkdir -p agents/data_analyzer
mkdir -p tools/content_search
mkdir -p tools/context_enrichment
mkdir -p tools/data_extraction
mkdir -p cli/commands
mkdir -p cli/utils
mkdir -p DevOps
mkdir -p config
mkdir -p scripts
mkdir -p docs
```