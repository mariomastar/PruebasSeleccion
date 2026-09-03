import pandas as pd
import numpy as np
from datetime import datetime

dptos_data = { 
    "depto_id": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
    "depto_name": ["Compras", "Ventas", "Inventario", "Tecnología", "Recursos Humanos", "Finanzas", "Marketing", "Logística", "Producción", "Calidad", "Atención al Cliente", "Desarrollo de Producto", "Legal", "Seguridad", "Mantenimiento", "Planificación Estratégica", "Relaciones Públicas", "Investigación y Desarrollo", "Sistemas de Información", "Auditoría"] 
} 

puestos_data = { 
    "puesto_id": [101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120],
    "puesto_name": ["Analista", "Auxiliar", "Cordinador", "Gerente", "Director", "Supervisor", "Asistente", "Especialista", "Consultor", "Jefe de Proyecto", "Encargado", "Administrador", "Técnico", "Representante de Ventas", "Diseñador", "Programador", "Ingeniero", "Contador", "Abogado", "Médico"] 
} 

nombres_data =   { 
    "nombre_id": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40],
    "nombre": ["Pedro", "Jose", "Juan", "Ana", "Lucia", "Doris", "Manuel", "Camilo", "Samuel", "Jenny", "Mario", "Stella", "Jorge", "Sofia", "Valentina", "Camila", "Isabella", "Gabriel", "Sebastian", "Diego", "Emilia", "Julian", "Martina", "Daniela", "Alejandro", "Victoria", "Andres", "Carolina", "Nicolas", "Mariana", "Santiago", "Paula", "Felipe", "Catalina", "David", "Laura", "Miguel", "Isabel", "Javier", "Sara"]
}

apellido_data = {
    "apellido_id": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40],
    "apellido": ["Sanchez", "Vera", "Gonzalez", "Lopez", "Arango", "Perez", "Rubio", "Gomez", "Diaz", "Aragon", "Cruz", "Chaves", "Rojas", "Mora", "Castro", "Alvarado", "Hernandez", "Ramirez", "Torres", "Vargas", "Jimenez", "Ortega", "Salazar", "Pineda", "Mendoza", "Cabrera", "Rincon", "Cardenas", "Montoya", "Serrano", "Quintero", "Valencia", "Cortes", "Palacios", "Figueroa", "Camacho", "Rincon", "Pacheco"]
}
np.random.seed(0)

dpto_names = dict(zip(dptos_data['depto_id'], dptos_data['depto_name']))
puesto_names = dict(zip(puestos_data['puesto_id'], puestos_data['puesto_name']))
dpto_ids = np.random.choice(dptos_data['depto_id'], 100)
puesto_ids = np.random.choice(puestos_data['puesto_id'], 100)

empleados_data = { 
    "empleado_id": np.arange(1, 101), 
    "empleado_name": [f"{np.random.choice(nombres_data['nombre'])} {np.random.choice(apellido_data['apellido'])}" for _ in range(100)], 
    "dpto_id": dpto_ids,
    "dpto_name": [dpto_names[dpto_id] for dpto_id in dpto_ids],
    "puesto_id": puesto_ids,
    "puesto_name": [puesto_names[puesto_id] for puesto_id in puesto_ids],
    "start_date": [datetime(2021, np.random.randint(1, 13), np.random.randint(1, 29)) for _ in range(100)] 
}

empleados_df = pd.DataFrame(empleados_data)
empleados_df.to_csv('datos.csv', index=False, encoding='utf-8')

print(empleados_df.head())