# Airdrop Hunting with Multi-Agent Systems

This repository is built on top of the Browser-Use repo and is meant to integrate web3 airdrop hunting with AI agents. Currently this repo focusses on Layer3 and Galxe but feel free to build on it to expand into more platforms!

# Quick start

With pip:

```bash
pip install browser-use
```

(optional) install playwright:

```bash
playwright install
```

And don't forget to add your API keys to your `.env` file.

```bash
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
```

# Demos

To be added soon!


# Features ⭐

This framework is built using browser-use, allowing automated interaction with websites to complete on-chain tasks efficiently. Below are the steps to set up and use the system securely.

## Getting Started

1. Connecting Your Wallet Securely
Use WalletConnect on your phone to connect to your chosen quest website.
Keep this tab open to prevent the agent from getting blocked.
This approach is safer than using browser extensions for two key reasons:
Security Risks with Browser Extensions – Connecting directly to a wallet extension would require disabling critical security modules, which is impractical for general users.
User-Controlled Approvals – Final transaction approvals remain manual, preventing unintended transactions.
2. Running the Scripts
Once connected, run the corresponding script (Layer3 or Galxe).
By default, the Galxe script will identify and attempt to complete the top 3 trending quests automatically.
3. Human Oversight
While the agent handles most tasks autonomously, occasional manual intervention may be required if it deviates from the intended workflow.
4. Security Best Practices
This is a proof of concept – use a burner wallet to minimize risk and avoid any potential loss of funds.


## Disclaimer
This framework is experimental and provided as-is. Use at your own discretion, and always exercise caution when interacting with on-chain applications.

# Contributing

Contributions are welcome! Feel free to open issues for bugs or feature requests.

## Local Setup

1. Create a virtual environment and install dependencies:

```bash
# To install all dependencies including dev
pip install . ."[dev]"
```

2. Add your API keys to the `.env` file:

```bash
cp .env.example .env
```

or copy the following to your `.env` file:

```bash
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
```

You can use any LLM model supported by LangChain by adding the appropriate environment variables. See [langchain models](https://python.langchain.com/docs/integrations/chat/) for available options.


---

