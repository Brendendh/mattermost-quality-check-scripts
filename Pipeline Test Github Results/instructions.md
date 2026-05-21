# Deployment Analysis

## Steps to reproduce
1. Ensure that the GitHub Cli is installed (to run the commands with gh)
2. Download and unzip version 11.6.1 of Mattermost into its own project.
4. Go to the terminal of the project and run the following command. This checks with GitHub the success rate of the pipeline and prints the results.
``````
gh workflow-stats -o mattermost -r mattermost -f {file name}
``````

# Build Pipeline Test results
The important build pipeline pass rate results can be viewed in `build-pipeline-results.txt`
