## Steps to reproduce
1. Follow the SonarQube instructions on running a local instance of the [Community SonarQube](https://docs.sonarsource.com/sonarqube-server/try-out-sonarqube) using the zip file method. Setup and run Sonar-scanner and SonarQube server by following the onscreen instructions.
2. Download and unzip version 11.6.1 of Mattermost into its own project.
3. Add the `sonar-project.properties` file to the root of the project.
4. Match the `sonar.sources` points to the folder containing the Mattermost project.
6. Navigate to the directory where you've placed `sonar-project.properties` in a terminal and run 
``````
 sonar-scanner -Dsonar.token={INSERT YOUR TOKEN HERE} -Dsonar.host.url=http://localhost:9000