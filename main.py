from fastapi import FastAPI

# Initialize the FastAPI application instance
app = FastAPI()

# Define a simple GET endpoint at the root URL
@app.get("/")
def read_root():
    return {"status": "success", "message": "Hello World"}
