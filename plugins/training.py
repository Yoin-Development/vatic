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
        parser = argparse.ArgumentParser(parents=[self.parent])
        parser.add_argument("output")
        parser.add_argument("--width", default=720, type=int)
        parser.add_argument("--height", default=480, type=int)
        parser.add_argument("--modulus", default=100, type=int)
        parser.add_argument("--number_samples", default=10, type=int)
        parser.add_argument("--x", default=128, type=int)
        parser.add_argument("--y", default=128, type=int)
        parser.add_argument("--no-resize", action="store_true", default=False)
        parser.add_argument("--positive", action="store_true", default=False)
        parser.add_argument("--negative", action="store_true", default=False)
        parser.add_argument("--rotate", action="store_true", default=False)
        return parser

    def generate_random_box(self, max_width, max_height, rect_dims, frame):
        w, h = rect_dims
        x = random.randrange(0, max_width - (w + 1))
        y = random.randrange(0, max_height - (h + 1))

        return Box(x, y, x + w, y + h, frame=frame)

    def delete_overlapping(self, box, box_list, overlap=0.05):
        for i, box_tmp in enumerate(box_list):
            if box.frame == box_tmp.frame and \
                    box.percentoverlap(box_tmp) > 0.05:
                box_list.pop(i)

    def save_box(self, output_dir, box, image, rect_dims, frame_number, rotate=0):
        w, h = tuple(map(lambda x: int(math.ceil(x / 2)), rect_dims))

        box_x, box_y = box.center

        xmin, ymin = box_x - w, box_y - h
        xmax, ymax = box_x + w, box_y + h

        image = image.rotate(rotate)
        img = image.crop((xmin, ymin, xmax, ymax))
        img.save("{0}/{1}_{2}.jpg".format(output_dir, frame_number, rotate))

    def create_negatives(self, video, data, args, skipframes=20, rect_dims=(128, 128)):
        output_dir = "{0}/neg".format(args.output)
        output_filename = "{}/neg_samples.info".format(args.output)

        try:
            os.makedirs(output_dir)
            output_file = open(negative_filename, "w+")
        except OSError as e:
            print "Could not create directory: {0}".format(e)
            raise

        frame_annotated = 0
        total_frames = video.totalframes

        # get a list of all boxes
        generated_boxes = []

        for frame in range(total_frames):
            generated_boxes.append(self.generate_random_box(video.width,
                video.height, rect_dims, frame))

        for track in data:
            for box in track.boxes:
                # delete from gen boxes if there is an overlapping box
                self.delete_overlapping(box, generated_boxes)

        for gen_box in generated_boxes:
            frame_number = gen_box.frame
            image = video[frame_number]

            self.save_box(args.output, gen_box, image, rect_dims, frame_number,
                    rotate=0)

            if args.rotate:
                for deg in [90, 180, 270]:
                    self.save_box(output_dir, gen_box, image, 
                            frame_number, rotate=deg)

        output_file.close()

    def create_positives(self, video, data, args, skipframes=20,
            rect_dims=(128, 128)):
        output_dir = "{0}/pos".format(args.output)
        output_filename = "{}/pos_samples.info".format(args.output)

        try:
            os.makedirs(output_dir)
            output_file = open(output_filename, "w+")
        except OSError as e:
            print "Could not create directory: {0}".format(e)
            raise

        for id, track in enumerate(data):
            for box in track.boxes:
                x, y, w, h = [0, 0, 0, 0]

                if box.occluded > 0:
                    continue

                if box.lost > 0:
                    continue

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

                while (x + w) > video.width:
                    x-=1

                while x < 0:
                    x+=1

                while (y + h) > video.height:
                    y-=1

                while y < 0:
                    y+=1

                degrees = 0
                #cx = x + w / 2
                #cy = y + h / 2
                #sq = int(math.ceil(math.sqrt(w**2+h**2)))
                image = video[box.frame]
                #image = video[box.frame].crop((cx - sq / 2, cy - sq / 2,
                #                        cx + sq / 2, cy + sq / 2))
                frame_number = box.frame

                self.save_box(output_dir, box, image, rect_dims, frame_number,
                        rotate=0)

                if args.rotate:
                    for deg in [90, 180, 270]:
                        self.save_box(output_dir, box, image, rect_dims,
                                frame_number, rotate=deg)

    def __call__(self, args):
        try:
            os.makedirs("{0}".format(args.output))
        except OSError as e:
            print "Could not create directory: {0}".format(e)
            raise

        video, data = self.getdata(args)

        random.seed(42)

        if args.negative:
            rect_dims = args.x, args.y
            self.create_negatives(video, data, args, rect_dims=rect_dims)

        # prepend class label
        if args.positive:
            rect_dims = args.x, args.y
            self.create_positives(video, data, args, rect_dims=rect_dims)
