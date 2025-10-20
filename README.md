# 💷 FinSights: A Financial Insight AI System

[![Python](https://img.shields.io/badge/python-≥3.11-blue.svg)](https://www.python.org/)
[![LangChain](https://img.shields.io/badge/LangChain-🚀-green.svg)](https://www.langchain.com/)
[![Status](https://img.shields.io/badge/status-experimental-orange.svg)]()

An **AI system** for **financial applications** built with **Python** and [**LangChain**](https://www.langchain.com/).  
The goal is to explore how AI can **analyze, summarize, and generate meaningful advice** from complex financial data.

---

## ✨ Features
- ⚡️ Powered by **LangChain**, the leading framework for LLM applications. Uses **LangGraph** for running stateful agents.
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

---

## 🧑🏻‍💻 Examples

> **REAL ESTATE EXAMPLE**: "Please compute the gross rental yield of a property in Madrid bought for 150,000 euros that needs a 30,000 euro renovation and will be rented for 1,000 euros monthly. My yearly gross salary is 32,000 euros and I want the mortgage term to be 25 years, fixed rate at 2.5%."

    ================== Tool Message ==================
    Name: real_estate_profitability_calculator

    ================== Ai Message ====================
    Name: real_estate_agent

    Here is the analysis of the property investment in Madrid:

    ### Acquisition Cost
    - **Purchase Price:** €150,000
    - **Renovation Cost:** €30,000
    - **ITP Tax Amount (6% of purchase price):** €9,000
    - **Total Acquisition Cost:** €195,300
    - **Down Payment:** €30,000 (your initial cash investment)
    - **Mortgage Loan Amount:** €120,000 (the financed portion)

    ### Mortgage Summary
    - **Monthly Mortgage Payment:** €538.34
    - **Annual Mortgage Payment:** €6,460.08
    - **First Year Interest Expense:** €2,960.08
    - **Annual Principal Payment:** €3,500.00

    ### Income & Expenses
    - **Annual Gross Rental Income:** €12,000 (€1,000 x 12 months)
    - **Total Annual Operating Expenses (including taxes):** €5,710.08
    - **Net Operating Income (NOI):** €6,289.92
    - **Income Tax on Rental Income:** €761.98
    - **Net Income After Taxes:** €5,527.95

    ### Profitability Metrics
    - **Gross Rental Yield:** 6.14%
    (This is calculated as Annual Gross Rental Income divided by Total Acquisition Cost)

    - **Net Rental Yield (Conservative):** 2.83%
    - **Net Rental Yield (Optimistic):** 3.75%

    - **Annual Cash Flow (Conservative):** €2,027.94 (after paying mortgage and expenses)
    - **Annual Cash Flow (Optimistic):** €3,827.94

    ### Interpretation
    - The **gross rental yield** of 6.14% suggests a strong potential return relative to the total investment in the property.
    - The **net rental yields** indicate a more conservative profitability perspective after accounting for operating costs and taxes.
    - You can expect an **annual cash flow** of approximately €2,027.94 to €3,827.94 depending on actual expenses and income levels.

    This investment could provide a solid revenue stream, but you should also consider potential risks and market conditions before proceeding.

> **COMPOUNDING INTEREST EXAMPLE**: "Can you tell me how much money will I get if I start with an initial balance of 865 euros and
invest 123 euros monthly for 12 years at an interest rate of 7.5%?"

    ================== Tool Message ==================

    Name: compound_interest_calculator

    ================== Ai Message ====================
    Name: financial_agent

    If you start with an initial balance of 2000 euros and invest 350 euros monthly for 8 years at an interest rate of 7.5%, here’s how your investment would grow year by year:

    - **Year 1:**
    - Total Deposits: 4200 euros
    - Total Interest Earned: 302.69 euros
    - **Balance:** 6502.69 euros

    - **Year 2:**
    - Total Deposits: 8400 euros
    - Total Interest Earned: 954.94 euros
    - **Balance:** 11354.94 euros

    - **Year 3:**
    - Total Deposits: 12600 euros
    - Total Interest Earned: 1983.88 euros
    - **Balance:** 16583.88 euros

    - **Year 4:**
    - Total Deposits: 16800 euros
    - Total Interest Earned: 3418.75 euros
    - **Balance:** 22218.75 euros

    - **Year 5:**
    - Total Deposits: 21000 euros
    - Total Interest Earned: 5291.08 euros
    - **Balance:** 28291.08 euros

    - **Year 6:**
    - Total Deposits: 25200 euros
    - Total Interest Earned: 7634.81 euros
    - **Balance:** 34834.81 euros

    - **Year 7:**
    - Total Deposits: 29400 euros
    - Total Interest Earned: 10486.55 euros
    - **Balance:** 41886.55 euros

    - **Year 8:**
    - Total Deposits: 33600 euros
    - Total Interest Earned: 13885.74 euros
    - **Balance:** 49485.74 euros

    At the end of the 8 years, your total balance will be approximately **49,485.74 euros**.