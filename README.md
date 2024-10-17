# MESA GUI

Micro Evaluation Security Assessments (MESAs) are designed to provide organizations with insights into their internal security posture. The MESA-GUI serves as a user-friendly front-end for the MESA-Toolkit command-line interface (https://github.com/cisagov/mesa-toolkit/). This project relies on the successful installation of the MESA-Toolkit and is not intended to function as a standalone application.

It is important to note that MESAs are not designed to furnish a comprehensive understanding of the entire internal environment. Instead, their purpose is to equip organizations with the essential information needed to establish a foundational security posture. This emphasis revolves around safeguarding against commonly exploited misconfigurations and vulnerabilities. MESAs lay the groundwork for organizations to initiate the process of fortifying their security stance, ensuring a proactive defense against prevalent risks.

## Installing the MESA-GUI
>[!IMPORTANT]
>It is recommended to use the [MESA-Toolkit](https://github.com/cisagov/mesa-toolkit/) installation bash script prior to installing the MESA-GUI to maintain a standardized naming convention for resource locations.

Once the [MESA-Toolkit](https://github.com/cisagov/mesa-toolkit/) has been successfully installed on a `Debian 12.7.0` instance, the following steps can be used to manually setup the MESA-GUI.

1. **Clone the MESA-GUI repository**
   
   Clone this repository into the /opt/ directory to download the MESA-GUI source code locally:

```bash
cd /opt/
sudo git clone https://github.com/cisagov/mesa-gui
cd mesa-gui
```

2. **Source the MESA virtual environment**

   Source the MESA virtual environment. This activates the environment, isolating the dependencies needed for the MESA-GUI to run:

```bash
source /opt/MESA-venv/bin/activate
```

3. **Install the MESA-GUI**
   
   Install the MESA-GUI using pip in editable mode (-e flag). This allows modifications to the source code without requiring a reinstall:

```bash
pip install -e .
```

4. **Apply database migrations**

   Run the migrate command to apply any necessary database schema changes:
   
```bash
cd mesa_gui
python manage.py migrate
```

5. **Create an administrative user**

  Create a superuser account for accessing the web application:

```bash
python manage.py createsuperuser
```

6. **Load MESA jobs data**

   Load the MESA jobs data into the Django database. These fixtures define the job functions that the MESA-GUI will use for scanning activities:

```bash
python manage.py loaddata mesa/fixtures/mesajobs.json
```

7. **Generate a self-signed SSL certificate**

  Generate a self-signed SSL certificate to securely host the MESA-GUI over HTTPS, ensuring encrypted communication:

```bash
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes -subj "/C=/ST=/L=/O=/OU=/CN="
```

8. **Start the web application**

   Start the web application using the SSL certificate:

```bash
python manage.py runsslserver --certificate cert.pem --key key.pem 0.0.0.0:8080
```

## Navigating the MESA-GUI

Once the installation process is complete, the MESA-GUI web interface can be accessed by browsing to the IP address of the machine hosting the web server:

```
https://[IP Address]:8080
```
![image](https://github.com/user-attachments/assets/d804ab89-2d21-467a-b80e-7bf3082ea614)

Login to the application using the credentials created during the installation process to access the MESA dashboard:

![image](https://github.com/user-attachments/assets/e5a0d4f8-2dc7-4448-99e6-788c0d08e8b6)

Configuring Scan Settings
--------------
Prior to running any scans, browse to the settings tab to configure the scan scope and pertinent deliverable variables:

![image](https://github.com/user-attachments/assets/3b13e3bd-ab9e-4fae-b5e4-3d2e28b5af61)

Update the following variables in the settings tab:

| Variable | Description | Default | Required |
|----------|-------------|---------|---------|
| Project Name | The name used to track the project | RV#### | yes |
| Customer Name | The customer full name as it will appear on the deliverables | Acme Corporation | yes |
| Customer Initials | The customer shortname as it will appear on the deliverables | ACME | yes |
| In-Scope Systems | The individual IP addresses or cidr blocks to be included in scanning activity | none | yes |
| Excluded Systems | The individual IP addresses or cidr blocks to be excluded from scanning activity | none | no |

MESA Job Definitions
--------------
Once the settings have been configured browse to the dashboard tab to begin running the scans:

![image](https://github.com/user-attachments/assets/1091208a-12a2-463e-81aa-960d47dc9497)

| Job Title | Description | Required | 
|----------|-------------|---------|
| Host Discovery Scans | Performs an nmap discovery scan against the provided scope. | yes |
| SMB Signing Checks | Performs a netexec scan to identify windows systems lacking smb signing within the provided scope. | no |
| Web Application Enumeration | Performs an aqutone web application enumeration scan against the provided scope. | no |
| Encryption Check | Performs a discovery scan to identify the exisitence of non encrypted protocols within the provided scope. Performs a secondary ssl scan against discovered web applications to check for deprecated ciphers. | no |
| Default Logins Check | Performs automated checks using nuclei for default login information against web applications and network devices within the provided scope. | no |
| Vulnerability Scan | Performs vulnerability scans using nuclei to identify critical, high, and medium findings. | no |
| Full Port Scan | Performs an nmap full port scan against the provided scope. | no |

Running MESA Jobs
--------------

MESA jobs can be ran individually or automatically in sequential order. To run the scans individually simply select the ![image](https://github.com/user-attachments/assets/208c9b72-7468-4421-a2f0-f9c7434b352f) button for the job you would like to run. 

>[!IMPORTANT]
>It is recommended to run the `Host Discovery Scans` job prior to running any other scans. This will ensure that a `live hosts` file is generated, expediting the time spent performing scans.

![image](https://github.com/user-attachments/assets/8b974fc0-6d7a-474f-9c9f-be7b21c0f16d)

In order to run the scans in sequential order starting with the `Host Discovery Scans`, simply click the `Run All Checks` button located on the dashboard:

![image](https://github.com/user-attachments/assets/c5c890a3-6702-4a6c-9004-419d564e82b8)

![image](https://github.com/user-attachments/assets/5b3ec047-b725-47f1-8cda-613eeda492c1)

>[!NOTE]
>Selecting the `Stop All Checks` button will stop current and remaining scans. Completed scans will still be accessible for download.

>[!WARNING]
>Selecting the `Run All Checks` button after stopping them will restart the scans back at the beginning. Any previous scan data will be overwritten. It is recommended to download a copy of the previous results using the ![image](https://github.com/user-attachments/assets/2d585e7e-2143-40ba-89b4-43570fe304a8) button.


### Understanding MESA Job Status
The second column on the MESA dashboard will provide the user with the status of any particular job. A description of each status can be found below:

| Status | Description | 
|----------|-------------|
| Not Started | The default status for any job that has not been ran |
| Queued | The job has been queued to run |
| Running | The job is actively running |
| Completed | The job has completed and the results are ready to download |
| Failed | The job failed to run, indicating an error when attempting to perform the scan |

### Stopping a Running Job
In the event that a scan needs to be stopped for any reason, simply select the ![image](https://github.com/user-attachments/assets/bd7ad5de-480f-4c10-bc96-6dc95a6789a1)
button to stop the scan:

![image](https://github.com/user-attachments/assets/4c8ceb70-97a3-4ddf-8865-28f675df3480)

>[!NOTE]
>The status of the scan will revert back to `Not Started` after it has been stopped. Stopped scans will need to be started from the beginning.

### Downloading Completed Job Results
After scans have been completed, the scans can be downloaded using the ![image](https://github.com/user-attachments/assets/2d585e7e-2143-40ba-89b4-43570fe304a8) button:

![image](https://github.com/user-attachments/assets/3251da8f-61a6-4e2a-bda1-a0cdde3587ca)

A zip file containing the raw scan results for the job selected will be downloaded. The file will be prepended with the project name.

### Deleting a Job
>[!CAUTION]
>Deleting a job is an irreversable action and should only be performed after downloading a backup of the data or if there is no use for the scan results.

In the event that the results from a job are no longer needed, they can be deleted using the ![image](https://github.com/user-attachments/assets/4c1ecc82-b531-43b7-ab73-246c71006ee2) button. 

![image](https://github.com/user-attachments/assets/7271136e-3db0-42d5-86c5-0aa559358a16)

After selecting the ![image](https://github.com/user-attachments/assets/4c1ecc82-b531-43b7-ab73-246c71006ee2) button, a pop up will appear reminding the user that this is an irreversable action. Select `Destroy` to delete the data for the selected job.

![image](https://github.com/user-attachments/assets/3c9a8293-976a-4b1b-a00b-502214c6b741)

## MESA Deliverables

The MESA-GUI was designed to provide three types of deliverables for users. 

### Raw Scan Data
Use the `Download All` button to download the raw scan results for all completed scans. This can be useful when wanting to manually parse through the various results from the tools used by the MESA-Toolkit:

![image](https://github.com/user-attachments/assets/8dbcbd58-d0ab-438c-a8e4-f4919264c9d3)

The contents of the zip file will be structured according to the scans that were performed and the finding type associated with the results:

![image](https://github.com/user-attachments/assets/95de4ef7-879b-4546-a7e5-5d2d62aa583b)

>[!NOTE]
>The contents of the zip file will vary depending on the network scanned. The screenshot above is just an example of the data structure.

### Summary HTML and PDF Reports
Use the `Download Report` button to download an HTML and PDF report that summarizes the scan results for the user:

![image](https://github.com/user-attachments/assets/88373564-6d66-4c17-a7c9-18a833f52325)

The reports can be found in the `report` directory within the downloaded zip file:

![image](https://github.com/user-attachments/assets/89597eb2-d4aa-4d7a-a2d1-dd9a90059ccf)

The HTML report will provide a summary of the scan results to the user with hyperlinks that will take the user to the raw scan results for further inspection:
>[!NOTE]
>The hyperlinks in the result summary section will break if the HTML report is removed from the reports directory. The PDF report is a standalone copy of the HTML report and can be used for situations where only summary statistics are requested.

![image](https://github.com/user-attachments/assets/ed0f9e3a-52a5-4d79-940b-3463997d22b4)

Links to CISA resources can be found at the top of the HTML report under the `CISA Resources` drop down. These links provide users with information regarding CISA specific services and resources:

![image](https://github.com/user-attachments/assets/a1da7ace-09c4-4adf-b62a-16e59f28f520)

Finally, the `Quick Access` drop down provides the user with direct access to the raw scan data collected from the MESA scans:
>[!NOTE]
>The quick access links will break if the HTML report is removed from the reports directory. These quick access links are intended to provide easy navigation through the raw scan directories located in the downloaded customer report zip file.

![image](https://github.com/user-attachments/assets/22b07a37-12f8-4b7d-9a2f-309aa0026a49)

### JSON Summary Data

![image](https://github.com/user-attachments/assets/15e25429-9814-4e66-9eca-1defe0c5b0d0)

## Migrations
>[!CAUTION]
>Migrations will need to be created when making alterations to the SQL database. The following commands can be used to create a migration:

```bash
python manage.py makemigrations mesa -n <name_of_file>
python manage.py sqlmigrate mesa 0011
python manage.py migrate
```

### Template Used

https://startbootstrap.com/theme/sb-admin-2
