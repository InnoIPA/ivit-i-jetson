from .cls import LIST as cls_list
from .darknet import LIST as obj_list
from .seg import LIST as seg_list
from .pose import LIST as pose_list

APP_LIST = {
    'cls'   : cls_list,
    'darknet'   : obj_list,
    'seg'   : seg_list,
    'pose'  : pose_list,
}
