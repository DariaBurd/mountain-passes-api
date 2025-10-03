from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from database import DatabaseManager

app = FastAPI(title="Mountain Passes API")
db = DatabaseManager()


class UserData(BaseModel):
    email: str
    phone: Optional[str] = None
    fam: Optional[str] = None
    name: str
    otc: Optional[str] = None


class CoordsData(BaseModel):
    latitude: str
    longitude: str
    height: str


class LevelData(BaseModel):
    winter: Optional[str] = ""
    summer: Optional[str] = ""
    autumn: Optional[str] = ""
    spring: Optional[str] = ""


class MountainPassData(BaseModel):
    beautyTitle: Optional[str] = ""
    title: str
    other_titles: Optional[str] = ""
    connect: Optional[str] = ""
    add_time: Optional[str] = ""
    user: UserData
    coords: CoordsData
    level: Optional[LevelData] = LevelData()
    images: Optional[Dict[str, Any]] = {}


@app.post("/submitData")
async def submit_data(data: MountainPassData):
    try:
        pass_id = db.add_mountain_pass(data.dict())

        return {
            "status": 200,
            "message": "Заявка успешно отправлена",
            "id": pass_id
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при сохранении данных: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)