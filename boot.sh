prisma db push && prisma generate && prisma py fetch
spacy download en_core_web_sm
spacy download es_core_news_sm
uvicorn main:app --host 0.0.0.0 --port 8080 --reload