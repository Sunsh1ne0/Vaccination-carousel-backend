from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import yaml
import pathlib
from .db_communication import connect_to_db, init_tables, update_settings, update_stats, remove_old_stats, drop_tables, read_stats, read_settings
import time

app = FastAPI()

firstStart = True

origins = [
    "*"
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
    targetSpeed: float
    vacPos1: int
    vacPos2: int
    pusher: str

class statsStuct(BaseModel):
    targetSpeed: float
    currentSpeed: int
    rpm: int
    dropsAmount: int
    vaccinationsAmount: int

class stateStuct(BaseModel):
    startFlag: bool
    sessionFlag: bool

def init_carousel_db():
    while True:
        if connect_to_db():
            time.sleep(1)
        else:
            print("CONNECTED TO DB")
            break
    init_tables()
    
    tempList = read_settings()
    if len(tempList) == 0:
        fullDict['rotDir'] = 'Counterclockwise'
        fullDict['targetSpeed'] = 1.8
        fullDict['vacPos1'] = 2
        fullDict['vacPos2'] = 3
        fullDict['pusher'] = 'Drop all'
    else:
        tempList = tempList[0]
        fullDict['rotDir'] = tempList[2]
        fullDict['targetSpeed'] = tempList[3]
        fullDict['vacPos1'] = tempList[4]
        fullDict['vacPos2'] = tempList[5]
        fullDict['pusher'] = tempList[6]

    tempList = read_stats()
    if len(tempList) == 0:
        fullDict['targetSpeed'] = 1.8
        fullDict['currentSpeed'] = 0
        fullDict['rotationAmount'] = 0
        fullDict['dropsAmount'] = 0
        fullDict['vaccinationAmount1'] = 0
        fullDict['vaccinationAmount2'] = 0
        fullDict['startFlag'] = False
        fullDict['sessionFlag'] = False
    else:
        tempList = tempList[0]
        fullDict['currentSpeed'] = tempList[2]
        fullDict['dropsAmount'] = tempList[3]
        fullDict['rotationAmount'] = tempList[4]
        fullDict['vaccinationAmount1'] = tempList[5]
        fullDict['vaccinationAmount2'] = tempList[6]
        fullDict['startFlag'] = False
        fullDict['sessionFlag'] = tempList[8]

fullDict = {}
init_carousel_db()

@app.get("/api", tags=["root"])
async def read_root()->dict:
    return {"message": "Welcome to the FastAPI application!"}

@app.post("/api/settings_update", tags=["settings"])
async def postSettings(settingsNew: settingsStruct):
    global fullDict
    fullDict['rotDir'] = 'Counterclockwise' if settingsNew.rotDir == 'Против часовой' else 'Clockwise'
    fullDict['targetSpeed'] = settingsNew.targetSpeed
    fullDict['vacPos1'] = settingsNew.vacPos1
    fullDict['vacPos2'] = settingsNew.vacPos2
    fullDict['pusher'] = 'Drop all' if settingsNew.pusher == 'Сброс всех' else ('Drop none' if settingsNew.pusher == 'Без сброса' else ('One vaccine' if settingsNew.pusher == 'Одна вакцина' else 'Two vaccines'))
    try:
        print(update_settings(fullDict['rotDir'], fullDict['targetSpeed'], fullDict['vacPos1'], fullDict['vacPos2'], fullDict['pusher']))
    # try:
    #     with open(config, 'w', encoding='utf8') as file:
    #         yaml.dump(fullDict, file, allow_unicode=True, default_flow_style=False)
    except:
        return {
            "status": "error",
        }
    return {
        "status": "success",
    }

@app.get("/api/settings_update", tags=["settings_upload"])
async def getSettings():
    # loadConfig()
    global fullDict
    tempList = read_settings()
    # if len(tempList) == 0:
    #     fullDict['rotDir'] = 'Против часовой'
    #     fullDict['targetSpeed'] = 1.8
    #     fullDict['vacPos1'] = 2
    #     fullDict['vacPos2'] = 3
    #     fullDict['pusher'] = 'Сброс всех'
    # else:
    tempList = tempList[0]
    fullDict['rotDir'] = tempList[2]
    fullDict['targetSpeed'] = tempList[3]
    fullDict['vacPos1'] = tempList[4]
    fullDict['vacPos2'] = tempList[5]
    fullDict['pusher'] = tempList[6]
    
    settings = [{ 'id': 0, 'title': 'Направление вращения', 'options': ['По часовой', 'Против часовой'], 'nameSet': 'rotDir', 'value': 'Против часовой' if fullDict['rotDir'] == 'Counterclockwise' else 'По часовой', 'input':'SelectInput'},
        { 'id': 1, 'title': 'Позиция вакцинатора 1', 'options': [2, 3, 4, 5, 6, 7, 8, 9], 'nameSet': 'vacPos1', 'value': fullDict['vacPos1'], 'input':'SelectInput' },
        { 'id': 2, 'title': 'Позиция вакцинатора 2', 'options': [2, 3, 4, 5, 6, 7, 8, 9], 'nameSet': 'vacPos2', 'value': fullDict['vacPos2'], 'input':'SelectInput' },
        { 'id': 3, 'title': 'Толкатель', 'options': ['Без сброса', 'Сброс всех', 'Одна вакцина', 'Две вакцины'], 'nameSet': 'pusher', 'value': 'Сброс всех' if fullDict['pusher'] == 'Drop all' else ('Без сброса' if fullDict['pusher'] == 'Drop none' else ('Одна вакцина' if fullDict['pusher'] == 'One vaccine' else 'Две вакцины')), 'input': 'SelectInput' },
        { 'id': 4, 'title': 'Скорость вращения', 'options': [], 'nameSet': 'targetSpeed', 'value': fullDict['targetSpeed'], 'input':'SliderInput' }]
    return JSONResponse(content=settings)

@app.get("/api/stats", tags=["stats"])
async def getStats(request: Request)->dict:
    global fullDict
    # loadConfig()
    tempList = read_stats()
    if len(tempList) == 0:
        fullDict['targetSpeed'] = 1.8
        fullDict['currentSpeed'] = 0
        fullDict['rotationAmount'] = 0
        fullDict['dropsAmount'] = 0
        fullDict['vaccinationAmount1'] = 0
        fullDict['vaccinationAmount2'] = 0
        fullDict['startFlag'] = False
        fullDict['sessionFlag'] = False
    else:
        tempList = tempList[0]
        fullDict['currentSpeed'] = tempList[2]
        fullDict['dropsAmount'] = tempList[3]
        fullDict['rotationAmount'] = tempList[4]
        fullDict['vaccinationAmount1'] = tempList[5]
        fullDict['vaccinationAmount2'] = tempList[6]
        fullDict['startFlag'] = tempList[7]
        fullDict['sessionFlag'] = tempList[8]
    stats = [{ 'id': 0, 'title': 'Целевая скорость', 'value': fullDict['targetSpeed'] },
        { 'id': 1, 'title': 'Текущая скорость', 'value': fullDict['currentSpeed'] },
        { 'id': 2, 'title': 'Количество оборотов', 'value': fullDict['rotationAmount'] },
        { 'id': 3, 'title': 'Количество сбросов', 'value': fullDict['dropsAmount'] },
        { 'id': 4, 'title': 'Количество вакцинаций 1', 'value': fullDict['vaccinationAmount1'] },
        { 'id': 5, 'title': 'Количество вакцинаций 2', 'value': fullDict['vaccinationAmount2'] }]
    return JSONResponse(content=stats)

@app.get("/api/state", tags=["state"])
async def getState(request: Request)->dict:
    global fullDict
    state = { 'startFlag' : fullDict['startFlag'], 'sessionFlag' : fullDict['sessionFlag'], }
    return JSONResponse(content=state)

@app.post("/api/state", tags=["state_update"])
async def postState(newState: stateStuct)->dict:
    global fullDict 
    print(newState)
    fullDict['startFlag'] = newState.startFlag
    fullDict['sessionFlag'] = newState.sessionFlag
    
    try:
        # with open(config, 'w', encoding='utf8') as file:
        #     yaml.dump(fullDict, file, allow_unicode=True, default_flow_style=False)
        print(fullDict)
        update_stats(fullDict['currentSpeed'], fullDict['dropsAmount'], fullDict['rotationAmount'], fullDict['vaccinationAmount1'], fullDict['vaccinationAmount2'], fullDict['startFlag'], fullDict['sessionFlag'] )

    except:
        return {
            "status": "error",
        }
    return {
        "status": "success",
    }