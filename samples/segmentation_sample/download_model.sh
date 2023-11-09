#!/bin/bash

function download(){
	ID=$1
	NAME=$2
	
	if [[ ! -z $(ls model 2>/dev/null )  ]];then
		echo "$(date +"%F %T") the model folder has already exist !"
	else
		gdown --id $ID -O $NAME
	fi
}

# ------------------------------------------------------------------------------

echo "$(date +"%F %T") Download model from google drive ..."
MODEL_PATH="/workspace/model/"
cd ${MODEL_PATH}

# ------------------------------------------------------------------------------

# Model: https://drive.google.com/file/d/1ylMHWd1KN6Ydhxryxrc-ZyPALf5rmI9F/view?usp=share_link
NAME="resnet18-320x480"
ZIP="${NAME}.zip"
TARGET_PATH="${MODEL_PATH}${NAME}"
if [[ -d ${NAME} ]];then
	echo "$(date +"%F %T") Model already exist"
	exit 1
fi

GID="16Gw198aIP0s8lF_XjCf6LEkuQubUZ9U8"
download $GID ${ZIP}
unzip $ZIP -d ${TARGET_PATH} && rm "${ZIP}"
