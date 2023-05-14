import functions_framework
import base64
import json
from google.cloud import bigquery
from google.cloud import iot_v1

@functions_framework.cloud_event
def handle_dht11_data(cloud_event):
  # Parameters - Cloud IoT Core
  project_id = cloud_event.data["message"]["attributes"]["projectId"]
  cloud_region = cloud_event.data["message"]["attributes"]["deviceRegistryLocation"]
  device_id = cloud_event.data["message"]["attributes"]["deviceId"]

  # Personalized parameters - BigQuery
  dataset = "dataset_iot_prenom"  # change prenom suffix by your name
  table = "temperature_humidite"

  # Pub/Sub data
  data = base64.b64decode(cloud_event.data["message"]["data"]).decode("utf-8")
  data_dict = json.loads(data)
  rows_to_insert = [{
    "device_id": device_id,
    "temperature": data_dict["temperature"],
    "humidite": data_dict["humidity"],
    "timestamp": data_dict["timestamp"]
  }]

  # Insert data on BigQuery
  bq_client = bigquery.Client()
  table_id = bigquery.Table.from_string(f"{project_id}.{dataset}.{table}")
  errors = bq_client.insert_rows_json(table_id, rows_to_insert)
  if errors:
    print(f"Encountered errors while inserting rows: {errors}")