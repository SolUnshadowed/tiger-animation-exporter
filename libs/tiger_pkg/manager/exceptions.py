class Package_Manager_Error(Exception):
	pass

class Base_Directory_Error(Exception):
	pass

class Path_Cache_Invalid_Error(Package_Manager_Error):
	pass

class Package_Error(Package_Manager_Error):
	pass

class Unexpected_Package_Name_Error(Package_Error):
	pass

class Unexpected_Package_Platform(Package_Error):
	pass
