#!/usr/bin/env python3
# Copyright (c) 2023 Innodisk Corporation
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT


import logging as log
import cv2, sys
import numpy as np
from argparse import ArgumentParser, SUPPRESS
from ivit_i.io import Source, Displayer
from ivit_i.core.models import iSegmentation
from ivit_i.common import Metric

def build_argparser():

    parser = ArgumentParser(add_help=False)

    basic_args = parser.add_argument_group('Basic options')
    basic_args.add_argument('-h', '--help', action='help', default=SUPPRESS, help='Show this help message and exit.')
    basic_args.add_argument('-m', '--model', required=True, help='the path to model')
    basic_args.add_argument('-i', '--input', required=True,
                      help='Required. An input to process. The input must be a single image, '
                           'a folder of images, video file or camera id.')
    basic_args.add_argument('-l', '--label', help='Optional. Labels mapping file.', default=None, type=str)
    basic_args.add_argument('-d', '--device', type=str,
                      help='Optional. `Intel` support [ `CPU`, `GPU` ] \
                            `Hailo` is support [ `HAILO` ]; \
                            `Xilinx` support [ `DPU` ]; \
                            `dGPU` support [ 0, ... ] which depends on the device index of your GPUs; \
                            `Jetson` support [ 0 ].' )
    
    model_args = parser.add_argument_group('Model options')
    model_args.add_argument('-t', '--confidence_threshold', default=0.1, type=float,
                                   help='Optional. Confidence threshold for detections.')
    model_args.add_argument('-topk', help='Optional. Number of top results. Default value is 5. Must be from 1 to 10.', default=5,
                                   type=int, choices=range(1, 11))

    io_args = parser.add_argument_group('Input/output options')
    io_args.add_argument('-n', '--name', default='ivit', 
                         help="Optional. The window name and rtsp namespace.")
    io_args.add_argument('-r', '--resolution', type=str, default=None, 
                         help="Optional. Only support usb camera. The resolution you want to get from source object.")
    io_args.add_argument('-f', '--fps', type=int, default=None,
                         help="Optional. Only support usb camera. The fps you want to setup.")
    io_args.add_argument('--no_show', action='store_true',
                         help="Optional. Don't display any stream.")

    args = parser.parse_args()
    # Parse Resoltion
    if args.resolution:
        args.resolution = tuple(map(int, args.resolution.split('x')))

    return args

def draw_detections(frame,result):
    visualizer = SegmentationVisualizer()
    frame = render_segmentation(frame, result, visualizer)

    return frame

class SegmentationVisualizer:
    pascal_voc_palette = [
        # (0,   0,   0),
        (128, 0,   0),
        (0,   128, 0),
        (128, 128, 0),
        (0,   0,   128),
        (128, 0,   128),
        (0,   128, 128),
        (128, 128, 128),
        (64,  0,   0),
        (192, 0,   0),
        (64,  128, 0),
        (192, 128, 0),
        (64,  0,   128),
        (192, 0,   128),
        (64,  128, 128),
        (192, 128, 128),
        (0,   64,  0),
        (128, 64,  0),
        (0,   192, 0),
        (128, 192, 0),
        (0,   64,  128)
    ]

    def __init__(self, colors_path=None):
        if colors_path:
            self.color_palette = self.get_palette_from_file(colors_path)
        else:
            self.color_palette = self.pascal_voc_palette
        self.color_map = self.create_color_map()

    def get_palette_from_file(self, colors_path):
        with open(colors_path, 'r') as file:
            colors = []
            for line in file.readlines():
                values = line[line.index('(')+1:line.index(')')].split(',')
                colors.append([int(v.strip()) for v in values])
            return colors

    def create_color_map(self):


        classes = np.array(self.color_palette, dtype=np.uint8)[:, ::-1] # RGB to BGR
        color_map = np.zeros((256, 1, 3), dtype=np.uint8)
        classes_num = len(classes)
        
        color_map[:classes_num, 0, :] = classes
        
        color_map[classes_num:, 0, :] = np.random.uniform(0, 255, size=(256-classes_num, 3))

        return color_map

    def apply_color_map(self, input):
        # print(input)
        input_3d = cv2.merge([input, input, input])
        # print(self.color_map)
        return cv2.LUT(input_3d, self.color_map)

def render_segmentation(frame, masks, visualiser, only_masks=False):

    output = visualiser.apply_color_map(masks)
    
    # cv2.imwrite("mask_after_lut.jpg", output)
    if not only_masks:
        output = np.floor_divide(frame, 2) + np.floor_divide(output, 2)
    
    return output

def main():

    # 1. Argparse
    args = build_argparser()

    # 2. Basic Parameters
    infer_metrx = Metric()
    
    # 3. Init Model
    model = iSegmentation(
        model_path = args.model,
        label_path = args.label,
        device=args.device
        )
    
    # 4. Init Source
    src = Source(   
        input = args.input, 
        resolution = args.resolution, 
        fps = args.fps )
    
    # 5. Init Display
    if not args.no_show:
        dpr = Displayer( cv = True )


    # 6. Start Inference
    try:
        while(True):
            # Get frame & Do infernece
            frame = src.read()       
            result = model.inference( frame )
            frame = draw_detections(frame,result)

            if args.no_show:
                # Just logout
                pass
            else:
                # Draw results
                # Draw FPS: default is left-top                     
                infer_metrx.paint_metrics(frame)
                
                # Display
                dpr.show(frame=frame)                   
                if dpr.get_press_key()==ord('q'):
                    break

            # Update Metrix
            infer_metrx.update()

    except KeyboardInterrupt: 
        log.info('Detected Key Interrupt !')

    finally:
        model.release()     # Release Model
        src.release()       # Release Source
        if not args.no_show: 
            dpr.release()   # Release Display

if __name__ == '__main__':
    sys.exit(main() or 0)