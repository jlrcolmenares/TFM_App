from typing import Optional
from fastapi import FastAPI, Query

from datetime import datetime # dudo que esto se tenga que hacer aquí

app = FastAPI()

@app.get("/")
def read_root(): 
    return {"Hello": "World"}

@app.get("/dates/")
async def read_item(
    begin: str = Query(
        None, 
        min_length = 8,
        regex="^(20)\d\d[-](0[1-9]|1[012])[-](0[1-9]|[12][0-9]|3[01])$"
        )):
            results = {"response": f"Formato de fecha inválido"}
            if begin: 
                Y, m, d = begin.split("-")
                start_date = datetime( int(Y), int(m), int(d)).strftime("%d/%m/%Y")
                results = {"response": f"la fecha de inicio es {start_date}"}
            return results 


# PARA VALIDAR QUE EL SRING DE ENTRADA SEA UNA FECHA SE PUEDEN UTILIZAR EXPRESIONES REGULARES

