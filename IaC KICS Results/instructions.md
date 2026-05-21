# KICS Analysis

## Steps to reproduce
1. Download docker desktop (we used version 4.72.0)
2. Download and unzip version 11.6.1 of Mattermost into its own project.
3. Run docker desktop in the background.
4. Go to the terminal of the project and run the following command. This scans the entire project for errors or misconfigurations
``````
docker run -t -v "${PWD}:/scan" checkmarx/kics:latest scan -p /scan
``````
5. If you want only errors or misconfigurations relevant to infrastructure, instead run the following command.
``````
docker run -t -v "${PWD}:/scan" checkmarx/kics:latest scan -p /scan --type Dockerfile --disable-secrets
``````
6. To save the results as a specific file, the following extra command was appended on to the previous commands.
``````
--report-formats json --output-path scan/scanned-results --output-name docker-scan
``````
9. To access the created file. Navigate to the most recent run container on docker desktop. (This should be the scan run)
8. Go to Files, if your container is currently running (because the created file is temporary) then you should see the files within it.
9. Navigate (assuming you have named it the same): apps > bin > scan > scanned-results > docker-scan.json

# KICS Scan results
Specific infrastructure results can be viewed in `docker-scan.json`
