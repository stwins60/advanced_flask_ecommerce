pipeline {
    agent any

    environment {
        IMAGE_NAME = "idrisniyi94/ecommerce-app"
        BRANCH_NAME = "${GIT_BRANCH.split('/')[1]}"
        DOCKERHUB_CREDENTIALS = credentials('3e4f8f4f-6b21-4486-b495-53b7cfc978ca')
        IMAGE_TAG = "v.0.0.${env.BUILD_NUMBER}"
    }

    stages {
        stage("Docker Login") {
            steps {
                sh "echo $DOCKERHUB_CREDENTIALS_PSW | docker login -u $DOCKERHUB_CREDENTIALS_USR --password-stdin"
                echo "Login Successful"
            }
        }
        stage("Docker Build") {
            steps {
                script {
                    if (env.BRANCH_NAME == "dev") {
                        sh "docker build -t $IMAGE_NAME:$BRANCH_NAME-$IMAGE_TAG ."
                        echo "Docker image built successfully"
                    } else if (env.BRANCH_NAME == "prod") {
                        sh "docker build -t $IMAGE_NAME:$BRANCH_NAME-$IMAGE_TAG ."
                        echo "Docker image built successfully"
                    }
                }
            }
        }
        stage("Docker Push") {
            steps {
                sh "docker push $IMAGE_NAME:$BRANCH_NAME-$IMAGE_TAG"
                echo "Image pushed successfully"
            }
        }
        stage("Deployment") {
            steps {
                script {
                    dir('./k8s') {
                        if (env.BRANCH_NAME == 'dev') {
                            sh "sed -i 's/NAMESPACE/dev/g' deploy.yaml"
                            sh "sed -i 's/NAMESPACE/dev/g' svc.yaml"
                            sh "sed -i 's|IMAGE_NAME|$IMAGE_NAME:$BRANCH_NAME-$IMAGE_TAG|g' deploy.yaml"

                            sh "kubectl apply -f ."

                            echo "Resources deployed to prod"
                        }else if (env.BRANCH_NAME == 'master') {
                            sh "sed -i 's/NAMESPACE/prod/g' deploy.yaml"
                            sh "sed -i 's/NAMESPACE/prod/g' svc.yaml"
                            sh "sed -i 's|IMAGE_NAME|$IMAGE_NAME:$BRANCH_NAME-$IMAGE_TAG|g' deploy.yaml"

                            sh "kubectl apply -f ."

                            echo "Resources deployed to prod"
                        }
                    }
                }
            }
        }
    }
}