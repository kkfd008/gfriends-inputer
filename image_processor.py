# -*- coding:utf-8 -*-
from PIL import Image, ImageFilter
import shared
import os, sys, re

try:
    from Lib.cv2dnn import find_faces
except:
    pass

def fix_size(type_val, path):
    try:
        pic = Image.open(path)
        if pic.mode != "RGB": pic = pic.convert('RGB')
        (wf, hf) = pic.size
        
        if not 2 / 3 - 0.02 <= wf / hf <= 2 / 3 + 0.02:
            if type_val == 1:
                fixed_pic = pic.resize((int(wf), int(3 / 2 * wf)))
                fixed_pic = fixed_pic.filter(ImageFilter.GaussianBlur(radius=50))
                fixed_pic.paste(pic, (0, int((3 / 2 * wf - hf) / 2)))
                fixed_pic.save(path, quality=95)
            elif type_val == 2:
                fixed_pic = pic.crop((int(wf / 2 - 1 / 3 * hf), 0, int(wf / 2 + 1 / 3 * hf), int(hf)))
                fixed_pic.save(path, quality=95)
            elif type_val == 3:
                x_nose, _ = find_faces(pic)
                x_left = wf - 2 / 3 * hf if x_nose + 1 / 3 * hf > wf else (0 if x_nose - 1 / 3 * hf < 0 else x_nose - 1 / 3 * hf)
                fixed_pic = pic.crop((x_left, 0, x_left + 2 / 3 * hf, hf))
                fixed_pic.save(path, quality=95)
        return True
    except Exception as e:
        shared.logger.error(f'{path} 头像优化失败: {e}')
        failed_dir = re.sub(r'(.*/)(.*)', r'\1Failed/', path)
        failed_path = re.sub(r'(.*/)(.*)', r'\1Failed/\2', path)
        if not os.path.exists(failed_dir): os.makedirs(failed_dir)
        if os.path.exists(failed_path): os.remove(failed_path)
        os.rename(path, failed_path)
        return False