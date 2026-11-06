from fastapi import FastAPI
import uvicorn
import aiomysql

# Настройки подключения — вынеси в переменные окружения для продакшена
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "db": "1",
}

app = FastAPI()

# Пул соединений создаётся один раз при старте
@app.on_event("startup")
async def startup():
    app.state.pool = await aiomysql.create_pool(
        minsize=1,
        maxsize=5,
        autocommit=True,
        **DB_CONFIG,
    )

@app.on_event("shutdown")
async def shutdown():
    app.state.pool.close()
    await app.state.pool.wait_closed()

@app.get("/api/orders")
async def get_orders():
    async with app.state.pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("SELECT id, name, amount, desciption FROM orders")
            rows = await cur.fetchall()
    return rows

if __name__ == "__main__":
    uvicorn.run("api:app", host="127.0.0.1", port=1323)
