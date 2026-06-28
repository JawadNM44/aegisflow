# Contributing to AEGISFLOW

1. Fork the repository
2. Create a feature branch: `git checkout -b feat/my-feature`
3. Commit changes: `git commit -m "feat: add my feature <why and how>"`
4. Push: `git push origin feat/my-feature`
5. Open a Pull Request

## Development

- Backend: `cd backend && pip install -r requirements.txt && uvicorn app.main:app --reload`
- Frontend: `cd frontend && npm install && npm run dev`
- Tests: `cd backend && python -m pytest tests/ -v`
