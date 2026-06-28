.PHONY: install test run clean
install:
	cd backend && pip install -r requirements.txt
	cd frontend && npm install

run:
	./start.sh

test:
	cd backend && python -m pytest tests/

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null; true
	rm -rf frontend/.next frontend/node_modules backend/venv

