from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
from pymongo import MongoClient
from bson import ObjectId
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this as per your requirements
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"],
)

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017')
db = client['todo_app']
collection = db['todos']

class Todo(BaseModel):
    id: str
    title: str
    done: bool

@app.get("/todos", response_model=List[Todo])
async def read_todos():
    todos = []
    for todo in collection.find():
        todo['id'] = str(todo['_id'])
        todos.append(Todo(**todo))
    return todos

@app.put("/todos/{todo_id}", response_model=Todo)
async def update_todo(todo_id: str, todo: Todo):
    todo_dict = todo.dict()
    del todo_dict['id']  # Remove id field from dict
    result = collection.update_one(
        {'_id': ObjectId(todo_id)},
        {'$set': todo_dict}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Todo not found")
    return Todo(**todo_dict, id=todo_id)

@app.post("/todos", response_model=Todo)
async def create_todo(todo: Todo):
    todo_dict = todo.dict()
    result = collection.insert_one(todo_dict)
    todo_dict['_id'] = result.inserted_id
    return Todo(**todo_dict)

@app.delete("/todos/{todo_id}")
async def delete_todo(todo_id: str):
    result = collection.delete_one({'_id': ObjectId(todo_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Todo not found")
    return {"message": "Todo deleted successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)