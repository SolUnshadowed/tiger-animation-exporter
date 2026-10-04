from libs.tiger_pkg.game_version import Game_Version


'''
d1_devalpha
80800AD5 s_animation_clip
808004C5 s_pattern_component
80800A98 s_runtime_rig_configuration_spec
80800DC9 s_skeleton_spec
808003D1 s_entity
? s_entity_model_mesh
? s_entity_model

d1_roi 
808005A1 s_animation_clip
80800861 s_pattern_component
808008B2 s_runtime_rig_configuration_spec
808006BD s_skeleton_spec
80800734 s_entity
80801BBF s_entity_model_mesh
80801AB5 s_entity_model

d2_eof
80808BE0 s_animation_clip
80809B06 s_pattern_component
80808B66 s_runtime_rig_configuration_spec
808081DD s_skeleton_spec
80809AD8 s_entity
80806EC5 s_entity_model_mesh
80806F07 s_entity_model

marathon
8080AE01 s_animation_clip
8080BADB s_pattern_component
8080AD85 s_runtime_rig_configuration_spec
80809FB6 s_skeleton_spec
8080BAAD s_entity (s_pattern??)
 s_entity_model_mesh
 s_entity_model

'''

s_animation_clip_refs: dict[Game_Version, int] = {
	Game_Version.D1_DEV_ALPHA: 0x80800AD5,
	Game_Version.D1_ROI: 0x808005A1,
	Game_Version.D2_EOF: 0x80808BE0,
	Game_Version.MARATHON: 0x8080AE01,
}

s_pattern_refs = {
	Game_Version.D1_DEV_ALPHA: 0x808003D1,
	Game_Version.D1_ROI: 0x80800734,
	Game_Version.D2_EOF: 0x80809AD8,
	Game_Version.MARATHON: 0x8080BAAD,

}

s_pattern_component_refs: dict[Game_Version, int] = {
	Game_Version.D1_DEV_ALPHA: 0x808004C5,
	Game_Version.D1_ROI: 0x80800861,
	Game_Version.D2_EOF: 0x80809B06,
	Game_Version.MARATHON: 0x8080BADB,
}


# number at (where default_instance_pointer points - 4)
s_runtime_rig_configuration_spec_secondary_classes: dict[Game_Version, int] = {
	Game_Version.D1_DEV_ALPHA: 0x80800A98, # 80800A97 if using definition_pointer
	Game_Version.D1_ROI: 0x808008B2, # 8080099B if using definition_pointer
	Game_Version.D2_EOF: 0x80808B66,
	Game_Version.MARATHON: 0x8080AD85,
}


s_skeleton_spec_secondary_classes: dict[Game_Version, int] = {
	Game_Version.D1_DEV_ALPHA: 0x80800DC9, # 80800DC4 if using definition_pointer
	Game_Version.D1_ROI: 0x808006BD, # 8080049A if using definition_pointer
	Game_Version.D2_EOF: 0x808081DD,
	Game_Version.MARATHON: 0x80809FB6,
}

# TODO: figure others
# it contains a reference to mesh
s_dynamic_model_component_secondary_classes = {
	Game_Version.D1_DEV_ALPHA: 0x808020CA, # 808020C0 if using definition_pointer
	Game_Version.D1_ROI: 0x80801A80, # 80801A9C if using definition_pointer
	Game_Version.D2_EOF: 0x80806D8A  # 80806D8F if using definition_pointer
}

s_entity_model_refs = {
	Game_Version.D1_DEV_ALPHA: 0x80802020,
	Game_Version.D1_ROI: 0x80801AB5,
	Game_Version.D2_EOF: 0x80806F07
}