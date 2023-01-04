import asyncio
import json
import os
import uuid
import subprocess

from fastapi import FastAPI, Body, File, UploadFile, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel, Field
from bson import ObjectId
from pymongo import MongoClient
import motor.motor_asyncio
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
import warnings
import sys
import uvicorn

# url = os.getenv("MONGODB_URL", "mongodb+srv://siuklee:tldnr4655@cluster0.hukgpba.mongodb.net/?retryWrites=true&w=majority")
# uri = os.getenv("MONGODB_URI", "<NOTSET>")
# uri_srv = os.getenv("MONGODB_URI_SRV", "<NOTSET>")
#
# if (uri == "<NOTSET>") and (uri_srv == "<NOTSET>"):
#     warnings.warn("Did not detect MONGODB_URI or MONGODB_URI_SRV environment variables.")
#     if url == "<NOTSET>":
#         warnings.warn("Did not detect MONGODB_URL evironment variables.")
#         warnings.warn("Please set these and relaunc the app.")
#         warnings.warn(f"MONGODB_URI={uri}, MONGODB_URI_SRV={uri_srv}, MONOGDB_URL={url}")
#         sys.exit(1)
#     else:
#         # Fall back to URL
#         uri = url
#
# if uri_srv == "<NOTSET>":
#     warnings.warn("MONGODB_URI_SRV was not set.")
#     uri = uri_srv
#
# user = os.getenv("MONGODB_USERNAME", "siuklee")
# pwd = os.getenv("MONGODB_PASSWORD", "tldnr4655")
# pwd_redact = "<NOTSET>" if (pwd == "<NOTSET>") else "*REDACTED*"
# print(f"uri:{uri}\nuri_srv:{uri_srv}\nuser:{user}\npwd:{pwd_redact}")


# class DataBase:
#     client: AsyncIOMotorClient = None
#     petDB = None
#
#
# db = DataBase()


# async def connect_to_mongo():
#     print("connecting to mongo...")
#
#     if not "<NOTSET>" in {user, pwd}:
#         try:
#             db.client = motor.motor_asyncio.AsyncIOMotorClient(uri_srv, username=user, password=pwd)
#         except Exception as err:
#             warnings.warn(f"ERROR: {err}")
#             if not uri == "<NOTSET>":
#                 warnings.warn(f"srv connect error, attepting with MONGODB_URI:{uri}")
#                 client = motor.motor_asyncio.AsyncIOMotorClient(uri, username=user, password=pwd)
#     else:
#         warnings.warn("MONGODB_USERNAME or MONGODB_PASSWORD not set, using connection string only.")
#         try:
#             db.client = motor.motor_asyncio.AsyncIOMotorClient(uri_srv)
#         except Exception as err:
#             warnings.warn(f"ERROR: {err}")
#             if not uri == "<NOTSET>":
#                 warnings.warn(f"srv connect error, attepting with MONGODB_URI:{uri}")
#                 client = motor.motor_asyncio.AsyncIOMotorClient(uri)
#     # get a collection
#     # Format db.<database_name>.<collection_name>
#     # db.crash = db.client.crash
#     db.database = db.client['client']
#     print("connected to tancho_ci_db/pet")
#
#
# async def close_mongo_connection():
#     print("closing connection...")
#     db.database.close()
#     print("closed connection")

async def schedule_symbolicate():
    loop = asyncio.get_event_loop()
    loop.create_task(symbolicate())

async def symbolicate():
    while True:
        print("symbolicate")

        client = MongoClient(
            "mongodb+srv://siuklee:tldnr4655@cluster0.hukgpba.mongodb.net/?retryWrites=true&w=majority")

        db = client['client']
        collection = db['crash']
        notSymbolicatedCrashReport = collection.find_one({"isSymbolicated": False})

        filename = notSymbolicatedCrashReport["filename"]

        UPLOAD_DIR = "./crashreport"  # 저장할 서버 경로

        # out_file = open(os.path.join(UPLOAD_DIR, filename), "wb")
        # subprocess.call("./retrace.sh %s" % filename, shell=True)
        # os.system('sh retrace.sh %s' % filename)
        return_value = os.popen('sh retrace.sh %s' % filename).read()
        print("notSymbolicatedCrashReport")

        SYMBOLICATED_DIR = "./symbolicated_crashreport"  # 저장할 서버 경로
        with open(os.path.join(SYMBOLICATED_DIR, filename), "wb") as fp:
            fp.write(bytes(return_value, 'utf-8'))  # 서버 로컬 스토리지에 저장 (쓰기)

        # jsoncrashreport = {'uuid': uniqueIdentifier, 'filename': filename, 'isSymbolicated': False}
        # crashreport = CrashReportModel(**jsoncrashreport)
        # json_crashreport = jsonable_encoder(crashreport)
        # collection.insert_one(json_crashreport)

        client.close()

        await asyncio.sleep(60)

app = FastAPI()
app.add_event_handler("startup", schedule_symbolicate)

origins = [
    "http://localhost:8086",
    "http://127.0.0.1:8086"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# app.add_event_handler("startup", connect_to_mongo)
# app.add_event_handler("shutdown", close_mongo_connection)


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class CrashReportModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    uuid: str
    filename: str
    isSymbolicated: bool = False

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "uuid": "test1111",
                "filename": "test1111",
                "isSymbolicated": False
            }
        }


@app.get("/")
async def root():
    return {"message": "Hello World"}


# @app.post("/uploadReport", )
# async def report(crashReport: CrashReportModel = Body(...)):
#     # crashContent = await file.read()
#
#     # collection = db.database['crash']
#     # jsonCrashReport = jsonable_encoder(crashReport)
#     # new_crashReport = await collection.insert_one(jsonCrashReport)
#
#     client = MongoClient(
#         "mongodb+srv://siuklee:tldnr4655@cluster0.hukgpba.mongodb.net/?retryWrites=true&w=majority")
#
#     db = client['client']
#     collection = db['crash']
#     json_crashreport = jsonable_encoder(crashReport)
#     new_crashreport = collection.insert_one(json_crashreport)
#     created_crash = collection.find_one({"_id": new_crashreport.inserted_id})
#
#     client.close()
#     return JSONResponse(
#         content={"code": "0", "message": "success", "content": created_crash},
#         status_code=200
#     )


@app.post("/upload")
async def upload(file: UploadFile):
    UPLOAD_DIR = "./crashreport"  # 저장할 서버 경로

    content = await file.read()
    # filename = f"{str(uuid.uuid4())}.xcrash"  #uuid로 유니크한 파일명으로 변경
    uniqueIdentifier = str(uuid.uuid4())
    filename = uniqueIdentifier + "_" + file.filename
    with open(os.path.join(UPLOAD_DIR, filename), "wb") as fp:
        fp.write(content)  # 서버 로컬 스토리지에 저장 (쓰기)

    client = MongoClient(
        "mongodb+srv://siuklee:tldnr4655@cluster0.hukgpba.mongodb.net/?retryWrites=true&w=majority")

    db = client['client']
    collection = db['crash']
    jsoncrashreport = {'uuid': uniqueIdentifier, 'filename': filename, 'isSymbolicated': False}
    crashreport = CrashReportModel(**jsoncrashreport)
    json_crashreport = jsonable_encoder(crashreport)
    collection.insert_one(json_crashreport)

    client.close()

    return JSONResponse(
        content={"code": "0", "message": "success"},
        status_code=200
    )

@app.get("/crashreport")
async def getCrashReport():
    client = MongoClient(
        "mongodb+srv://siuklee:tldnr4655@cluster0.hukgpba.mongodb.net/?retryWrites=true&w=majority")

    db = client['client']
    collection = db['crash']
    crashreports = list(collection.find())
    return JSONResponse(
        content={"code": "0", "message": "success", "crashreports": crashreports},
        status_code=200
    )

