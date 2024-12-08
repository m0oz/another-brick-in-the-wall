import os
from dataclasses import asdict
from math import floor

from flask import Flask, jsonify, request, send_file, send_from_directory
from flask_cors import CORS

from lib.bonds import Bond, BrickWidth
from lib.wall_state import Stride, WallState, find_best_stride

FULL_BRICK_WIDTH = 220
COURSE_HEIGHT = 65.5
STRIDE_WIDTH = floor((800 / FULL_BRICK_WIDTH) * BrickWidth.FULL)
STRIDE_HEIGHT = floor(1300 / COURSE_HEIGHT)


class App:
    def __init__(self):
        self.app = Flask(__name__, static_folder="frontend/dist")
        CORS(self.app)
        self.wall = WallState()
        self.brick_generator = None
        self.current_stride = Stride(0, 0, STRIDE_WIDTH, STRIDE_HEIGHT)

        # Register routes
        self.app.route("/", defaults={"path": ""})(self.serve)
        self.app.route("/<path:path>")(self.serve)
        self.app.route("/api/init", methods=["POST"])(self.init_wall)
        self.app.route("/api/next")(self.next_block)
        self.app.route("/api/reset", methods=["POST"])(self.reset)

    def serve(self, path):
        if path and os.path.exists(os.path.join(self.app.static_folder, path)):
            return send_from_directory(self.app.static_folder, path)
        return send_file(os.path.join(self.app.static_folder, "index.html"))

    def init_wall(self):
        data = request.json
        width = data.get("width")
        height = data.get("height")
        bond = data.get("bond")
        mode = data.get("mode")

        try:
            if bond == "flemish":
                self.wall.initialize_wall(width * BrickWidth.HALF, height, Bond.FLEMISH)
            elif bond == "english":
                self.wall.initialize_wall(width * BrickWidth.HALF, height, Bond.ENGLISH)
            elif bond == "wildverband":
                self.wall.initialize_wall(width * BrickWidth.HALF, height, Bond.WILD)
            else:
                self.wall.initialize_wall(
                    width * BrickWidth.HALF, height, Bond.STRETCHER
                )
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

        # Choose brick placement strategy based on mode
        if mode == "left-to-right":
            self.brick_generator = self.wall.place_bricks_left_to_right()
        elif mode == "optimal-strides":
            self.brick_generator = self.wall.place_bricks_for_stride(
                stride=self.current_stride
            )
        else:
            return jsonify({"error": "Invalid mode specified"}), 400

        return jsonify(self.wall.to_dict())

    def next_block(self):
        if self.brick_generator is None:
            return jsonify({"error": "Wall not initialized"}), 400

        brick = next(self.brick_generator, None)

        if brick is None:
            self.current_stride = find_best_stride(
                self.wall, STRIDE_WIDTH, STRIDE_HEIGHT
            )
            print(
                f"Next optimal stride {self.current_stride.origin_x}, {self.current_stride.origin_y}"
            )
            self.brick_generator = self.wall.place_bricks_for_stride(
                self.current_stride
            )
            brick = next(self.brick_generator, None)

        print(self.current_stride)
        response = {
            "wall": self.wall.to_dict(),
            "stride": self.current_stride,
        }

        return jsonify(response)

    def reset(self):
        self.wall.reset()
        self.brick_generator = None
        return jsonify(asdict(self.wall))

    def run(self, host="0.0.0.0", port=8000, debug=True):
        self.app.run(host=host, port=port, debug=debug)


app = App()

if __name__ == "__main__":
    app.run()
