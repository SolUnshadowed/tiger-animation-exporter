import numpy as np

from pygfx import (
    Geometry,
    Line,
    LineSegmentMaterial,
)

class Custom_Axes_Helper(Line):
	"""A WorldObject to indicate the scene's axes.

	Generates three arrows starting at the local origin and pointing into the
	direction of the local x, y, and z-axis respectively. Each arrow is colored
	to represent the respective axis. In particular, the x-axis arrow is red,
	the y-axis arrow is green, and the z-axis arrow is blue.

	Parameters
	----------
	size : float
		The length of the lines in local space.
	thickness : float
		The thickness of the lines in (onscreen) pixels.

	"""

	def __init__(self, size=1.0, thickness=1):
		line_positions = np.array(
			[
				[0, 0, 0],
				[1, 0, 0],
				[0, 0, 0],
				[0, 1, 0],
				[0, 0, 0],
				[0, 0, 1],
			],
			dtype="f4",
		)

		colors = np.array(
			[
				[1, 0, 0, 1],
				[1, 0.6, 0, 1],  # x is red
				[0, 1, 0, 1],
				[0.6, 1, 0, 1],  # y is green
				[0, 0, 1, 1],
				[0, 0.6, 1, 1],  # z is blue
			],
			dtype="f4",
		)

		line_size = np.max([0.005, size])  # ensure > 0.0
		line_positions *= line_size

		geometry = Geometry(positions=line_positions, colors=colors)
		material = LineSegmentMaterial(
			color_mode="vertex", thickness=thickness, aa=True
		)

		super().__init__(geometry, material)
