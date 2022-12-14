#!/bin/python3

import os, sys, cv2, logging, argparse, time

# Import iVIT-I Module
sys.path.append(os.getcwd())
from ivit_i.common import api
from ivit_i.common.pipeline import Pipeline
from ivit_i.utils.err_handler import handle_exception
from ivit_i.utils.parser import load_json
from ivit_i.utils.draw_tools import draw_fps
from ivit_i.app.handler import get_application
from ivit_i.app.common import CV_WIN

FULL_SCREEN = True
WAIT_KEY_TIME   = 1
SERV    = 'server'
RTSP    = 'rtsp'
GUI     = 'gui'

def init_cv_win():
    logging.info('Init Display Window')
    cv2.namedWindow( CV_WIN, cv2.WND_PROP_FULLSCREEN )
    cv2.setWindowProperty( CV_WIN, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN )

def fullscreen_toggle():
    global FULL_SCREEN
    cv2.setWindowProperty( 
        CV_WIN, cv2.WND_PROP_FULLSCREEN, 
        cv2.WINDOW_FULLSCREEN if FULL_SCREEN else cv2.WINDOW_NORMAL )
    FULL_SCREEN = not FULL_SCREEN

def display(frame, t_wait_key):

    exit_flag = False

    cv2.imshow(CV_WIN, frame)            
    
    key = cv2.waitKey(t_wait_key)
    if key in {ord('q'), ord('Q'), 27}:
        exit_flag = True
    elif key in { ord('a'), 201, 206, 210, 214 }:
        fullscreen_toggle()

    return exit_flag

def get_running_mode(args):
    if(args.server): return SERV
    elif(args.rtsp): return RTSP
    else: return GUI

def check_info(info):
    if info is None: return False
    if info['detections']==[]: return False
    
    return True

def get_gst_pipeline(rtsp_url):
    """
    5M = 4096000
    """
    return \
        'appsrc ' + \
        '! videoconvert ' + \
        '! nvvidconv ! video/x-raw(memory:NVMM), format=(string)I420 ' + \
        '! nvv4l2h264enc bitrate=40000000 insert-sps-pps=true idrinterval=30 profile=0 ' + \
        '! video/x-h264, stream-format=(string)byte-stream ' + \
        f' ! rtspclientsink location={rtsp_url}'


def main(args):

    # Get Mode
    mode = get_running_mode(args)
    t_wait_key  = 0 if args.debug else WAIT_KEY_TIME

    # Load and combine configuration
    app_conf = load_json(args.config)                       # load the configuration of the application
    model_conf = load_json(app_conf['prim']['model_json'])             # load the configuration of the AI model
    total_conf = model_conf.copy()
    total_conf.update(app_conf)

    # Get the target API and load model
    try:
        trg = api.get(total_conf)
        trg.load_model(total_conf)
    except Exception as e:
        handle_exception(error=e, title="Could not get ivit-i API", exit=True)

    # Start inference base on three mode
    src = Pipeline(total_conf['source'], total_conf['source_type'])
    src.start()
    (src_hei, src_wid), src_fps = src.get_shape(), src.get_fps()

    # Inference Mode: Async or Sync ( Default )
    if args.mode==1:
        trg.set_async_mode()

    # Concate RTSP pipeline
    if mode==RTSP:
        rtsp_url = f"rtsp://{args.ip}:{args.port}{args.name}"
        gst_pipeline = get_gst_pipeline(rtsp_url)
        out = cv2.VideoWriter(  gst_pipeline, cv2.CAP_GSTREAMER, 0, 
                                src_fps, (src_wid, src_hei), True )
        logging.info(f'Define Gstreamer Pipeline: {gst_pipeline}')
        # assert not out.isOpened(), "can't open video writer"

    # Setting Application
    try:
        application = get_application(total_conf)
        if total_conf["application"]["name"] != "default":
            application.set_area(frame=src.get_first_frame() if mode==GUI else None)
    except Exception as e:
        handle_exception(error=e, title="Could not load application ... set app to None", exit=False)
    

    # Start inference
    if mode==GUI: init_cv_win()

    # Infer Parameters
    temp_info, cur_info    = None, None
    cur_fps , temp_fps     = 30, src.get_fps()
    fps_buf = []

    try:
        while True:
            
            # Get current frame
            t_start = time.time()
            success, frame = src.read()
            
            # Check frame
            if not success:
                if src.get_type() == 'v4l2':
                    break
                else:
                    application.reset()
                    src.reload()
                    continue

            draw = frame.copy()
            
            # Inference
            temp_info = trg.inference( frame )

            if(check_info(temp_info)):
                cur_info, cur_fps = temp_info, temp_fps
            
            # Drawing result using application and FPS
            if(check_info(cur_info)):
                draw, app_info = application(draw, cur_info)
                draw = draw_fps( draw, cur_fps )

            # Display draw
            if mode==GUI:
                exit_win = display(draw, t_wait_key)
                if exit_win: break

            elif mode==RTSP:
                out.write(draw)

            # Log
            if(check_info(cur_info)): 
                print(cur_info['detections'])

            # Delay inferenece to fix in target fps
            t_cost, t_expect = (time.time()-t_start), (1/src.get_fps())
            if( t_cost<t_expect ):
                time.sleep( (t_expect-t_cost) )
            
            # Calculate FPS
            if(check_info(cur_info)):
                fps_buf.append(int(1/(time.time()-t_start)))
                if(len(fps_buf)>10): fps_buf.pop(0)
                temp_fps = sum(fps_buf)/len(fps_buf)

    except Exception as e:
        print(handle_exception(e))

    finally:
        trg.release()            
        src.release()

        if mode==RTSP:
            out.release()

    logging.warning('Quit')
    sys.exit()
        
if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', help = "The path of application config")
    parser.add_argument('-s', '--server', action="store_true", help = "Server mode, not to display the opencv windows")
    parser.add_argument('-r', '--rtsp', action="store_true", help = "RTSP mode, not to display the opencv windows")
    parser.add_argument('-d', '--debug', action="store_true", help = "Debug mode")
    parser.add_argument('-m', '--mode', type=int, default = 1, help = "Select sync mode or async mode{ 0: sync, 1: async }")
    parser.add_argument('-i', '--ip', type=str, default = '127.0.0.1', help = "The ip address of RTSP uri")
    parser.add_argument('-p', '--port', type=str, default = '8554', help = "The port number of RTSP uri")
    parser.add_argument('-n', '--name', type=str, default = '/mystream', help = "The name of RTSP uri")

    args = parser.parse_args()

    if not ('/' in args.name):
        args.name = f'/{args.name}'

    main(args)
    
