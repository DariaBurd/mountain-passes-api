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


@app.get("/submitData/{pass_id}")
async def get_pass_by_id(pass_id: int):
    try:
        pass_data = db.get_pass_by_id(pass_id)
        if not pass_data:
            raise HTTPException(
                status_code=404,
                detail="Перевал не найден"
            )

        return {
            "status": 200,
            "data": pass_data
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при получении данных: {str(e)}"
        )


@app.patch("/submitData/{pass_id}")
async def update_pass(pass_id: int, data: MountainPassData):
    try:
        success, message = db.update_mountain_pass(pass_id, data.dict())

        return {
            "state": 1 if success else 0,
            "message": message
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при обновлении данных: {str(e)}"
        )


@app.get("/submitData/")
async def get_passes_by_user_email(user__email: str):
    try:
        passes = db.get_passes_by_user_email(user__email)

        return {
            "status": 200,
            "data": passes,
            "count": len(passes)
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при получении данных: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)