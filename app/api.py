from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import yaml
import os

app = FastAPI()

origins = [
    # "http://localhost",
    "*"
    # "http://localhost:80",
    # "http://localhost:3000",
    # "localhost:3000",
    # "localhost"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class settingsStruct(BaseModel):
    rotDir: str
    targetSpeed: int
    vacPos1: int
    vacPos2: int
    pusher: str

class statsStuct(BaseModel):
    targetSpeed: int
    currentSpeed: int
    rpm: int
    dropsAmount: int
    vaccinationsAmount: int

class stateStuct(BaseModel):
    startFlag: bool
    sessionFlag: bool

def loadConfig():
    global settingsDict, config, statsDict, fullDict
    with open(config, "r", encoding='utf8') as file:
        fullDict = yaml.safe_load(file)


config = 'config.yaml'
fullDict = {}
loadConfig()

@app.get("/api", tags=["root"])
async def read_root()->dict:
    return {"message": "Welcome to the FastAPI application!"}

@app.post("/api/settings_update", tags=["settings"])
async def getSettings(settingsNew: settingsStruct):
    global fullDict, config
    
    fullDict['rotDir'] = settingsNew.rotDir
    fullDict['targetSpeed'] = settingsNew.targetSpeed
    fullDict['vacPos1'] = settingsNew.vacPos1
    fullDict['vacPos2'] = settingsNew.vacPos2
    fullDict['pusher'] = settingsNew.pusher
    try:
        with open(config, 'w', encoding='utf8') as file:
            yaml.dump(fullDict, file, allow_unicode=True, default_flow_style=False)
    except:
        return {
            "status": "error",
        }
    return {
        "status": "success",
    }

@app.get("/api/settings_update", tags=["settings_upload"])
async def getSettings():
    loadConfig()
    settings = [{ 'id': 0, 'title': 'Направление вращения', 'options': ['По часовой', 'Против часовой'], 'nameSet': 'rotDir', 'value': fullDict['rotDir'], 'input':'SelectInput'},
        { 'id': 1, 'title': 'Позиция вакцинатора 1', 'options': [2, 3, 4, 5, 6, 7, 8, 9], 'nameSet': 'vacPos1', 'value': fullDict['vacPos1'], 'input':'SelectInput' },
        { 'id': 2, 'title': 'Позиция вакцинатора 2', 'options': [2, 3, 4, 5, 6, 7, 8, 9], 'nameSet': 'vacPos2', 'value': fullDict['vacPos2'], 'input':'SelectInput' },
        { 'id': 3, 'title': 'Толкатель', 'options': ['Без сброса', 'Сброс всех', 'Одна вакцина', 'Две вакцины'], 'nameSet': 'pusher', 'value': fullDict['pusher'], 'input': 'SelectInput' },
        { 'id': 4, 'title': 'Скорость вращения', 'options': [], 'nameSet': 'targetSpeed', 'value': fullDict['targetSpeed'], 'input':'TextInput' }]
    return JSONResponse(content=settings)

@app.get("/api/stats", tags=["stats"])
async def getSettings(request: Request)->dict:
    global fullDict
    stats = [{ 'id': 0, 'title': 'Целевая скорость', 'value': fullDict['targetSpeed'] },
        { 'id': 1, 'title': 'Текущая скорость', 'value': fullDict['currentSpeed'] },
        { 'id': 2, 'title': 'Количество оборотов', 'value': fullDict['rotationAmount'] },
        { 'id': 3, 'title': 'Количество сбросов', 'value': fullDict['dropsAmount'] },
        { 'id': 4, 'title': 'Количество вакцинаций 1', 'value': fullDict['vaccinationAmount1'] },
        { 'id': 5, 'title': 'Количество вакцинаций 2', 'value': fullDict['vaccinationAmount2'] }]
    return JSONResponse(content=stats)

@app.get("/api/state", tags=["state"])
async def getSettings(request: Request)->dict:
    global fullDict 
    state = { 'startFlag' : fullDict['startFlag'], 'sessionFlag' : fullDict['sessionFlag'], }
    return JSONResponse(content=state)

@app.post("/api/state", tags=["state_update"])
async def getSettings(newState: stateStuct)->dict:
    global fullDict 
    fullDict['startFlag'] = newState.startFlag
    fullDict['sessionFlag'] = newState.sessionFlag
    
    try:
        with open(config, 'w', encoding='utf8') as file:
            yaml.dump(fullDict, file, allow_unicode=True, default_flow_style=False)
    except:
        return {
            "status": "error",
        }
    return {
        "status": "success",
    }