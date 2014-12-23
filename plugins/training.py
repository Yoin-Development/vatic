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
        parser.add_argument("--jump_frames", default=1, type=int)
        parser.add_argument("--dimensions", default=False, type=str)
        parser.add_argument("--no-resize", action="store_true", default=False)
        parser.add_argument("--positive", action="store_true", default=False)
        parser.add_argument("--negative", action="store_true", default=False)
        parser.add_argument("--rotate", action="store_true", default=False)
        return parser

    def resize_with_dims(self, box, args):
        scale = args.scale
        w, h = tuple(map(float, args.dimensions.split("x")))

        s = w / video.width

        if s * video.height > h:
            s = h / video.height
        scale = s
        return box.transform(scale)

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

    def write_to_file(self, output_file, output_list):
        output_file = open(output_file, "w+")
        output_file.write("\n".join(output_list))
        output_file.close()

    def save_box(self, output_dir, box, image, rect_dims, frame_number,
            rotate=0, crop=False, output_list=None, prefix=""):
        w, h = box.size
        xmin, ymin = box.xtl, box.ytl
        img = image.rotate(rotate)

        if crop:
            w_half, h_half = tuple(map(lambda x: int(math.ceil(x / 2)), rect_dims))
            box_x, box_y = box.center
            xmin, ymin = box_x - w_half, box_y - h_half
            xmax, ymax = box_x + w_half, box_y + h_half
            img = image.crop((xmin, ymin, xmax, ymax))

        filename = "{output_dir}/{frame_number}_{x}_{y}_{w}_{h}.jpg".format(
                        output_dir=output_dir, frame_number=frame_number,
                        x=xmin, y=ymin, w=w, h=h)

        if output_list is not None:
            # opencvsampletraining outputfile
            output_string = "{prefix}{filename} {num_objects} {xmin} {ymin} {w} {h}".format(
                                prefix=prefix, filename=os.path.basename(filename),
                                num_objects=1, xmin=xmin, ymin=ymin,
                                w=w, h=h)
            output_list.append(output_string)

        img.save(filename)

    def create_negatives(self, video, data, args, jump_frames=1, rect_dims=(128, 128)):
        output_dir = "{0}/neg".format(args.output)
        output_filename = "{}/neg_samples.info".format(args.output)
        output_list = []

        try:
            os.makedirs(output_dir)
        except OSError as e:
            print "Could not create directory: {0}".format(e)
            raise

        frame_annotated = 0
        total_frames = video.totalframes

        # get a list of all boxes
        generated_boxes = []

        for frame in range(0, total_frames, jump_frames):
            generated_boxes.append(self.generate_random_box(video.width,
                video.height, rect_dims, frame))

        for track in data:
            for box in track.boxes:
                # delete from gen boxes if there is an overlapping box
                self.delete_overlapping(box, generated_boxes)

        for gen_box in generated_boxes:
            frame_number = gen_box.frame
            image = video[frame_number]

            self.save_box(output_dir, gen_box, image, rect_dims, frame_number,
                    rotate=0, crop=True, output_list=output_list, prefix="neg/")

            if args.rotate:
                for deg in [90, 180, 270]:
                    self.save_box(output_dir, gen_box, image, frame_number, 
                            crop=True, rotate=deg, output_list=output_list,
                            prefix="neg/")

        self.write_to_file(output_filename, output_list)

    def create_positives(self, video, data, args, jump_frames=1,
            rect_dims=(128, 128)):
        output_dir = "{0}/samples".format(args.output)
        output_filename = "{}/pos_samples.info".format(args.output)
        output_list = []

        try:
            os.makedirs(output_dir)
        except OSError as e:
            print "Could not create directory: {0}".format(e)
            raise

        for id, track in enumerate(data):
            for i in range(0, len(track.boxes), jump_frames):
                box = track.boxes[i]

                if box.occluded > 0 or box.lost > 0:
                    continue

                # example use: resize box by dimensions of original video
                if args.dimensions:
                    box = resize_with_dims(box, args)

                frame_number = box.frame
                image = video[frame_number]

                self.save_box(output_dir, box, image, rect_dims,
                        frame_number, rotate=0, crop=False,
                        output_list=output_list, prefix="sample/")

                if args.rotate:
                    for deg in [90, 180, 270]:
                        self.save_box(output_dir, tmp_box, image, rect_dims,
                                frame_number, rotate=deg, crop=False,
                                output_list=output_list, prefix="sample/")

        self.write_to_file(output_filename, output_list)

        #box_w = box.width
        #box_h = box.height
        #box_x, box_y = box.center

        # Resize height
        #if box.width > box.height:
        #    x = box.xtl
        #    y = box.center[1] - box.width / 2
        #    w = box.width
        #    h = box.width
        ## Resize width
        #elif box.height > box.width:
        #    x = box.center[0] - box.height / 2
        #    y = box.ytl
        #    w = box.height
        #    h = box.height
        #else:
        #    # Resize whole
        #    x = box.xtl
        #    y = box.ytl
        #    w = box.width
        #    h = box.height
        #while (x + w) > video.width:
        #    x-=1

        #while x < 0:
        #    x+=1

        #while (y + h) > video.height:
        #    y-=1

        #while y < 0:
        #    y+=1

        #degrees = 0
        #cx = x + w / 2
        #cy = y + h / 2
        #sq = int(math.ceil(math.sqrt(w**2 + h**2)))
        #tmp_box = Box(x, y, x + w, y + h)

        #image = video[box.frame]
        #image = video[box.frame].crop((cx - sq / 2, cy - sq / 2,
        #                        cx + sq / 2, cy + sq / 2))

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
            self.create_negatives(video, data, args, rect_dims=rect_dims,
                    jump_frames=args.jump_frames)

        # prepend class label
        if args.positive:
            rect_dims = args.x, args.y
            self.create_positives(video, data, args, rect_dims=rect_dims, 
                    jump_frames=args.jump_frames)
