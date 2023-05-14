import functions_framework
import base64
from google.cloud import bigquery
from google.cloud import iot_v1
import os
#twilio nous permet de recevoir les notification 
#import twilio
#from twilio.rest import Client

#def risk_prediction(text):
  # Set environment variables for your credentials
  # Read more at http://twil.io/secure
  #account_sid = "AC0b24f0cafa51bb85dbad6d385e126954"
 # auth_token = "a748d7f67aaa969e65a6dffa0114de1f"
 # client = Client(account_sid, auth_token)
 # message = client.messages.create(
  #  body=f"{text}",
  #  from_="+",
  #  to="+"
 # )
  #print(message.sid)

@functions_framework.cloud_event
def risk_assessment(cloud_event):
    # Parameters - Cloud IoT Core (à indiquer manuellement)
    project_id = "dit-m1ia-nov22"
    cloud_region = "us-central1"
    registry_id = "registre-bayili"  # remplacer prenom par votre propre prenom
    device_id = "hum-temp-device"
    
    # Pub/Sub data : get message from cloud scheduler
    schedule_message = base64.b64decode(cloud_event.data["message"]["data"]).decode("utf-8")
    print(f"Receiving message from Cloud Scheduler : {schedule_message}")
    
    # Predict based on the last 12 hours recorded sensor data (temperature, humidity, month)
    bq_client = bigquery.Client()
    # NB: dans la requête suivante, remplacer prenom par le prenom que vous indiqué dans BigQuery
    query_asthme = """
     SELECT
       *
     FROM
       ML.PREDICT(MODEL `ml_models_bbrahima.asthme_prediction`, (
       SELECT
          CAST(humidite AS FLOAT64) AS humidity,
          CAST(temperature AS FLOAT64) AS temperature,
          EXTRACT(MONTH FROM timestamp) as month
          FROM
            `dataset_iot_bbrahima.temperature_humidite`
          ORDER BY
            timestamp DESC
          LIMIT 10
       ))
    """
    query_hypertension = """
     SELECT
       *
     FROM
       ML.PREDICT(MODEL `ml_models_bbrahima.hypertension_prediction`, (
       SELECT
          CAST(humidite AS FLOAT64) AS humidity,
          CAST(temperature AS FLOAT64) AS temperature,
          EXTRACT(MONTH FROM timestamp) as month
          FROM
            `dataset_iot_bbrahima.temperature_humidite`
          ORDER BY
            timestamp DESC
          LIMIT 10
       ))
    """
    query_avc = """
     SELECT
       *
     FROM
       ML.PREDICT(MODEL `ml_models_bbrahima.avc_prediction`, (
       SELECT
          CAST(humidite AS FLOAT64) AS humidity,
          CAST(temperature AS FLOAT64) AS temperature,
          EXTRACT(MONTH FROM timestamp) as month
          FROM
            `dataset_iot_bbrahima.temperature_humidite`
          ORDER BY
            timestamp DESC
          LIMIT 10
       ))
    """
  
    query_job_asthme = bq_client.query(query_asthme)
    print()
    query_job_hypertension = bq_client.query(query_hypertension)
    print()
    query_job_avc = bq_client.query(query_avc)
    print()

    predict_asthme_daily_emergency = 0
    for row in query_job_asthme:
      print(row)
      if row[0] > predict_asthme_daily_emergency :
        predict_asthme_daily_emergency = row[0]
        print(f"predict_asthme_daily_emergency : {predict_asthme_daily_emergency}")

    predict_hypertension_daily_emergency = 0
    for row in query_job_hypertension:
      print(row)
      if row[0] > predict_hypertension_daily_emergency :
        predict_hypertension_daily_emergency = row[0]
        print(f"predict_hypertension_daily_emergency : {predict_hypertension_daily_emergency}")

    predict_avc_daily_emergency = 0
    for row in query_job_avc:
      print(row)
      if row[0] > predict_avc_daily_emergency :
        predict_avc_daily_emergency = row[0]
        print(f"predict_AVC_daily_emergency : {predict_avc_daily_emergency}")

    # Give prescription (NO RISK, RISK EXIST) based on rules engine
    # Cas ASTHME
    mean_asthme_daily_emergency = 5.62
    mean_hypertension_daily_emergency = 35.81
    mean_avc_daily_emergency = 75.2
    asthme_prescription = None
    if predict_asthme_daily_emergency  > mean_asthme_daily_emergency  :
      asthme_prescription = "ASTHME RISK EXIST : take your inhaler with you, avoid physical exertion, stay in ventilated spaces."
      print(f"asthme_prescription : {asthme_prescription}")
    
    # Cas : HYPERTENSION
    elif predict_hypertension_daily_emergency  > mean_hypertension_daily_emergency  :
      hypertension_prescription = "HYPERTENSION RISK EXIST : take your dispositions."
      print(f"Hypertension_prescription : {hypertension_prescription}")
    
    # Cas AVC
    elif predict_avc_daily_emergency  > mean_avc_daily_emergency  :
      avc_prescription = "AVC RISK EXIST : Be carefull and take your dispositions."
      print(f"avc_prescription : {avc_prescription}")
    
    
    # Formatting command
    command = ""
    if asthme_prescription:
      command = asthme_prescription
     # risk_prediction("ASTHME RISK EXIST")
    elif hypertension_prescription:
      command = hypertension_prescription
      #risk_prediction("HYPERTENSION RISK EXIST")
    elif avc_prescription:
      command = avc_prescription
      #risk_prediction("AVC RISK EXIST")
    
    # Sending command
    print("Sending command to device")
    iot_client = iot_v1.DeviceManagerClient()
    device_path = iot_client.device_path(project_id, cloud_region, registry_id, device_id)

    return iot_client.send_command_to_device(
       request={"name": device_path, "binary_data": command.encode("utf-8")}
    )