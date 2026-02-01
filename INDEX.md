# 📖 AI Release Guardian - Documentation Index

## 🎯 Start Here (Choose Your Path)

### 👤 **I'm a Developer** (Want to understand the code?)
1. Read: [README.md](README.md) (2 mins)
2. Read: [QUICK_REFERENCE.md](QUICK_REFERENCE.md) (5 mins)
3. Read: [ARCHITECTURE.md](ARCHITECTURE.md) (15 mins)
4. Explore: `src/agents/planner.py` (entry point for code)

### 🚀 **I'm Ready to Deploy** (Want to get it live?)
1. Read: [GETTING_STARTED.md](GETTING_STARTED.md) (15 mins)
2. Follow: Setup & Local Testing section
3. Follow: Deployment to AWS Lambda section
4. Use: [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) (30 mins)

### 📊 **I'm a Manager** (Want to understand business value?)
1. Read: [README.md](README.md) (2 mins)
2. Read: [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) (10 mins)
3. Section: "What to Measure (Phase 1 Success)"

### ❓ **I Have Questions** (Looking for specific answers?)
- **"How does it work?"** → [ARCHITECTURE.md](ARCHITECTURE.md)
- **"How do I deploy?"** → [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)
- **"What are the APIs?"** → [QUICK_REFERENCE.md](QUICK_REFERENCE.md#mcp-server-endpoints)
- **"How do I use the agents?"** → [GETTING_STARTED.md](GETTING_STARTED.md#mcp-server-endpoints)
- **"What's the project status?"** → [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)
- **"How do I troubleshoot?"** → [GETTING_STARTED.md](GETTING_STARTED.md#troubleshooting)

---

## 📚 Documentation Overview

### Core Documentation

| Document | Purpose | Read Time | Audience |
|----------|---------|-----------|----------|
| [README.md](README.md) | Project overview & quick facts | 2 min | Everyone |
| [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) | Complete project status | 10 min | Managers, DevOps |
| [QUICK_REFERENCE.md](QUICK_REFERENCE.md) | API examples & quick start | 5 min | Developers |
| [ARCHITECTURE.md](ARCHITECTURE.md) | System design & data flow | 15 min | Architects, Lead devs |
| [GETTING_STARTED.md](GETTING_STARTED.md) | Detailed setup guide | 15 min | All developers |
| [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) | Pre-deployment validation | 30 min | DevOps, Release mgr |

### What Each Doc Covers

#### 1. **README.md** - 2 minute read
- What is AI Release Guardian?
- Quick start commands
- Project structure overview
- Configuration instructions
- Next steps

#### 2. **PROJECT_SUMMARY.md** - 10 minute read
- Complete project status
- What was built (features list)
- Project structure breakdown
- Core features explained
- Success metrics to track
- Phase 1 vs Phase 2
- Quick timeline

#### 3. **QUICK_REFERENCE.md** - 5 minute read
- What this project solves
- Quick setup (5 mins)
- Key files explained
- Core concepts (agents, server, flow)
- API examples with curl
- Environment setup
- Running tests
- Deployment to Lambda
- Troubleshooting

#### 4. **ARCHITECTURE.md** - 15 minute read
- System overview (with diagram)
- Data flow (input → processing → output)
- Agent responsibilities (4 agents)
- Integration points (GitHub, Jira, Claude)
- Data models (TestScenario, RiskAssessment, etc)
- Performance characteristics
- Security architecture
- Scalability notes

#### 5. **GETTING_STARTED.md** - 15 minute read
- Prerequisites
- Installation steps
- Configuration (.env setup)
- Running locally
- API testing examples
- Deployment to AWS Lambda
- GitHub webhook configuration
- How it works (Phase 1 details)
- Project structure explanation
- MCP server endpoints
- Troubleshooting guide

#### 6. **DEPLOYMENT_CHECKLIST.md** - 30 minute read
- Pre-deployment validation
- Local testing checklist
- API validation
- External services validation
- AWS Lambda deployment steps
- GitHub integration steps
- Monitoring & observability setup
- Security checklist
- Performance verification
- Success criteria
- Deployment timeline

---

## 🗂️ Project Structure (File Reference)

### Documentation Files (You are here!)
```
├── INDEX.md                        ← You are here!
├── README.md                       → Start for overview
├── PROJECT_SUMMARY.md              → Project status & metrics
├── QUICK_REFERENCE.md              → API & quick start
├── ARCHITECTURE.md                 → System design
├── GETTING_STARTED.md              → Setup guide
├── DEPLOYMENT_CHECKLIST.md         → Pre-deploy checklist
└── GETTING_STARTED_NEXT_STEPS.md   → Phase 1 summary
```

### Source Code Files
```
src/
├── agents/                         # AI agents (4 total)
│   ├── planner.py                 # PR + Jira analysis
│   ├── test_generator.py          # Test generation
│   ├── risk_scorer.py             # Risk assessment
│   └── rollback.py                # Rollback planning
├── integrations/                   # External APIs (3 total)
│   ├── github.py                  # GitHub API wrapper
│   ├── jira.py                    # Jira API wrapper
│   └── claude.py                  # Claude AI wrapper
├── mcp/
│   └── server.py                  # MCP API server
├── models/
│   └── schemas.py                 # Pydantic data models
└── utils/
    └── logger.py                  # Logging setup
```

### Deployment Files
```
lambda/
├── handler.py                     # GitHub webhook handler
├── template.yaml                  # AWS SAM template
└── requirements.txt               # Lambda dependencies
```

### Test Files
```
tests/
├── test_agents.py                 # Agent unit tests
└── test_integrations.py           # Integration tests
```

### Configuration
```
├── .env.example                   # Environment template
├── .gitignore                     # Git exclusions
└── requirements.txt               # Root dependencies
```

---

## 🎯 Common Workflows

### Workflow 1: "I want to understand the project"
```
1. Read: README.md (2 min)
2. Read: PROJECT_SUMMARY.md (10 min)
3. Read: ARCHITECTURE.md (15 min)
4. Browse: src/agents/ (understand agents)
Total: ~30 minutes
```

### Workflow 2: "I want to deploy this today"
```
1. Read: QUICK_REFERENCE.md (5 min)
2. Follow: GETTING_STARTED.md setup section (15 min)
3. Run: Local MCP server (5 min)
4. Follow: Lambda deployment section (30 min)
5. Configure: GitHub webhook (5 min)
Total: ~60 minutes
```

### Workflow 3: "I'm deploying to production"
```
1. Read: GETTING_STARTED.md completely (15 min)
2. Use: DEPLOYMENT_CHECKLIST.md (30 min)
3. Test: Each checkbox systematically
4. Monitor: CloudWatch logs post-deployment
Total: ~60-90 minutes
```

### Workflow 4: "I want to add a new agent"
```
1. Read: ARCHITECTURE.md (15 min)
2. Study: src/agents/planner.py (10 min)
3. Copy: src/agents/planner.py → new_agent.py
4. Modify: Your agent logic
5. Register: In src/mcp/server.py
6. Test: With pytest
Total: ~1 hour
```

### Workflow 5: "Something is broken"
```
1. Check: GETTING_STARTED.md#troubleshooting
2. If Lambda: CloudWatch logs
3. If Local: .env configuration
4. If API: Test with curl examples
5. If GitHub: Webhook delivery history
```

---

## 🔑 Key Concepts Explained

### Agents (4 types)
- **Planner:** Reads PR + Jira, extracts context
- **Test Generator:** Creates test scenarios (integration, automation, E2E)
- **Risk Scorer:** Calculates deployment risk (0-100%)
- **Rollback Planner:** Creates rollback procedures

### MCP Server
- API server that exposes agent functionality
- 4 endpoints: `/analyze-release`, `/generate-tests`, `/release-risk-score`, `/rollback-plan`
- Can run locally or in Lambda

### GitHub Webhook
- GitHub sends webhook when PR opened/updated
- Webhook triggers Lambda function
- Lambda calls MCP agents for analysis
- Analysis result posted as PR comment

### Data Models
- `TestScenario` - A single test scenario
- `RiskAssessment` - Risk score + flags
- `PRAnalysis` - Complete PR analysis
- `RollbackPlan` - Rollback steps

---

## 📊 Success Metrics

Track these to measure Phase 1 impact:

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Test case writing time | -40% | Hours/PR before vs after |
| QA review cycle | -25% | Days to approve |
| Early bug detection | +50% | Defects caught in first week |
| Team adoption | 8/10 | Survey QA team |
| System reliability | <1% error | Check Lambda errors |

---

## 🚀 Quick Navigation

### Getting Started
- **First time?** → [README.md](README.md) + [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
- **Want to understand?** → [ARCHITECTURE.md](ARCHITECTURE.md)
- **Ready to deploy?** → [GETTING_STARTED.md](GETTING_STARTED.md)
- **Need checklist?** → [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)

### For Specific Questions
- **"What are the endpoints?"** → [QUICK_REFERENCE.md](QUICK_REFERENCE.md#api-examples)
- **"How do I deploy?"** → [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)
- **"What's the architecture?"** → [ARCHITECTURE.md](ARCHITECTURE.md)
- **"I see an error, help!"** → [GETTING_STARTED.md](GETTING_STARTED.md#troubleshooting)
- **"What's the business case?"** → [README.md](README.md#why-it-wins)

### For Deep Dives
- **Understanding agents** → [ARCHITECTURE.md](ARCHITECTURE.md#agent-responsibilities)
- **Understanding data flow** → [ARCHITECTURE.md](ARCHITECTURE.md#data-flow)
- **Understanding security** → [ARCHITECTURE.md](ARCHITECTURE.md#security-architecture)
- **Understanding deployment** → [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)

---

## 📞 Support Decision Tree

```
Having an issue?

├─ Local development issues?
│  └─ See: GETTING_STARTED.md#troubleshooting
│
├─ Deployment issues?
│  └─ See: DEPLOYMENT_CHECKLIST.md
│
├─ API/endpoint issues?
│  └─ See: QUICK_REFERENCE.md#api-examples
│
├─ Want to understand the code?
│  └─ See: ARCHITECTURE.md + src/agents/
│
├─ Need to add something?
│  └─ See: QUICK_REFERENCE.md#development
│
└─ Something else?
   └─ Search all docs or check src/mcp/server.py
```

---

## ⏱️ Reading Guide by Role

### 👨‍💻 Developer (30 mins)
1. [README.md](README.md) (2 min)
2. [QUICK_REFERENCE.md](QUICK_REFERENCE.md) (5 min)
3. [ARCHITECTURE.md](ARCHITECTURE.md) (15 min)
4. Browse code in `src/agents/` (8 min)

### 🏗️ DevOps/SRE (45 mins)
1. [README.md](README.md) (2 min)
2. [GETTING_STARTED.md](GETTING_STARTED.md) (15 min)
3. [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) (20 min)
4. [ARCHITECTURE.md](ARCHITECTURE.md) - Infrastructure section (8 min)

### 📊 Product Manager (15 mins)
1. [README.md](README.md) (2 min)
2. [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - What to Measure section (8 min)
3. [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Data Models section (5 min)

### 👥 QA Lead (25 mins)
1. [README.md](README.md) (2 min)
2. [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) (10 min)
3. [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - MCP Server Endpoints section (8 min)
4. [ARCHITECTURE.md](ARCHITECTURE.md) - Data Models section (5 min)

---

## 🎯 Next Action

**Where to go from here:**

1. **First time here?**
   - Start: [README.md](README.md)
   - Next: [QUICK_REFERENCE.md](QUICK_REFERENCE.md)

2. **Want to run it?**
   - Start: [GETTING_STARTED.md](GETTING_STARTED.md)

3. **Want to deploy it?**
   - Start: [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)

4. **Want to understand it?**
   - Start: [ARCHITECTURE.md](ARCHITECTURE.md)

---

**Everything you need to understand, deploy, and use AI Release Guardian Phase 1.**

**Choose your starting point above and get going!** 🚀

---

*AI Release Guardian - Documentation Index*  
*Last Updated: Feb 1, 2026*
