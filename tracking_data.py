from google.cloud import bigquery
import os


# Ruta absoluta al archivo de credenciales de la cuenta de servicio, siempre relativa a este archivo
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GOOGLE_CREDENTIALS_PATH = os.path.join(BASE_DIR, "credentials", "datos-clientes-441216-e0f1e3740f41.json")

def consultar_estado(tracking):
    client = bigquery.Client.from_service_account_json(GOOGLE_CREDENTIALS_PATH)
    query = """
        SELECT
            primary_client_id,
            tracking_number,
            client,
            Destino,
            Depto_Destino,
            Actual_Normal_Status,
            Status_Date,
            FS,
            Empleado,
            Carrier,
            Almacen_Actual,
            master,
            customer_mobile_number,
            pais,
            nombre,
            direccion,
            Origen_City,
            Destino_City
        FROM `datos-clientes-441216.Servicio_Cliente.Status`
        WHERE tracking_number = @tracking
        LIMIT 1
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("tracking", "STRING", tracking)
        ]
    )
    query_job = client.query(query, job_config=job_config)
    result = list(query_job)
    if not result:
        return None
    row = result[0]
    return {
        "primary_client_id": row.get("primary_client_id"),
        "tracking_number": row.get("tracking_number"),
        "client": row.get("client"),
        "destino": row.get("Destino"),
        "depto_destino": row.get("Depto_Destino"),
        "estado": row.get("Actual_Normal_Status"),
        "fecha_estado": row.get("Status_Date"),
        "fs": row.get("FS"),
        "empleado": row.get("Empleado"),
        "carrier": row.get("Carrier"),
        "almacen_actual": row.get("Almacen_Actual"),
        "master": row.get("master"),
        "customer_mobile_number": row.get("customer_mobile_number"),
        "pais": row.get("pais"),
        "nombre": row.get("nombre"),
        "direccion": row.get("direccion"),
        "origen_city": row.get("Origen_City"),  # ✅ NUEVO CAMPO
        "destino_city": row.get("Destino_City"),  # ✅ NUEVO CAMPO
    }