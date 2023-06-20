# Copyright 2022 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# --------------------------------------------------------------------------------
# Load The Dependencies
# --------------------------------------------------------------------------------

import csv
import datetime
import io
import json
import logging
import os

from airflow import models
from airflow.providers.google.cloud.operators.dataflow import DataflowTemplatedJobStartOperator
from airflow.operators import dummy
from airflow.providers.google.cloud.operators.bigquery import  BigQueryDeleteTableOperator
from airflow.utils.task_group import TaskGroup

# --------------------------------------------------------------------------------
# Set variables - Needed for the DEMO
# --------------------------------------------------------------------------------
BQ_LOCATION = os.environ.get("BQ_LOCATION")
CURATED_PRJ = os.environ.get("CURATED_PRJ")
CURATED_BQ_DATASET = os.environ.get("CURATED_BQ_DATASET")
CURATED_GCS = os.environ.get("CURATED_GCS")
LAND_PRJ = os.environ.get("LAND_PRJ")
LAND_GCS = os.environ.get("LAND_GCS")
PROCESSING_GCS = os.environ.get("PROCESSING_GCS")
PROCESSING_SA = os.environ.get("PROCESSING_SA")
PROCESSING_PRJ = os.environ.get("PROCESSING_PRJ")
PROCESSING_SUBNET = os.environ.get("PROCESSING_SUBNET")
PROCESSING_VPC = os.environ.get("PROCESSING_VPC")
DP_KMS_KEY = os.environ.get("DP_KMS_KEY", "")
DP_REGION = os.environ.get("DP_REGION")
DP_ZONE = os.environ.get("DP_REGION") + "-b"

# --------------------------------------------------------------------------------
# Set default arguments
# --------------------------------------------------------------------------------

# If you are running Airflow in more than one time zone
# see https://airflow.apache.org/docs/apache-airflow/stable/timezone.html
# for best practices
yesterday = datetime.datetime.now() - datetime.timedelta(days=1)

default_args = {
  'owner': 'airflow',
  'start_date': yesterday,
  'depends_on_past': False,
  'email': [''],
  'email_on_failure': False,
  'email_on_retry': False,
  'retries': 1,
  'retry_delay': datetime.timedelta(minutes=5),
}

# --------------------------------------------------------------------------------
# Main DAG
# --------------------------------------------------------------------------------

with models.DAG(
    'delete_tables_dag',
    default_args=default_args,
    schedule_interval=None) as dag:
  start = dummy.DummyOperator(
    task_id='start',
    trigger_rule='all_success'
  )

  end = dummy.DummyOperator(
    task_id='end',
    trigger_rule='all_success'
  )

  # Bigquery Tables deleted here for demo porpuse. 
  # Consider a dedicated pipeline or tool for a real life scenario.
  with TaskGroup('delete_table') as delte_table:  
    delete_table_customers = BigQueryDeleteTableOperator(
      task_id="delete_table_customers",
      deletion_dataset_table=CURATED_PRJ+"."+CURATED_BQ_DATASET+".customers",
      impersonation_chain=[PROCESSING_SA]
    )

  start >> delte_table >> end  
