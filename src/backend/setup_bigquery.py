import os
import random
import uuid
from datetime import datetime, timedelta
from google.cloud import bigquery
from google.api_core.exceptions import Conflict

# --- Configuration ---
# Replace with your actual project ID or set the GCP_PROJECT_ID environment variable.
PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "YOUR_PROJECT_ID")
DATASET_ID = "feria_sevilla_2025"

def get_client():
    """Initializes the BigQuery client."""
    if PROJECT_ID == "YOUR_PROJECT_ID":
        print("⚠️ Warning: Using default credentials (ADC) as PROJECT_ID is not set.")
        return bigquery.Client()
    return bigquery.Client(project=PROJECT_ID)

def create_dataset_if_not_exists(client):
    """Creates the dataset if it doesn't exist."""
    dataset_ref = client.dataset(DATASET_ID)
    try:
        client.get_dataset(dataset_ref)
        print(f"✅ Dataset {DATASET_ID} already exists.")
    except Exception:
        dataset = bigquery.Dataset(dataset_ref)
        dataset.location = "EU" # Standard for Sevilla context, or US if preferred
        try:
            client.create_dataset(dataset)
            print(f"✅ Dataset {DATASET_ID} created.")
        except Conflict:
            print(f"✅ Dataset {DATASET_ID} already exists (Conflict).")

def create_table_if_not_exists(client, table_id, schema):
    """Creates a table if it doesn't exist."""
    table_ref = client.dataset(DATASET_ID).table(table_id)
    try:
        client.get_table(table_ref)
        print(f"✅ Table {table_id} already exists.")
    except Exception:
        table = bigquery.Table(table_ref, schema=schema)
        client.create_table(table)
        print(f"✅ Table {table_id} created.")

def generate_afluencia_data(client):
    """Generates mock data for afluencia_casetas."""
    table_id = "afluencia_casetas"
    schema = [
        bigquery.SchemaField("id_caseta", "STRING"),
        bigquery.SchemaField("nombre_caseta", "STRING"),
        bigquery.SchemaField("tipo_caseta", "STRING"),
        bigquery.SchemaField("timestamp", "TIMESTAMP"),
        bigquery.SchemaField("numero_visitantes", "INTEGER"),
    ]
    create_table_if_not_exists(client, table_id, schema)

    # Check if table has data
    table_ref = client.dataset(DATASET_ID).table(table_id)
    table = client.get_table(table_ref)
    if table.num_rows > 0:
        print(f"ℹ️ Table {table_id} already has data ({table.num_rows} rows). Skipping generation.")
        return

    print(f"🚀 Generating data for {table_id}...")
    rows_to_insert = []
    casetas = [
        ("C01", "A Ver Si Llego", "privada"),
        ("C02", "Aguanta Como Puedas", "privada"),
        ("C03", "Aquí Mismo", "privada"),
        ("C04", "Casi Caemos", "privada"),
        ("C05", "El Cuadro", "privada"),
        ("C06", "El Penúltimo Trago", "privada"),
        ("C07", "El Último Varal", "privada"),
        ("C08", "Esto Se Avisa", "privada"),
        ("C09", "La Cachava", "privada"),
        ("C10", "La De Clavo", "privada"),
        ("C11", "La Penúltima y nos vamos", "privada"),
        ("C12", "La Rebotica", "privada"),
        ("C13", "Los Que Faltaban", "privada"),
        ("C14", "Los Tardíos", "privada"),
        ("C15", "No Juegues Con Fuego", "privada"),
        ("C16", "No Ni Na", "privada"),
        ("C17", "Pa Qué Más", "privada"),
        ("C18", "Poquito a Poco", "privada"),
        ("C19", "Se Te Ve El Plumero", "privada"),
        ("C20", "Vértigo", "privada"),
        ("C21", "La Pajarera", "privada"),
        ("C22", "La Castañuela", "privada"),
        ("C23", "El Cachirulo", "privada"),
        ("C24", "El Farol", "privada"),
        ("C25", "El Ruedo", "privada"),
        ("C26", "La Cigarrera", "privada"),
        ("C27", "La Esquina", "privada"),
        ("C28", "Los Cabales", "privada"),
        ("C29", "El Olivo", "privada"),
        ("C30", "La Parrala", "privada"),
        ("C31", "La Giralda", "privada"),
        ("C32", "El Mantoncillo", "privada"),
        ("C33", "La Espuela", "privada"),
        ("C34", "El Azahar", "privada"),
        ("C35", "La Reja", "privada"),
        ("C36", "El Redoble", "privada"),
        ("C37", "La Marimorena", "privada"),
        ("C38", "El Patio", "privada"),
        ("C39", "La Revirá", "privada"),
        ("C40", "Los del Rincón", "privada"),
        ("C41", "A.D. Nervión", "privada"),
        ("C42", "Asoc. And. de Esclerosis Múltiple", "privada"),
        ("C43", "Círculo de Labradores", "privada"),
        ("C44", "Círculo Mercantil e Industrial", "privada"),
        ("C45", "Colegio de Abogados de Sevilla", "privada"),
        ("C46", "Colegio de Agentes Comerciales", "privada"),
        ("C47", "Colegio de Médicos", "privada"),
        ("C48", "Colegio Notarial de Andalucía", "privada"),
        ("C49", "Hermandad del Rocío de la Macarena", "privada"),
        ("C50", "La Prensa (Asociación de la Prensa de Sevilla)", "privada"),
        ("C51", "Telefónica", "privada"),
        ("C52", "Real Betis Balompié", "privada"),
        ("C53", "Sevilla F.C.", "privada"),
        ("C54", "Distrito Casco Antiguo", "pública"),
        ("C55", "Distrito Triana", "pública"),
        ("C56", "Distrito Nervión", "pública"),
        ("C57", "Distrito Macarena", "pública"),
        ("C58", "Distrito Sur", "pública"),
        ("C59", "Distrito Este-Alcosa-Torreblanca", "pública"),
        ("C60", "PSOE Andalucía", "pública"),
        ("C61", "Partido Popular", "pública"),
        ("C62", "UGT", "pública"),
        ("C63", "CCOO", "pública"),
    ]
    
    # Feria 2025 dates: 30 Abril al 4 Mayo
    base_date = datetime(2025, 4, 30, 0, 0, 0)
    
    # Generate data for all casetas every hour for 5 days
    for day in range(5):
        for hour in range(24):
            ts = base_date + timedelta(days=day, hours=hour)
            for caseta_id, name, type_caseta in casetas:
                # Base visitors depends on hour to reach ~500k per day
                if 20 <= hour or hour <= 3:
                    base_visitors = random.randint(400, 800) # Night peak
                elif 13 <= hour <= 17:
                    base_visitors = random.randint(200, 600)  # Afternoon peak
                else:
                    base_visitors = random.randint(50, 150)   # Low hours
                
                rows_to_insert.append({
                    "id_caseta": caseta_id,
                    "nombre_caseta": name,
                    "tipo_caseta": type_caseta,
                    "timestamp": ts.isoformat(),
                    "numero_visitantes": base_visitors
                })

    # Chunk insert
    chunk_size = 500
    for i in range(0, len(rows_to_insert), chunk_size):
        chunk = rows_to_insert[i:i + chunk_size]
        errors = client.insert_rows_json(table_ref, chunk)
        if errors:
            print(f"❌ Errors inserting {table_id}: {errors}")
        else:
            print(f"✅ Inserted {len(chunk)} rows into {table_id}")

def generate_transporte_data(client):
    """Generates mock data for transporte_publico."""
    table_id = "transporte_publico"
    schema = [
        bigquery.SchemaField("id_viaje", "STRING"),
        bigquery.SchemaField("tipo_transporte", "STRING"),
        bigquery.SchemaField("linea", "STRING"),
        bigquery.SchemaField("timestamp", "TIMESTAMP"),
        bigquery.SchemaField("pasajeros", "INTEGER"),
    ]
    create_table_if_not_exists(client, table_id, schema)

    table_ref = client.dataset(DATASET_ID).table(table_id)
    table = client.get_table(table_ref)
    if table.num_rows > 0:
        print(f"ℹ️ Table {table_id} already has data. Skipping.")
        return

    print(f"🚀 Generating data for {table_id}...")
    rows_to_insert = []
    lines = {
        "bus": ["C1", "C2", "Especia Feria"],
        "metro": ["L1"],
        "taxi": ["Urbano"]
    }
    
    base_date = datetime(2025, 4, 30, 0, 0, 0)
    
    # Generate hourly aggregates for each transport line to reach ~2.6M total
    for day in range(5):
        for hour in range(24):
            ts = base_date + timedelta(days=day, hours=hour)
            for transport_type, line_list in lines.items():
                for line in line_list:
                    # Passengers depend on hour and type
                    if 20 <= hour or hour <= 3:
                        base_pasajeros = random.randint(7000, 15000) if transport_type != "taxi" else random.randint(500, 1000)
                    elif 13 <= hour <= 17:
                        base_pasajeros = random.randint(4000, 8000) if transport_type != "taxi" else random.randint(300, 600)
                    else:
                        base_pasajeros = random.randint(1000, 2000) if transport_type != "taxi" else random.randint(50, 200)
                        
                    rows_to_insert.append({
                        "id_viaje": str(uuid.uuid4()),
                        "tipo_transporte": transport_type,
                        "linea": line,
                        "timestamp": ts.isoformat(),
                        "pasajeros": base_pasajeros
                    })

    errors = client.insert_rows_json(table_ref, rows_to_insert)
    if errors:
        print(f"❌ Errors inserting {table_id}: {errors}")
    else:
        print(f"✅ Inserted {len(rows_to_insert)} rows into {table_id}")

def generate_economico_data(client):
    """Generates mock data for impacto_economico."""
    table_id = "impacto_economico"
    schema = [
        bigquery.SchemaField("id_transaccion", "STRING"),
        bigquery.SchemaField("tipo_negocio", "STRING"),
        bigquery.SchemaField("timestamp", "TIMESTAMP"),
        bigquery.SchemaField("importe_eur", "FLOAT"),
    ]
    create_table_if_not_exists(client, table_id, schema)

    table_ref = client.dataset(DATASET_ID).table(table_id)
    table = client.get_table(table_ref)
    if table.num_rows > 0:
        print(f"ℹ️ Table {table_id} already has data. Skipping.")
        return

    print(f"🚀 Generating data for {table_id}...")
    rows_to_insert = []
    base_date = datetime(2025, 4, 30, 0, 0, 0)
    
    for i in range(2000):
        negocio = random.choice(["hotel", "restaurante"])
        offset_seconds = random.randint(0, 5 * 24 * 3600)
        ts = base_date + timedelta(seconds=offset_seconds)
        
        if negocio == "hotel":
            importe = random.uniform(100.0, 500.0)
        else:
            importe = random.uniform(15.0, 150.0)
            
        rows_to_insert.append({
            "id_transaccion": str(uuid.uuid4()),
            "tipo_negocio": negocio,
            "timestamp": ts.isoformat(),
            "importe_eur": importe
        })

    # Chunk insert
    chunk_size = 1000
    for i in range(0, len(rows_to_insert), chunk_size):
        chunk = rows_to_insert[i:i + chunk_size]
        errors = client.insert_rows_json(table_ref, chunk)
        if errors:
            print(f"❌ Errors inserting {table_id}: {errors}")
        else:
            print(f"✅ Inserted {len(chunk)} rows into {table_id}")

def generate_meteorologia_data(client):
    """Generates mock data for meteorologia."""
    table_id = "meteorologia"
    schema = [
        bigquery.SchemaField("timestamp", "TIMESTAMP"),
        bigquery.SchemaField("estado_clima", "STRING"), # Soleado, Lluvioso, Nublado
        bigquery.SchemaField("temperatura_c", "FLOAT"),
    ]
    create_table_if_not_exists(client, table_id, schema)

    table_ref = client.dataset(DATASET_ID).table(table_id)
    
    # Feria 2025 dates: 30 Abril al 4 Mayo
    base_date = datetime(2025, 4, 30, 0, 0, 0)
    rows_to_insert = []
    
    # Generar datos cada hora para los 5 días
    for hour_offset in range(5 * 24):
        ts = base_date + timedelta(hours=hour_offset)
        
        # Simular que el Viernes (Día 3) llovió por la tarde
        if ts.day == 2 and 14 <= ts.hour <= 20:
            clima = "Lluvioso"
            temp = random.uniform(15.0, 18.0)
        else:
            clima = random.choice(["Soleado", "Nublado"])
            temp = random.uniform(20.0, 28.0)
            
        rows_to_insert.append({
            "timestamp": ts.isoformat(),
            "estado_clima": clima,
            "temperatura_c": temp
        })

    client.insert_rows_json(table_ref, rows_to_insert)
    print(f"✅ Inserted {len(rows_to_insert)} rows into {table_id}")

def main():
    client = get_client()
    
    create_dataset_if_not_exists(client)
    
    # Force reset for new data by deleting tables
    tables = ["afluencia_casetas", "transporte_publico", "impacto_economico", "meteorologia"]
    for t in tables:
        try:
            client.delete_table(client.dataset(DATASET_ID).table(t), not_found_ok=True)
            print(f"🗑️ Deleted table {t} for a clean reset.")
        except Exception as e:
            print(f"ℹ️ Note when deleting table {t}: {e}")
            
    generate_afluencia_data(client)
    generate_transporte_data(client)
    generate_economico_data(client)
    generate_meteorologia_data(client)
    print("🎉 All done!")

if __name__ == "__main__":
    main()
