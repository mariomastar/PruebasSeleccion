import os
import uuid
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.responses import JSONResponse
import pandas as pd
import psycopg2
from psycopg2.extras import execute_batch
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="API de Empleados")

# Database connection parameters from environment variables
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "pruebas")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

def get_db_connection():
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    return conn

@app.on_event("startup")
async def startup_event():
    # Create table if not exists
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS employees (
                    empleado_id SERIAL PRIMARY KEY,
                    empleado_name VARCHAR(100) NOT NULL,
                    dpto_id INTEGER NOT NULL,
                    dpto_name VARCHAR(100) NOT NULL,
                    puesto_id INTEGER NOT NULL,
                    puesto_name VARCHAR(100) NOT NULL,
                    start_date DATE NOT NULL
                );
            """)
            # Se crea una vista para el reporte de empleados por departamento y puesto.
            cur.execute("""
                CREATE OR REPLACE VIEW employee_report AS
                SELECT 
                    dpto_id,
                    dpto_name,
                    puesto_id,
                    puesto_name,
                    COUNT(*) AS employee_count
                FROM employees
                GROUP BY dpto_id, dpto_name, puesto_id, puesto_name
                ORDER BY dpto_id, puesto_id;
            """)
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Solo se permiten archivos CSV.")
    
    contents = await file.read()
    df = pd.read_csv(pd.io.common.BytesIO(contents))
    
    # Validate required columns
    required_columns = ['empleado_id', 'empleado_name', 'dpto_id', 'dpto_name', 'puesto_id', 'puesto_name', 'start_date']
    if not all(col in df.columns for col in required_columns):
        raise HTTPException(status_code=400, detail=f"CSV must contain columns: {required_columns} - Columns found: {list(df.columns)}")
    
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Use execute_batch for efficient insertion
            data = [tuple(row) for row in df[required_columns].to_numpy()]
            execute_batch(cur, """
                INSERT INTO employees (empleado_id, empleado_name, dpto_id, dpto_name, puesto_id, puesto_name, start_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (empleado_id) DO UPDATE SET
                    empleado_name = EXCLUDED.empleado_name,
                    dpto_id = EXCLUDED.dpto_id,
                    dpto_name = EXCLUDED.dpto_name,
                    puesto_id = EXCLUDED.puesto_id,
                    puesto_name = EXCLUDED.puesto_name,
                    start_date = EXCLUDED.start_date;
            """, data)
        conn.commit()
        return {"message": f"Successfully uploaded {len(df)} records"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.post("/employees/batch")
async def create_employees_batch(employees: list[dict]):
    if not employees:
        raise HTTPException(status_code=400, detail="No employees provided")
    
    # Validate each employee dict has required fields
    required_fields = ['empleado_id', 'empleado_name', 'dpto_id', 'dpto_name', 'puesto_id', 'puesto_name', 'start_date']
    for emp in employees:
        if not all(field in emp for field in required_fields):
            raise HTTPException(status_code=400, detail=f"Each employee must have fields: {required_fields}")
    
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            data = [(emp['empleado_id'], emp['empleado_name'], emp['dpto_id'], emp['dpto_name'], emp['puesto_id'], emp['puesto_name'], emp['start_date']) for emp in employees]
            execute_batch(cur, """
                INSERT INTO employees (empleado_id, empleado_name, dpto_id, dpto_name, puesto_id, puesto_name, start_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (empleado_id) DO UPDATE SET
                    empleado_name = EXCLUDED.empleado_name,
                    dpto_id = EXCLUDED.dpto_id,
                    dpto_name = EXCLUDED.dpto_name,
                    puesto_id = EXCLUDED.puesto_id,
                    puesto_name = EXCLUDED.puesto_name,
                    start_date = EXCLUDED.start_date;
            """, data)
        conn.commit()
        return {"message": f"Successfully created/updated {len(employees)} employees"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.get("/report")
async def get_employee_report():
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT dpto_id, dpto_name, puesto_id, puesto_name, employee_count FROM employee_report ORDER BY dpto_id, puesto_id")
            rows = cur.fetchall()
            report = [{"dpto_id": row[0], "dpto_name": row[1], "puesto_id": row[2], "puesto_name": row[3], "employee_count": row[4]} for row in rows]
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

# Optional: Get all employees with pagination
@app.get("/employees")
async def get_employees(skip: int = 0, limit: int = 100):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT empleado_id, empleado_name, dpto_id, dpto_name, puesto_id, puesto_name, start_date FROM employees ORDER BY empleado_id LIMIT %s OFFSET %s", (limit, skip))
            rows = cur.fetchall()
            employees = [{"empleado_id": row[0], "empleado_name": row[1], "dpto_id": row[2], "dpto_name": row[3], "puesto_id": row[4], "puesto_name": row[5], "start_date": row[6].isoformat() if row[6] else None} for row in rows]
        return employees
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

# Optional: Get a single employee by ID
@app.get("/employees/{empleado_id}")
async def get_employee(empleado_id: int):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT empleado_id, empleado_name, dpto_id, dpto_name, puesto_id, puesto_name, start_date FROM employees WHERE empleado_id = %s", (empleado_id,))
            row = cur.fetchone()
            if row is None:
                raise HTTPException(status_code=404, detail="Employee not found")
            employee = {"empleado_id": row[0], "empleado_name": row[1], "dpto_id": row[2], "dpto_name": row[3], "puesto_id": row[4], "puesto_name": row[5], "start_date": row[6].isoformat() if row[6] else None}
        return employee
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)