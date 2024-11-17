python3 -m spacy download en_core_web_sm
python3 -m spacy download es_core_news_sm
python3 -m uvicorn main:app --host 0.0.0.0 --port 8080