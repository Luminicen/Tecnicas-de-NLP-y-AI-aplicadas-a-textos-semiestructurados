#!/bin/bash

# Variables
IMAGE_NAME="gabiperez/voz-pasiva-api"
IMAGE_TAG="latest"
DEPLOYMENT_NAME="voz-pasiva-api"
CONTAINER_NAME="voz-pasiva-container"
MANIFEST_FILE="k8s/deployment.yaml"

echo "Construyendo imagen Docker..."
docker build -t $IMAGE_NAME:$IMAGE_TAG .

echo "Haciendo push de la imagen al registry..."
docker push $IMAGE_NAME:$IMAGE_TAG

echo "Aplicando manifiesto en OKD..."
oc apply -f $MANIFEST_FILE

echo "Forzando actualización de imagen en el deployment..."
oc set image deployment/$DEPLOYMENT_NAME $CONTAINER_NAME=$IMAGE_NAME:$IMAGE_TAG --record

echo "Mostrando pods actualizados..."
oc get pods -l app=$DEPLOYMENT_NAME

echo "http://voz-pasiva-api-req-nlp.okd.lifia.info.unlp.edu.ar/
