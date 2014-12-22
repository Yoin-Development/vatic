import merge
import argparse

from turkic.database import session
from turkic.cli import Command

import vision.visualize
import vision.track.interpolation
import vision.pascal

from models import Path, Video

class DumpCommand(Command):
    parent = argparse.ArgumentParser(add_help=False)
    parent.add_argument("slug")
    parent.add_argument("--merge", "-m", action="store_true", default=False)
    parent.add_argument("--merge-threshold", "-t",
                        type=float, default = 0.5)
    parent.add_argument("--worker", "-w", nargs = "*", default = None)

    class Tracklet(object):
        def __init__(self, label, paths, boxes, workers):
            self.label = label
            self.paths = paths
            self.boxes = sorted(boxes, key = lambda x: x.frame)
            self.workers = workers

        def bind(self):
            for path in self.paths:
                self.boxes = Path.bindattributes(path.attributes, self.boxes)

    def getdata(self, args):
        response = []
        video = session.query(Video).filter(Video.slug == args.slug)
        if video.count() == 0:
            print "Video {0} does not exist!".format(args.slug)
            raise SystemExit()
        video = video.one()

        if args.merge:
            for boxes, paths in merge.merge(video.segments,
                                            threshold = args.merge_threshold):
                workers = list(set(x.job.workerid for x in paths))
                tracklet = DumpCommand.Tracklet(paths[0].label.text,
                                                paths, boxes, workers)
                response.append(tracklet)
        else:
            for segment in video.segments:
                for job in segment.jobs:
                    if not job.useful:
                        continue
                    worker = job.workerid
                    for path in job.paths:
                        tracklet = DumpCommand.Tracklet(path.label.text,
                                                        [path],
                                                        path.getboxes(),
                                                        [worker])
                        response.append(tracklet)

        if args.worker:
            workers = set(args.worker)
            response = [x for x in response if set(x.workers) & workers]

        interpolated = []
        for track in response:
            path = vision.track.interpolation.LinearFill(track.boxes)
            tracklet = DumpCommand.Tracklet(track.label, track.paths,
                                            path, track.workers)
            interpolated.append(tracklet)
        response = interpolated

        for tracklet in response:
            tracklet.bind()

        return video, response
