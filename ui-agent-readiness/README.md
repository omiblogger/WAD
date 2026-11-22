# Banking AI Assistant — EY 7-day readiness lab

**Goal:** learn to READ, CHANGE, TEST and DEPLOY a small AI-service codebase. Built for hands-on practice with FastAPI, Azure OpenAI, retrieval, Agent Framework and Azure Container Apps.

## START HERE — Saturday, day 1 (Windows PowerShell, VS Code)

1. Unzip folder and open `ui-agent-readiness` in VS Code.
2. Open **Terminal → New Terminal** at project root.
3. Run (Python 3.12 preferred):

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

If `py -3.12` is not available, install Python 3.12, or replace it with `python` if a compatible Python (3.11+) is present.

4. Open http://127.0.0.1:8000/docs (FastAPI Swagger).
5. Try `GET /health` then `POST /search`, body:

```json
{"question":"Which documents are required for a home loan?"}
```

6. Try `POST /emi`, body:

```json
{"principal":500000,"annual_rate":8,"years":5}
```

7. Stop server with Ctrl+C. Run tests:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

**Good output:** Swagger shows `/health`, `/search`, `/emi`, `/chat`. All tests pass. `/search` is *only a local keyword retrieval baseline* — not yet Azure vector RAG.

## HOW TO READ THE CODE (the first job skill)

For `/search`, follow this exact path:

`HTTP request → app/main.py → Question Pydantic model → retrieve() in app/retrieval.py → data/policies.json → JSON response`

Every time you see `def`, answer: (1) What goes in? (2) What comes out? (3) What could go wrong?

### Day 1 exercises (do **by yourself** first)
- In `app/main.py`, make `/health` return an extra `version: 1` field.
- In `data/policies.json`, add a fourth fake policy with a unique ID.
- Change retrieval limit to `2` in `/search`; predict what happens. Why?
- Intentionally rename `retrieve` to a wrong name; read the stack trace, then fix it.
- Add one pytest assertion that validates your new health field.
- Commit your code: `git init; git add .; git commit -m "Day 1 API basics"` (Git may ask you to configure name/email).

## DAY 2 — Azure OpenAI + retrieval-augmented answers

- Copy `.env.example` to `.env` and use **only personal/explicitly authorized** Azure credentials. Never put keys in code or Git.
- Set `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_CHAT_MODEL` (your **deployment** name), `APP_ACCESS_TOKEN`.
- Run the app again and use `POST /chat` in Swagger with header `X-App-Token`. Swagger may not show custom header input as auth, but will show it as a header field.
- Ask a real question and one unanswerable question. Check that the answer references `POL-xxx` or refuses unsupported claims.
- In `app/llm.py`, explain to yourself system prompt, retrieved context, model and deployment name.

**Important:** retrieval using overlapping keywords + generation is a simple RAG-style demo, **not semantic vector RAG**. No external Azure credentials are needed on Day 1.

## DAY 3 — Azure AI Search

- Understand `document → chunk → embedding → index → query → top-k → LLM`.
- Use official Microsoft vector-search quickstart to build an index **in your own Azure subscription** (can cost money).
- `app/azure_search_demo.py` is a working pattern for *keyword search of an index that already exists*, not an index creator or vector query.
- Run `python -m app.vector_rag_demo` after setting `AZURE_OPENAI_EMBEDDING_MODEL` to an authorized embedding deployment. It performs **real semantic vector ranking** over 3 documents in memory; this is separate from Azure AI Search, which provides durable indexes. Compare local keyword retrieval, in-memory vector retrieval, and Azure AI Search. For Azure AI Search vector indexes follow the official quickstart and then replace `retrieve()`.
- SQL: practice `SELECT`, `WHERE`, `GROUP BY`, `JOIN`, plus `ROW_NUMBER()` vs `DENSE_RANK()` on a small table.

Docs: https://learn.microsoft.com/en-us/azure/search/search-get-started-vector

## DAY 4 — Microsoft Agent Framework

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-optional.txt
.\.venv\Scripts\python.exe -m app.agent_maf
```

- Examine: `Agent → OpenAIChatCompletionClient → instructions → tool(s) → await agent.run()`.
- This agent can **choose** the policy lookup and EMI calculator tools. Inspect actual output for evidence of correct tool use. You can add logging to functions if necessary.
- Exercise: add a third tool, `get_supported_loan_types()`, returning a constant list. Make the agent use it.
- SDK changes quickly; use the [official providers docs](https://learn.microsoft.com/en-us/agent-framework/integrations/by-component/model-providers/openai) if imports differ.

## DAY 5 — LangGraph

```powershell
.\.venv\Scripts\python.exe -m app.graph_demo
```

- Study `State`, `fetch_context` node, `draft_answer` node, `START`, `END` and `compile`.
- This demo is deliberately **NOT a full LLM agent**. Replace `draft_answer()` with Azure LLM call once the graph state is clear.
- Add `validate_answer` node that checks an answer is nonempty. Learn conditional edges after this works.

## DAY 6 — Docker + Azure Container Apps

Optional local Docker practice:

```powershell
docker build -t ui-bank-lab .
docker run --rm -p 8080:8080 ui-bank-lab
```

Open http://127.0.0.1:8080/health.

**Azure CLI:** sign in with your **own / approved** Azure subscription. Deploy the **offline-demo endpoints only** (the .env file is excluded from the image):

```powershell
az login
az account show --output table
az extension add --name containerapp --upgrade
az containerapp up --name ui-bank-lab-demo --resource-group rg-ui-bank-lab --location centralindia --source . --ingress external --target-port 8080
```

Azure CLI may create a container registry, environment and Log Analytics workspace; **billable resources**. Ingress exposes a demonstration API publicly. Never use real banking data or attach an unprotected LLM key to this publicly exposed demo. Confirm you are using an authorized subscription, check subscription quota and region availability.

To delete **the entire resource group created solely for this lab** and prevent ongoing costs:

```powershell
az group delete --name rg-ui-bank-lab --yes
```

**Do not delete a shared resource group.**

Official guide: https://learn.microsoft.com/en-us/azure/container-apps/containerapp-up

## DAY 7 — Debugging / job simulation

Someone on the team asks: "Add support for a new policy, fix poor retrieval results, log response time, and deploy a fix." You should be able to:
1. find the code entrypoint,
2. reproduce bug/request,
3. make one change,
4. run tests,
5. check Swagger,
6. deploy,
7. explain what changed and any limitations.

`azure-pipelines.yml` is a ready-to-read Azure DevOps CI example: on push to main it installs Python dependencies and runs tests. It does not deploy. Set up a pipeline only in a personal or authorized Azure DevOps project.

## Three rules for AI-assisted coding

1. **Read the function before prompting AI.** Predict what it does.
2. **Ask AI for an explanation or a small patch**, not a completely rewritten app.
3. **Run tests and explain the changed lines** before accepting code.

Never send employer source code, API keys, or confidential client data to unapproved AI services. Use approved tools and account boundaries.
