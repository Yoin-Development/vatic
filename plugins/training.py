import os
import sys
import math
import random
import argparse

from vision import Box
import vision.visualize
import vision.track.interpolation

from turkic.cli import handler

from extendturkic import DumpCommand

@handler("Create samples from the annotated frames")
class createsample(DumpCommand):
    def setup(self):
        parser = argparse.ArgumentParser(parents = [self.parent])
        parser.add_argument("output")
        parser.add_argument("--width", default=720, type=int)
        parser.add_argument("--height", default=480, type=int)
        parser.add_argument("--modulus", default=100, type=int)
        parser.add_argument("--number_samples", default=10, type=int)
        parser.add_argument("--no-resize",
            action="store_true", default = False)
        parser.add_argument("--positive", action="store_true", default=False)
        parser.add_argument("--negative", action="store_true", default=False)
        return parser

    def __call__(self, args):
        try:
            os.makedirs("{0}".format(args.output))
            os.makedirs("{0}/pos".format(args.output))
            os.makedirs("{0}/neg".format(args.output))
        except OSError as e:
            print "Could not create directory: {0}".format(e)
            sys.exit(0)

        video, data = self.getdata(args)

        random.seed(42)

        if args.negative:
            frame = 0
            totalframes = video.totalframes

            while frame < totalframes:
                frame += 1
                if frame % 20 != 0:
                    continue

                count = 0
                frame_annotated = 0

                while count < args.number_samples:
                    w = 128
                    h = 128
                    x = random.randrange(0, video.width-w)
                    y = random.randrange(0, video.height-h)

                    tmp_box = Box(x, y, x+w, y+h)
                    overlapping = False

                    for track in data:
                        for box in track.boxes:
                            if box.frame != frame:
                                continue

                            if box.occluded > 0:
                                continue
                            if box.lost > 0:
                                continue

                            frame_annotated += 1

                            if box.percentoverlap(tmp_box) > 0.05:
                                overlapping = True

                            # frame found, break
                            break

                        # continue searching if frame was not overlapping
                        if overlapping:
                            print "overlapping 1"
                            break

                    # continue with new box if frame overlapped
                    if overlapping:
                        print "overlapping 2"
                        continue

                    # check if frame any annotated
                    if frame_annotated > 0:
                        image = video[frame]
                        degrees = 0
                        cx = x+w/2
                        cy = y+h/2
                        sq = int(math.ceil(math.sqrt(w**2+h**2)))
                        image = image.crop((cx-sq/2, cy-sq/2,
                                            cx+sq/2, cy+sq/2))

                        #image = image.crop((x,y,x+w,y+h))

                        while degrees <= 90:
                            img = image.rotate(degrees)
                            iw, ih = img.size
                            ix = iw/2-w/2
                            iy = ih/2-h/2
                            img = img.crop((ix,iy,ix+w,iy+h))
                            print "save"
                            print args.output
                            img.save("{0}/neg/{1}_{2}_{3}_{4}.jpg".format(
                                args.output, video.slug, frame, count, degrees))
                            degrees += 30

                        count += 1
                    # else continue to main loop
                    else:
                        break

        i = 0
        # prepend class label
        if args.positive:
            for id, track in enumerate(data):
                for box in track.boxes:
                    x,y,w,h = [0,0,0,0]

                    if box.occluded > 0:
                        continue
                    if box.lost > 0:
                        continue

                    i += 1
                    if i % args.modulus == 0:
                        break

                    if box.width > box.height:
                        # Resize height
                        x = box.xtl
                        y = box.center[1] - box.width/2
                        w = box.width
                        h = box.width

                    elif box.height > box.width:
                        # Resize width
                        x = box.center[0] - box.height/2
                        y = box.ytl
                        w = box.height
                        h = box.height
                    else:
                        # Resize whole
                        x = box.xtl
                        y = box.ytl
                        w = box.width
                        h = box.height

                    while (x + w) > video.width: x-=1
                    while x < 0: x+=1
                    while (y + h) > video.height: y-=1
                    while y < 0: y+=1

                    degrees = 0
                    cx = x+w/2
                    cy = y+h/2
                    sq = int(math.ceil(math.sqrt(w**2+h**2)))
                    image = video[box.frame].crop((cx-sq/2, cy-sq/2,
                                            cx+sq/2, cy+sq/2))

                    while degrees <= 90:
                        #image = video[box.frame].crop((x,y,x+w,y+h))
                        img = image.rotate(degrees)
                        iw, ih = img.size
                        ix = iw/2-w/2
                        iy = ih/2-h/2
                        img = img.crop((ix,iy,ix+w,iy+h))

                        img.save("{0}/pos/{1}_{2}_{3}_{4}.jpg".format(
                            args.output, video.slug, box.frame, id, degrees))
                        degrees += 30
