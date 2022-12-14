#!/bin/bash
# POSE ESTIMATION SAMPLE

# Define Parameters
LEN=20
WS="/workspace"
FRAMEWORK="tensorrt"
TASK_ROOT="task"

TASK_NAME="humanpose_sample"
TASK_CONF="task.json"
MODEL_NAME="resnet18_baseline_att_224x224_A.engine"
PTH_NAME="resnet18_baseline_att_224x224_A.pth"

RUN_DEMO=false
SERVER_MODE=""

# Combine Parameters
TASK_PATH="${WS}/${TASK_ROOT}/${TASK_NAME}"
CONF_PATH="${TASK_PATH}/${TASK_CONF}"
MODEL_PATH="${TASK_PATH}/${MODEL_NAME}"
PTH_PATH="${TASK_PATH}/${PTH_NAME}"

# Setup Running Script
DOWNLOAD_SCRIPT="download_model.sh"
MODIFTY_GPU_SCRIPT="${WS}/tools/update_first_gpu.py"
CONVERT_SCRIPT="${WS}/converter/yolo-converter.sh"

RUN_DOWNLOAD_DATA="${TASK_PATH}/download_data.sh"
RUN_DOWNLOAD_MODEL="${TASK_PATH}/download_model.sh"
RUN_GPU_MODIFY="python3 ${MODIFTY_GPU_SCRIPT} -f ${FRAMEWORK} -j ${CONF_PATH}"

# Title
printf "\n"
printf "# FAST-RUN ${TASK_NAME} \n"

# Define HELP
function help(){
	echo "Run the iVIT-I environment."
	echo
	echo "Syntax: scriptTemplate [-rsh]"
	echo "options:"
	echo "r     run demo"
    echo "s     run demo with server mode"
	echo "h     help."
}

# Define Argument and Parse it
while getopts "rsh" option; do
	case $option in
		r )
			RUN_DEMO=true ;;
		s )
			SERVER_MODE="-s" ;;
		h )
			help; exit ;;
		\? )
			help; exit;;
		* )
			help; exit;;
	esac
done

# Show information
printf "%-${LEN}s | %-${LEN}s \n" "TIME" "$(date)"
printf "%-${LEN}s | %-${LEN}s \n" "TASK_PATH" "${TASK_PATH}"
printf "%-${LEN}s | %-${LEN}s \n" "CONF_PATH" "${CONF_PATH}"
printf "%-${LEN}s | %-${LEN}s \n" "RUN SAMPLE" "${RUN_DEMO}"
printf "%-${LEN}s | %-${LEN}s \n" "SERVER MODE" $(if [[ ${SERVER_MODE} = "" ]];then echo false; else echo true;fi)
printf "%-${LEN}s | %-${LEN}s \n" "DOWNLOAD DATA" "${RUN_DOWNLOAD_DATA}"
printf "%-${LEN}s | %-${LEN}s \n" "DOWNLOAD MODEL" "${RUN_DOWNLOAD_MODEL}"
printf "%-${LEN}s | %-${LEN}s \n" "MODIFY GPU" "${RUN_GPU_MODIFY}"

# Move to Workspace
cd $WS

# Download data
${RUN_DOWNLOAD_DATA}

# Download model
${RUN_DOWNLOAD_MODEL}

# Convert Model
if [[ ! -f ${MODEL_PATH} ]];then
    ./converter/pose-converter \
    -m ${PTH_PATH} \
    -j ${TASK_PATH}/label.json \
    -e ${MODEL_PATH}
fi

# Change GPU
${RUN_GPU_MODIFY}

# Run Sample
if [[ "$RUN_DEMO" = true ]];then
    printf "\nRun Sample ... \n"
	export IVIT_I=/workspace/ivit-i.json
    python3 demo.py -c ${CONF_PATH} ${SERVER_MODE}
else
    printf "${TASK_NAME} Initialize finished \n"
fi
