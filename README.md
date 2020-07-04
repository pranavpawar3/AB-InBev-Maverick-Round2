# ABInBev Maverick -- Final Round
### Team Data_Brewers, IIT MADRAS

### Invoice Data Extraction -- End-to-End system

**Pipeline components**
  * [round2_api.py](/round2_api.py) - Flask API service
  * [run_job.py](/run_job.py) - Batch Processing Pipeline
  * [mongodb_upload.py](/mongodb_upload.py) - Script to upload data over MongoDB
 
 These scripts can be executed with right set of param inputs and you can get the job done! 
 
 But as we are looking for an end-to-end system, we have Airflow Continuous Integration of our processes. 
 
**Airflow Dags**
  * [pipeline_dag.py](/pipeline_dag.py) - DAG for Batch Processing Pipeline
  * [api_airflow_dag.py](/api_airflow_dag.py) - DAG for Flask API
  
### Instructions to start the docker service 

  * In order to start the service, you will first have to clone the [airflow-tutorial](https://github.com/pranavpawar3/airflow-tutorial) repo.
  * Now, navigate to the [docker-compose.yaml]() file and change this [line](https://github.com/pranavpawar3/airflow-tutorial/blob/18ce212911aa0c268d64cd7c1e2a281c50ed15ce/docker-compose.yml#L34) according to your machine's local paths where the dags are stored.
  * In the same yaml file as above, change this [line](https://github.com/pranavpawar3/airflow-tutorial/blob/18ce212911aa0c268d64cd7c1e2a281c50ed15ce/docker-compose.yml#L35) to local path where your invoice data is getting stored (can be a dynamic location).
  * Its preferred that you keep the directory struture of this repo same as it is for accurate docker volume map.

**Start the Service**

* Now navigate to the airflow-tutorial directory 
* ` cd airflow-tutorial `
* ` docker-compose up --build `
* This shall start building the docker and soon the airflow manager would start. It's likely to throw an error saying variables are not imported, but don't worry we will import the variables in the next step.
* Now, naviagate to `localhost:8080` and in the navigation bar on home page go to Admin > Variables, and upload the [variables.json](/config/variables.json) cofig file.
* If the location/ name for raw data source directory is changed, change the parameter `raw_invoice_path` in config file to the new directory name

Once all done, you can start the processes from on/off switch!!




  
