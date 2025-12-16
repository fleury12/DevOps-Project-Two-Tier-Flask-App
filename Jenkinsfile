pipeline{
    agent any
    environment {
        SCANNER_HOME = tool 'sonar-scanner'
    }
    stages{
        stage('clean workspace') {
            steps {
                cleanWs()
            }
        }

        stage('Clone repo'){
            steps{
                git branch: 'main', url: 'https://github.com/prashantgohel321/DevOps-Project-Two-Tier-Flask-App.git'
            }
        }
        stage("Sonarqube Analysis") {
            steps {
                withSonarQubeEnv('sonar-server') {
                    sh """
                        $SCANNER_HOME/bin/sonar-scanner \
                        -Dsonar.projectName=flask_app \
                        -Dsonar.projectKey=flask_app \
                        -Dsonar.sources=. \
                    """
                }
            }
        }
        stage("quality gate") {
            steps {
                script {
                    waitForQualityGate abortPipeline: false, credentialsId: 'sonar-token'
                }
            }
        }
        stage('OWASP FS SCAN') {
            steps {
                dependencyCheck additionalArguments: '--scan ./ --disableYarnAudit --disableNodeAudit', odcInstallation: 'DP-Check'
                dependencyCheckPublisher pattern: '**/dependency-check-report.xml'
            }
        }
        stage('TRIVY FS SCAN') {
            steps {
                sh "trivy fs . > trivyfs.txt"
            }
        }
        stage("Docker Build & Push"){
            steps{
                script{
                   withDockerRegistry(credentialsId: 'docker', toolName: 'docker'){   
                       sh "docker build -t flask-app ."
                       sh "docker tag flask-app fleury12/flask-app:latest "
                       sh "docker push fleury12/flask-app:latest "
                    }
                }
            }
        }
        stage("TRIVY"){
            steps{
                sh "trivy image fleury12/flask-app:latest > trivyimage.txt" 
            }
        }
        stage('Deploy with docker compose'){
            steps{
                // existing container if they are running
                sh 'docker compose down || true'
                // start app, rebuilding flask image
                sh 'docker compose up -d --build'
            }
        }
    }
}