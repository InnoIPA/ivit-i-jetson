# Segmentation Sample
iVIT Segmentation Sample, this sample demonstrates how to do inference of image segmentation models using iVIT [Source](../ivit_source_sample/README.md) and [Displayer](../ivit_displayer_sample/README.md).

## Getting Start
* Clone Repository    
    ```bash
    git clone https://github.com/InnoIPA/ivit-i-jetson-dev__confidential.git && cd ivit-i-hailoivit-i-jetson-dev__confidential
    ```
* Run iVIT-I Docker Container
    ```bash
    ./docker/run.sh
    ```
    * More options : 
        ```bash
        -b	#run in background
        -q	#Qucik launch iVIT-I
        -h	#help.
        ```
* Download Data 
    ```bash
    # Move to target folder
    cd /workspace/samples/segmentation_sample
    
    chmod u+x ./*.sh

    #Download data and model and covert model.
    ./model_prepare.sh        

    ```
    * More infomation about model_prepare.sh
    ```bash
    ./model_prepare.sh --help
        """
        -m		download model.
        -d		download data.
        -c		convert  model.
        """
    ```     
    
* Setting Varaible
    ```bash
    
    EXEC_PY="python3 ./segmentation_demo.py"

    ROOT=/workspace
    MODEL=${ROOT}/model/resnet18-320x480/resnet18-320x480.trt
    LABEL=${ROOT}/model/resnet18-320x480/classes.txt
    INPUT=${ROOT}/data/0006R0_f02100.png
    ```

* Run Sample
    ```bash
    ${EXEC_PY} -m ${MODEL} -l ${LABEL} -i ${INPUT}
    ```

## Usage
* Help
    ```bash
    ${EXEC_PY} -h
    ```
