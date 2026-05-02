from fastapi import FastAPI



app=FastAPI(
    title="Wiki -Devops knowledge Base",
    description="Rag chatbot for internal Devops documentation",
    version="1.0.0"
)
@app.get("/")
def root():
    return {
        'message':'Wiki API is running'
    }
@app.get("/health")
def health():
    return{
        "status":'ok'
    }