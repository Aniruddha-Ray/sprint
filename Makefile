setup:
	python -m pip install -r requirements.txt

# Full pipeline: raw Excel -> SQLite -> financial ratios
run:
	python -m src.etl.market_data
	python -m src.etl.validator
	python -m src.etl.load_database
	python -m src.analytics.ratio_engine
	python -m src.etl.verify_database

api:
	uvicorn src.api.main:app --reload

dashboard:
	streamlit run src/dashboard/app.py

test:
	python -m pytest tests/

format:
	black src tests

lint:
	flake8 src

clean:
	python -c "import pathlib, shutil; [shutil.rmtree(p) for p in pathlib.Path(\".\").rglob(\"__pycache__\")]"
