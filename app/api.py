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

config = 'config.yaml'
statsDict = {'targetSpeed' : 0, 'currentSpeed' : 0, 'rpm' : 0, 'dropsAmount' : 0, 'vaccinationsAmount' : 0}
with open(config, "r", encoding='utf8') as file:
    settingsDict = yaml.safe_load(file)


statsDict['targetSpeed'] = 1000
statsDict['currentSpeed'] = 999
statsDict['rpm'] = 200
statsDict['dropsAmount'] = 3
statsDict['vaccinationsAmount'] = 200

@app.get("/api", tags=["root"])
async def read_root()->dict:
    return {"message": "Welcome to the FastAPI application!"}

@app.post("/api/settings_update", tags=["settings"])
async def getSettings(settingsNew: settingsStruct):
    global settingsDict, config
    
    settingsDict['rotDir'] = settingsNew.rotDir
    settingsDict['targetSpeed'] = settingsNew.targetSpeed
    settingsDict['vacPos1'] = settingsNew.vacPos1
    settingsDict['vacPos2'] = settingsNew.vacPos2
    settingsDict['pusher'] = settingsNew.pusher
    try:
        with open(config, 'w', encoding='utf8') as file:
            yaml.dump(settingsDict, file, allow_unicode=True, default_flow_style=False)
    except:
        return {
            "status": "error",
        }
    return {
        "status": "success",
    }

@app.get("/api/settings_update", tags=["settings_upload"])
async def getSettings():
    # global settingsDict
    global config
    with open(config, "r", encoding='utf8') as file:
        settingsDict = yaml.safe_load(file)
    settings = [{ 'id': 0, 'title': 'Направление вращения', 'options': ['По часовой', 'Против часовой'], 'nameSet': 'rotDir', 'value': settingsDict['rotDir'], 'input':'SelectInput'},
        { 'id': 1, 'title': 'Позиция вакцинатора 1', 'options': [2, 3, 4, 5, 6, 7, 8, 9], 'nameSet': 'vacPos1', 'value': settingsDict['vacPos1'], 'input':'SelectInput' },
        { 'id': 2, 'title': 'Позиция вакцинатора 2', 'options': [2, 3, 4, 5, 6, 7, 8, 9], 'nameSet': 'vacPos2', 'value': settingsDict['vacPos2'], 'input':'SelectInput' },
        { 'id': 3, 'title': 'Толкатель', 'options': ['Без сброса', 'Сброс всех', 'Одна вакцина', 'Две вакцины'], 'nameSet': 'pusher', 'value': settingsDict['pusher'], 'input': 'SelectInput' },
        { 'id': 4, 'title': 'Скорость вращения', 'options': [], 'nameSet': 'targetSpeed', 'value': settingsDict['targetSpeed'], 'input':'TextInput' }]
    return JSONResponse(content=settings)

@app.get("/api/stats", tags=["stats"])
async def getSettings(request: Request)->dict:
    global statsDict, settingsDict 
    stats = [{ 'id': 0, 'title': 'Целевая скорость', 'value': settingsDict['targetSpeed'] },
        { 'id': 1, 'title': 'Текущая скорость', 'value': statsDict['currentSpeed'] },
        { 'id': 2, 'title': 'Количество оборотов', 'value': statsDict['rpm'] },
        { 'id': 3, 'title': 'Количество сбросов', 'value': statsDict['dropsAmount'] },
        { 'id': 4, 'title': 'Количество вакцинаций', 'value': statsDict['vaccinationsAmount'] }]
    return JSONResponse(content=stats)

@app.get("/api/state", tags=["state"])
async def getSettings(request: Request)->dict:
    global settingsDict 
    state = { 'startFlag' : settingsDict['startFlag'], 'sessionFlag' : settingsDict['sessionFlag'], }
    return JSONResponse(content=state)

@app.post("/api/state", tags=["state_update"])
async def getSettings(newState: stateStuct)->dict:
    global settingsDict 
    settingsDict['startFlag'] = newState.startFlag
    settingsDict['sessionFlag'] = newState.sessionFlag
    print(newState)
    
    try:
        with open(config, 'w', encoding='utf8') as file:
            yaml.dump(settingsDict, file, allow_unicode=True, default_flow_style=False)
    except:
        return {
            "status": "error",
        }
    return {
        "status": "success",
    }