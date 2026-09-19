# HACK-HERE-HACKATHON + Featherless AI

## 1. Setup OpenCode provider
`opencode.json` defines a custom `featherless` provider (OpenAI-compatible):
- baseURL `https://api.featherless.ai/v1`
- env `FEATHERLESS_API_KEY`
- models: `featherless/qwen3-coder-480b` (default), `featherless/qwen25-coder-32b`, `featherless/qwen3-coder-30b`

Set key for current PowerShell session:
```powershell
$env:FEATHERLESS_API_KEY="rc_xxx"
opencode /models   # select featherless/...
```

Or persist for user:
```powershell
setx FEATHERLESS_API_KEY "rc_xxx"
```

## 2. Backend usage
```powershell
copy .env.example .env
# edit .env with real key
pip install openai python-dotenv
python backend/featherless_client.py
```

See `backend/featherless_client.py:1` for reusable `chat()` + `list_models()`.
