# 💷 FinSights: A Financial Insight AI System

[![Python](https://img.shields.io/badge/python-≥3.11-blue.svg)](https://www.python.org/)
[![LangChain](https://img.shields.io/badge/LangChain-🚀-green.svg)](https://www.langchain.com/)
[![Status](https://img.shields.io/badge/status-experimental-orange.svg)]()

An **AI system** for **financial applications** built with **Python** and [**LangChain**](https://www.langchain.com/).  
The goal is to explore how AI can **analyze, summarize, and generate meaningful advice** from complex financial data.

---

## ✨ Features
- ⚡️ Powered by **LangChain**, the leading framework for LLM applications.  
- 🔎 Financial data processing and analysis.  
- 🕵️‍♂️ Based on **Deep Agents** with to-do planning capability, access to a file system for context offloading, task delegation
using sub-agents and carefully-crafted prompts.
- 🛠️ Tools (already implemented): **compound interest calculator**, **Real Estate investment simulation tool**.

---

## 📦 Requirements
- Python ≥ **3.11**  
- [Poetry](https://python-poetry.org/)  for dependency management.  
- Langchain dependencies should be conflict-free in the .toml file. If you encounter problems with the langchain dependencies, check [langchain version compatibility table.](https://python.langchain.com/docs/versions/v0_3/)

---

## 👍 Our principles

At the moment, this application is experimental, which means that we are more focused on getting accurate results. However, it is and will be developed according to these principles:

- **ADLC (Agent Development Life Cycle)** based on **standard DevSecOps practices**, to ensure that agents remain safe, reliable, secure and aligned with regulatory goals (such as compliance with AI regulations).
- **Automated evaluation** integrated into **CI/CD** pipelines, making use of **Langchain AgentEvals** to evaluate agent trajectories (either with **agent trajectory match** or with **LLM-as-a-Judge**).
- **MCP** is preferred whenever possible to stablish secure and governed connections to data.
- **Sandboxing**, which is running agents and their tools insiide constrained execution environments, strictly limiting their capailities. Enforce least-priviledge access to compute, storage, network and system APIs.

---

## ⌛ Soon

- Fiancial Stock Data API will be implemented for financial requests
- Quantitative finance tools.
- Quantitative Real Estate tools.
