# run backend

source .venv/Scripts/activate
uvicorn main:app --reload

python -m uvicorn app.main:app --reload

npm run dev