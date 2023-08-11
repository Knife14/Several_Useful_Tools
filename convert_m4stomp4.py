# -*- coding: utf-8 -*- #

# -----------------------------
# Topic: Convert m4s video to mp4 in bilibili
# Author: m14
# Created: 2023.08.11
# History:
#    <author>    <version>    <time>        <desc>
#    m14         v0.1    2023/08/11    build the basic
# -----------------------------

import os
import json
import subprocess


def check_batch_folder(folder_path):
    if not os.path.exists(folder_path):
        return []
    if not os.path.isdir(folder_path):
        return []
    
    sub_items = os.listdir(folder_path)
    if folders := [item for item in sub_items if os.path.isdir(os.path.join(folder_path, item))]:
        return folders
    
    return []

def decode_m4s_file(file_path):
    with open(file_path, 'r+b') as file:
        content = file.read()
        tl_latest = content.lstrip(b'0')
        file.seek(0)
        file.write(tl_latest)
        file.truncate()

def check_video_folder(file_path):
    sub_items = os.listdir(file_path)

    video = {}
    for items in sub_items:
        if items == '.videoInfo':
            videoInfo_file = open(os.path.join(file_path, items), 'rb')
            videoInfo = json.loads(videoInfo_file.read())
            video['videoInfo'] = videoInfo
        if 'm4s' in items:
            m4s_path = os.path.join(file_path, items)
            decode_m4s_file(m4s_path)
            if 'video' not in video:
                video['video'] = []
            video['video'].append(m4s_path)
    
    return video

def convert_m4s_mp4(curr_video, output_path):
    if not curr_video:
        return
    
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    
    video_name = curr_video['videoInfo']['title'] + '.mp4'
    print(curr_video['videoInfo']['itemId'], ':', video_name, 'is converting...')
    output = os.path.join(output_path, curr_video['videoInfo']['title'] + '.mp4')
    ffmpeg_command = ['ffmpeg', '-i', curr_video['video'][0], '-i', curr_video['video'][1], '-c', 'copy', output, '-y']
    try:
        subprocess.run(ffmpeg_command, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT, check=True)
        print(video_name, 'converted successfully.')
    except subprocess.CalledProcessError as e:
        print(video_name, 'converted unsuccessfully.')
    

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--folder", type=str, required=True,
                        help="batch processing conversion")
    parser.add_argument("-o", "--output", type=str, required=True,
                        help="output folder path")
    args = parser.parse_args()
    
    videos = check_batch_folder(args.folder)
    if not videos:
        video = check_video_folder(args.folder)
        convert_m4s_mp4(video, args.output)
    
    for video in videos:
        video = check_video_folder(os.path.join(args.folder, video))
        convert_m4s_mp4(video, args.output)
