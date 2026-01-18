# Agent Skills

A collection of custom skills for Claude Code, Anthropic's official CLI for Claude. These skills extend Claude Code's capabilities with specialized, domain-specific functionality.

## What are Agent Skills?

Agent skills are modular extensions that provide Claude Code with specialized knowledge and tools for specific tasks. Each skill includes:

- **SKILL.md** - Skill definition with instructions and procedures
- **References** - Domain knowledge and pattern libraries
- **Scripts** - Automation tools and utilities
- **Assets** - Templates and supporting files

## Available Skills

### Next.js Security Scan

A comprehensive security vulnerability scanner for Next.js and TypeScript/JavaScript projects.

**Features:**
- OWASP Top 10:2025 vulnerability detection
- XSS and injection flaw identification
- Authentication and authorization issue detection
- Hardcoded secrets and credentials scanning
- Next.js-specific vulnerability checks
- Dependency audit for known CVEs
- Actionable security reports

**Scan Types:**
- **Quick Scan** - Fast scan for critical vulnerabilities
- **Full Scan** - Comprehensive security assessment
- **Targeted Scan** - Focus on specific vulnerability categories (XSS, injection, auth, secrets, deps, nextjs)

**Usage:**
```
/nextjs-security-scan
```

---

### Python Security Scan

A comprehensive security vulnerability scanner for Python projects including Flask, Django, and FastAPI applications.

**Features:**
- OWASP Top 10:2025 vulnerability detection
- Python-specific vulnerabilities (eval, exec, pickle, etc.)
- Framework auto-detection and framework-specific checks
- SQL/NoSQL/Command injection detection
- Insecure deserialization patterns
- Hardcoded secrets and credentials scanning
- Dependency audit via pip-audit/safety
- Actionable security reports with CWE references

**Supported Frameworks:**
- **Flask** - Template injection, session security, debug mode, CORS
- **Django** - ORM injection, CSRF, settings security, middleware
- **FastAPI** - Input validation, authentication, CORS, Pydantic security

**Scan Types:**
- **Quick Scan** - Critical vulnerabilities (secrets, dangerous functions, known CVEs)
- **Full Scan** - Comprehensive security assessment
- **Targeted Scan** - Focus on specific categories (injection, deserialization, auth, secrets, deps, crypto, flask, django, fastapi)

**Usage:**
```
/python-security-scan
```

---

### Subtitle Correction

Corrects speech recognition errors in subtitle files (.srt) while preserving exact timeline information.

**Features:**
- Chinese and English subtitle support
- Phonetic error correction (同音字/谐音)
- Technical term recognition (AI/ML, programming)
- English-Chinese mixed content handling
- Code identifier formatting (snake_case, camelCase)
- Interactive terminology collection workflow
- Validation script for structural integrity

**Workflow:**
1. Collects domain-specific terminology from user
2. Identifies speech recognition error patterns
3. Applies corrections while preserving timestamps
4. Validates output maintains structural integrity

**Usage:**
```
/subtitle-correction
```

## Project Structure

```
agent-skills/
├── skills/
│   ├── nextjs-security-scan/
│   │   ├── SKILL.md              # Skill definition
│   │   ├── references/           # Vulnerability pattern libraries
│   │   │   ├── owasp-top-10.md
│   │   │   ├── xss-patterns.md
│   │   │   ├── injection-patterns.md
│   │   │   ├── auth-vulnerabilities.md
│   │   │   └── nextjs-specific.md
│   │   ├── scripts/              # Automation tools
│   │   │   ├── dependency-audit.sh
│   │   │   ├── secret-scanner.py
│   │   │   └── pattern-scanner.py
│   │   └── assets/               # Templates
│   │       └── report-template.md
│   │
│   ├── python-security-scan/
│   │   ├── SKILL.md              # Skill definition
│   │   ├── references/           # Vulnerability pattern libraries
│   │   │   ├── owasp-top-10.md
│   │   │   ├── python-vulnerabilities.md
│   │   │   ├── injection-patterns.md
│   │   │   ├── deserialization.md
│   │   │   ├── flask-security.md
│   │   │   ├── django-security.md
│   │   │   └── fastapi-security.md
│   │   ├── scripts/              # Automation tools
│   │   │   ├── dependency-audit.sh
│   │   │   ├── secret-scanner.py
│   │   │   └── pattern-scanner.py
│   │   └── assets/               # Templates
│   │       └── report-template.md
│   │
│   └── subtitle-correction/
│       ├── SKILL.md              # Skill definition
│       ├── references/           # Domain knowledge
│       │   ├── terminology.md
│       │   └── srt-format.md
│       └── scripts/              # Validation tools
│           └── subtitle_tool.py
├── .claude/                      # Claude Code configuration
├── LICENSE
└── README.md
```

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/sugarforever/agent-skills.git
   ```

2. Add the skills directory to your Claude Code configuration, or copy individual skills to your project's `.claude/skills/` directory.

## Creating New Skills

To create a new skill:

1. Create a new directory under `skills/` with your skill name
2. Add a `SKILL.md` file with:
   - YAML frontmatter (name, description)
   - Usage instructions
   - Procedures and workflows
3. Add supporting files as needed:
   - `references/` - Domain knowledge
   - `scripts/` - Automation tools
   - `assets/` - Templates and resources

## Requirements

### Next.js Security Scan
- Python 3.x (for secret scanner)
- Node.js and npm/yarn/pnpm (for dependency audit)
- jq (for JSON parsing in audit script)

### Python Security Scan
- Python 3.8+
- pip-audit or safety (for dependency audit): `pip install pip-audit`
- jq (optional, for JSON parsing)

## License

MIT License - see [LICENSE](LICENSE) for details.

## Contributing

Contributions are welcome! Please feel free to submit pull requests with new skills or improvements to existing ones.
