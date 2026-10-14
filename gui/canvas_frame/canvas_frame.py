import pygfx
import pygfx as gfx
import pygfx.animation as pygfx_anim
import numpy as np
from PySide6.QtWidgets import (
	QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
	QSlider, QDoubleSpinBox, QLabel, QPlainTextEdit
)
from PySide6.QtCore import Slot, Qt, Signal
from rendercanvas.qt import QRenderWidget
from dataclasses import dataclass

from libs.matrix_operations import glm_decompose_mat4

from src.tag_readers.animation.read_animation import Animation_Data
from src.tag_readers.skeleton.read_skeleton import Skeleton, transform_to_np_matrix
from src.fnv_hashes.int_to_hex import u32_to_be_hex

from gui.canvas_frame.custom_axes_helper import Custom_Axes_Helper
from gui.canvas_frame.custom_skeleton_helper import Custom_Skeleton_Helper
from gui.worker_types import Animation_Model, Model_Properties, Render_Data


clock = gfx.Clock()


def animation_fmt(animation: Animation_Data) -> str:
	animation_header = animation.animation_header

	rig_lines = ["Runtime rig components:"]
	for comp in animation.runtime_rig_components.payload:
		fnv_hash = u32_to_be_hex(comp.hash)
		rig_lines.append(f"\thash: {fnv_hash}, count: {comp.control_count}")
	rig_components_str = "\n".join(rig_lines)

	static_bones_header = getattr(animation, "static_bones_header", None)
	if static_bones_header:
		static_bones_str = (
			f"Static bones header:\n"
			f"\tframes: {static_bones_header.frame_count}\n"
			f"\tcodec type: {static_bones_header.codec_type}\n"
			f"\tscale_stream_count: {static_bones_header.scale_stream_count}\n"
			f"\trotation_stream_count: {static_bones_header.rotation_stream_count}\n"
			f"\ttranslation_stream_count: {static_bones_header.translation_stream_count}"
		)
	else:
		static_bones_str = "Static bones header:\n\tno"

	animated_bones_header = getattr(animation, "animated_bones_header", None)
	if animated_bones_header:
		animated_bones_str = (
			f"Animated header:\n"
			f"\tcodec type: {animated_bones_header.codec_type}\n"
			f"\tscale_stream_count: {animated_bones_header.scale_stream_count}\n"
			f"\trotation_stream_count: {animated_bones_header.rotation_stream_count}\n"
			f"\ttranslation_stream_count: {animated_bones_header.translation_stream_count}"
		)
	else:
		animated_bones_str = "Animated header:\n\tno"

	return (
		f"Animation header:\n"
		f"\tframes: {animation_header.frame_count}\n"
		f"\tanimation hash: {u32_to_be_hex(animation_header.animation_hash)}\n"
		f"\tnode count: {animation_header.node_count}\n"
		f"\trig control count: {animation_header.rig_control_count}\n"
		f"\tanimation type: {animation_header.animation_type.name}\n\n"
		f"{rig_components_str}\n\n"
		f"{static_bones_str}\n\n"
		f"{animated_bones_str}\n\n"
	)


@dataclass
class Animation_Playback_State:
	is_paused: bool
	speed: float
	fps: float
	total_frames: int
	is_moved: bool


class Canvas_Frame(QWidget):
	canvas: QRenderWidget
	renderer: gfx.WgpuRenderer
	scene: gfx.Scene
	controller: gfx.OrbitController
	skeleton_helper: Custom_Skeleton_Helper | None
	skeleton: gfx.Skeleton | None
	group: gfx.Group | None
	root_bone: gfx.Bone | None
	mixer: gfx.AnimationMixer | None
	bones: list[gfx.Bone]
	action: gfx.AnimationAction | None
	light: gfx.DirectionalLight
	playback_state: Animation_Playback_State
	animation_data = Signal(str)
	render_status: bool = True


	def __init__(self, parent=None):
		super().__init__(parent)

		self.canvas = QRenderWidget(parent=self)
		self.renderer = gfx.WgpuRenderer(self.canvas)
		self.scene = gfx.Scene()

		background = gfx.Background.from_color("#202020")
		self.scene.add(background)

		self.grid = gfx.GridHelper()
		self.grid.local.y = -0.001
		self.scene.add(self.grid)

		self.axes_helper = Custom_Axes_Helper(size=10, thickness=1)
		self.axes_helper.local.y = 0.001
		self.scene.add(self.axes_helper)

		self.light = gfx.DirectionalLight()
		self.scene.add(self.light)
		self.light.local.position = (300, 300, 300)

		self.scene.add(gfx.AmbientLight())

		self.camera = gfx.OrthographicCamera(110, 110)
		self.skeleton_helper = None
		self.skeleton = None
		self.group = None
		self.root_bone = None
		self.bones = []
		self.mixer = gfx.AnimationMixer()
		self.action = None

		self.playback_state = Animation_Playback_State(
			is_paused = True,
			speed= 1.0,
			fps = 30.0,
			total_frames = 0,
			is_moved= False
		)

		self.controller = gfx.OrbitController(self.camera, register_events=self.renderer)

		main_layout = QVBoxLayout(self)
		main_layout.setContentsMargins(0, 0, 0, 0)
		main_layout.addWidget(self.canvas)

		controls_layout = QHBoxLayout()
		controls_layout.setContentsMargins(10, 5, 10, 5)

		self.play_pause_button = QPushButton("Play") # is_paused in state is true
		self.play_pause_button.setFixedWidth(60)
		self.play_pause_button.clicked.connect(self.toggle_play_pause)
		controls_layout.addWidget(self.play_pause_button)

		self.frame_slider = QSlider(Qt.Orientation.Horizontal)
		self.frame_slider.setRange(0, 0)
		self.frame_slider.sliderPressed.connect(self.on_slider_pressed)
		self.frame_slider.sliderReleased.connect(self.on_slider_released)
		self.frame_slider.valueChanged.connect(self.on_slider_value_changed)
		controls_layout.addWidget(self.frame_slider)

		self.frame_count_label = QLabel("0 / 0")
		self.frame_count_label.setFixedWidth(80)
		controls_layout.addWidget(self.frame_count_label)

		playback_speed_label = QLabel("Speed:")
		controls_layout.addWidget(playback_speed_label)

		self.spin_speed = QDoubleSpinBox()
		self.spin_speed.setRange(0.1, 5.0)
		self.spin_speed.setSingleStep(0.1)
		self.spin_speed.setValue(1.0)
		self.spin_speed.setSuffix("x")
		self.spin_speed.valueChanged.connect(self.on_speed_changed)
		controls_layout.addWidget(self.spin_speed)

		main_layout.addLayout(controls_layout)

		self.renderer.render(self.scene, self.camera)
		self.canvas.request_draw(self.animate)


	@Slot(object)
	def set_render_data(self, render_data: Render_Data):
		self.clear_animation()

		skeleton = render_data.skeleton
		# cleanup
		if self.skeleton is not None:
			self.skeleton = None

		if self.root_bone is not None:
			self.scene.remove(self.root_bone)
			self.bones = []

		if self.skeleton_helper is not None:
			self.scene.remove(self.skeleton_helper)
			self.skeleton_helper = None

		if self.group is not None:
			self.scene.remove(self.group)

		self.group = gfx.Group()
		self.scene.add(self.group)

		# skeleton things
		bones = []

		if skeleton is not None:
			for i in range(len(skeleton.bone_to_parent_offset)):
				parent_offset = skeleton.bone_to_parent_offset[i]
				node_def = skeleton.node_defs[i]

				bone = gfx.Bone(str(node_def.bone_hash))

				if node_def.parent_node_index > -1:
					bones[node_def.parent_node_index].add(bone)

				bone.add(Custom_Axes_Helper(size=0.05, thickness=1))

				sc, rot, tr = glm_decompose_mat4(parent_offset)
				bone.local.position = np.array([tr[0], tr[1], tr[2]])
				bone.local.rotation = np.array([rot[1], rot[2], rot[3], rot[0]])
				bone.local.scale = np.array([sc[0], sc[1], sc[2]])

				bones.append(bone)

			self.bones = bones

			self.root_bone = bones[0]
			self.scene.add(self.root_bone)
			self.skeleton_helper = Custom_Skeleton_Helper(self.root_bone, 0.5)
			self.scene.add(self.skeleton_helper)

			#inv_bind_matrices = [transform_to_np_matrix(transform) for transform in skeleton.default_inv_obj_space_tr]

			#self.skeleton = gfx.Skeleton(self.bones, inv_bind_matrices)
			self.skeleton = gfx.Skeleton(self.bones)

		# 3d model stuff
		model_properties = render_data.model_properties

		for model_prop in model_properties:
			if model_prop is None:
				continue

			normals = model_prop.normal_buffer

			if model_prop.skin_indices is not None and model_prop.skin_weights is not None and self.skeleton is not None:
				geom = pygfx.Geometry(
					positions=model_prop.position_buffer,
					normals=normals,
					indices=model_prop.index_buffer,
					skin_indices=model_prop.skin_indices,
					skin_weights=model_prop.skin_weights
				)

				mesh = pygfx.SkinnedMesh(geom, pygfx.MeshPhongMaterial())

				mesh.world.position = model_prop.translation
				mesh.local.scale = model_prop.scale

				mesh.bind(self.skeleton)

			else:
				geom = pygfx.Geometry(
					positions=model_prop.position_buffer,
					normals=normals,
					indices=model_prop.index_buffer
				)

				mesh = pygfx.Mesh(geom, pygfx.MeshPhongMaterial())
				mesh.world.position = model_prop.translation
				mesh.local.scale = model_prop.scale

			self.group.add(mesh)

	def clear_animation(self):
		if self.action is not None:
			self.action.stop()

		self.action = None
		self.playback_state.total_frames = 0
		self.frame_slider.blockSignals(True)
		self.frame_slider.setRange(0, 0)
		self.frame_slider.blockSignals(False)
		self.frame_count_label.setText("0 / 0")

	def set_animation(self, animation: Animation_Model):
		self.clear_animation()

		frame_count = animation.animation_data.animation_header.frame_count
		self.playback_state.total_frames = frame_count

		t_array = np.arange(0, frame_count, dtype=np.float32) / self.playback_state.fps
		tracks = []

		for i in range(len(animation.tracks)):
			track_group = animation.tracks[i]
			bone_name = str(track_group.bone_name_hash)

			track_pos = pygfx_anim.KeyframeTrack(
				bone_name, self.bones[i], "translation",
				t_array, track_group.translations.copy(), pygfx_anim.LinearInterpolant
			)
			track_rot = pygfx_anim.KeyframeTrack(
				bone_name, self.bones[i], "rotation",
				t_array, track_group.rotations.copy(), pygfx_anim.QuaternionLinearInterpolant
			)
			track_sc = pygfx_anim.KeyframeTrack(
				bone_name, self.bones[i], "scale",
				t_array, track_group.scales.copy(), pygfx_anim.LinearInterpolant
			)
			tracks.append(track_pos)
			tracks.append(track_rot)
			tracks.append(track_sc)

		clip = gfx.AnimationClip("", frame_count / self.playback_state.fps, tracks)
		self.action = self.mixer.clip_action(clip)

		self.action.time_scale = self.playback_state.speed
		self.action.paused = self.playback_state.is_paused

		self.action.play()

		self.frame_slider.blockSignals(True)
		self.frame_slider.setRange(0, max(0, frame_count - 1))
		self.frame_slider.setValue(0)
		self.frame_slider.blockSignals(False)
		self.frame_count_label.setText(f"0 / {frame_count - 1}")

		self.animation_data.emit(animation_fmt(animation.animation_data))

	def toggle_play_pause(self):
		self.playback_state.is_paused = not self.playback_state.is_paused
		if self.action is not None:
			self.action.paused = self.playback_state.is_paused

		self.play_pause_button.setText("Play" if self.playback_state.is_paused else "Pause")

	def on_speed_changed(self, value: float):
		self.playback_state.speed = value
		if self.action is not None:
			self.action.time_scale = value

	def on_slider_pressed(self):
		self.playback_state.is_moved = True

	def on_slider_released(self):
		self.playback_state.is_moved = False

	def on_slider_value_changed(self, frame_index: int):
		if self.action is None or self.playback_state.total_frames == 0:
			return

		target_time = frame_index / self.playback_state.fps
		self.action.time = target_time
		self.mixer.update(0)
		self.frame_count_label.setText(f"{frame_index} / {self.playback_state.total_frames - 1}")

	def animate(self):
		dt = clock.get_delta()

		if self.mixer is not None:
			self.mixer.update(dt)

		if self.action is not None and not self.playback_state.is_moved and self.playback_state.total_frames > 0:
			current_time = self.action.time
			current_frame = int(current_time * self.playback_state.fps) % self.playback_state.total_frames

			self.frame_slider.blockSignals(True)
			self.frame_slider.setValue(current_frame)
			self.frame_slider.blockSignals(False)
			self.frame_count_label.setText(f"{current_frame} / {self.playback_state.total_frames - 1}")

		if self.skeleton is not None:
			self.skeleton.update()

		if self.skeleton_helper is not None:
			self.skeleton_helper.update()

		self.renderer.render(self.scene, self.camera)

		if self.render_status:
			self.canvas.request_draw(self.animate)

	def shutdown(self):
		self.render_status = False
		self.scene.clear()
		self.canvas.close()
