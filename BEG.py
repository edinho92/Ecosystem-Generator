bl_info = {
	'name': 'Blender Ecosystem Generator',
	'author': 'Edoardo Gaetani',
	'version': (1, 0, 1),
	'blender': (2, 7, 0),
	"location": "View3D > Tools > BEG",
	'warning': '',
	'description': 'Several improvements for Ecosystem Generator',
	'wiki_url': '',
	'tracker_url': '',
	'category': 'Ecosystem'}

import bpy
from bpy.props import *

		############ FUNZIONI DI SUPPORTO ############
		
def GetIndexFromName(name):
    i = -1
    for n in bpy.context.scene.hk_group_object_list:
        i = i + 1
        if name == n.name:
            return i
			
def GetIndexFromNamePS(name):
    i = -1
    for n in bpy.context.object.particle_systems:
        i = i + 1
        if name == n.name:
            return i
		
#METODO AUSILIARIO PER CARICARE LA MAPPA DI DISTRIBUZIONE
def load(key, scn):
	try:
		val = scn[key]
		img = bpy.data.images.load(val)
	except:
		bpy.ops.error.message('INVOKE_DEFAULT', message = 'Image not found, please select right path!')
		return {'FINISHED'}
	bpy.context.scene.render.engine = 'CYCLES'	
	
	#CERCO IL PARTICLE SYSTEM A CUI ASSOCIARE LA TEXTURE
	object = bpy.context.object
	if object == None:
		return {'FINISHED'}
	else:
		for my_item in object.propertyPath:
			if(val in my_item.value):
				return{'FINISHED'}
		list = object.particle_systems
		index = object.particle_systems.active_index
		if(len(list) == 0):
			bpy.ops.error.message('INVOKE_DEFAULT', message = 'Particle System not found!')
			return {'FINISHED'}
		
		part_system = object.particle_systems[index]
		
		cTex = bpy.data.textures.new('ImageTexture', type = 'IMAGE')
		cTex.image = img
		
		part_settings = bpy.data.particles[part_system.settings.name]
		for count in range(0,18):
			part_settings.active_texture_index = count
			if(part_settings.active_texture == None):
				part_settings.active_texture = cTex
				part_settings.texture_slots[count].texture_coords = 'UV'
				part_settings.texture_slots[count].use_map_density = True
				part_settings.texture_slots[count].use_map_size = True
				tex_property = object.propertyPath.add()
				tex_property.value = val
				return {'FINISHED'}
	
		
class PathProperty(bpy.types.PropertyGroup):
	value = bpy.props.StringProperty(name="", default="unknown")
	

def initSceneProperties():
	bpy.types.Object.propertyPath = bpy.props.CollectionProperty(type=PathProperty)
	bpy.types.Scene.path = bpy.props.StringProperty(name="", description="simple file path", maxlen= 1024, subtype='FILE_PATH', default= "")
	bpy.types.Scene.scene_property = bpy.props.StringProperty()
	bpy.types.Object.my_property = bpy.props.StringProperty()
	bpy.types.Object.target = bpy.props.StringProperty()
	bpy.types.Scene.hk_group_list = bpy.props.CollectionProperty(type=GroupList)
	bpy.types.Scene.hk_group_list_index = bpy.props.IntProperty()
	bpy.types.Scene.hk_group_object_list = bpy.props.CollectionProperty(type=GroupObjectList)
	bpy.types.Scene.hk_group_object_list_index = bpy.props.IntProperty()
	return	


#BOTTONE NELLA FINESTRA DI ERRORE
class OkOperator(bpy.types.Operator):
    bl_idname = "error.ok"
    bl_label = "OK"
    def execute(self, context):
        return {'FINISHED'}

#OPERATORE PER GESTIRE GLI ERRORI		
class MessageOperator(bpy.types.Operator):
    bl_idname = "error.message"
    bl_label = "Message"
    message = StringProperty()
 
    def execute(self, context):
        self.report({'INFO'}, self.message)
        return {'FINISHED'}
 
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_popup(self, width=500, height=200)
 
    def draw(self, context):
        self.layout.label("Si è verificato un errore:")
        row = self.layout.split(0.80)
        row.prop(self, "message")
        row = self.layout.split(0.80)

		
def clearListGroup():
	list_group = bpy.context.scene.hk_group_list
	if(len(list_group) == 0):
		return
	else:
		for grp in list_group.items():
			list_group.remove(0)

def clearListObjectGroup():
	list_object = bpy.context.scene.hk_group_object_list
	if(len(list_object) == 0):
		return
	else:
		for obj in list_object.items():
			list_object.remove(0)
		
def refreshListGroup():
	scena = bpy.context.scene
	if("hk_group_list" in dir(scena)):
		list = scena.hk_group_list
		index = scena.hk_group_list_index
		
		#RIPULISCE ELENCO
		clearListGroup()
	
		#AGGIUNGE TUTTI I GRUPPI, SE CE NE SONO
		if(len(bpy.data.groups) == 0):
			return
			
		for grp in bpy.data.groups:
			if(grp != None):
				if(grp.name[:3] == 'BG_'):
					grp_member = list.add()
					grp_member.name = grp.name[3:]
					grp_member.value = grp.name[3:]
		count = len(list)
		if(count > 0 and count == index):
			scena.hk_group_list_index = index-1

def refreshObjectListGroup():
	scena = bpy.context.scene
	if("hk_group_object_list" in dir(scena)):
		list_group = scena.hk_group_list
		index_group = scena.hk_group_list_index
		list_object = scena.hk_group_object_list
		index_object = scena.hk_group_object_list_index
		
		#RIPULISCE ELENCO
		clearListObjectGroup()
		
		if(len(list_group) == 0):
			return
		
		gruppo = bpy.data.groups["BG_"+list_group[index_group].name]
		
		#AGGIUNGE TUTTI GLI OGGETTI, SE CE NE SONO
		if(gruppo.objects == 0):
			return
			
		for obj in gruppo.objects:
			if(obj != None):
				obj_member = list_object.add()
				obj_member.name = obj.name
				obj_member.value = obj.name
				
		count = len(list_group)
		if(count > 0 and count == index_group):
			scena.hk_group_object_list_index = index_object-1
			
class ParticleSystemList(bpy.types.PropertyGroup):
    pass

class GroupList(bpy.types.PropertyGroup):
    pass

class GroupObjectList(bpy.types.PropertyGroup):
    pass

class GroupEditor_ItemList(bpy.types.UIList):
	def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):   
		layout.label(item.name)

class GroupEditor_ObjectList(bpy.types.UIList):
	def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):   
		layout.label(item.name)
		
class ParticleSystem_ObjectList(bpy.types.UIList):
	def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):   
		layout.label(item.name)
		temp = layout.operator("set_count_object.operator", text="", icon="SCRIPTWIN", emboss=False)
		temp.target = item.name
		
class GroupEditor_ObjectList_Editable(bpy.types.UIList):
	def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):   
		layout.label(item.name)
		temp = layout.operator("set_count.operator", text="", icon="SCRIPTWIN", emboss=False)
		temp.target = item.name
		
		############### PANNELLI ###############

#PANNELLO DI EDITOR DEGLI ECOSISTEMI E DEGLI OGGETTI
class EcosystemLibrary(bpy.types.Panel):
	bl_category = "BEG"
	bl_label = "Ecosystem Library"
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS"
	bl_options = {'DEFAULT_CLOSED'}	
	
	def draw(self, context):
		layout = self.layout
		
		#LISTA DEI GRUPPI 
		row = layout.row()
		row.template_list("GroupEditor_ItemList", "", bpy.context.scene, "hk_group_list", bpy.context.scene, "hk_group_list_index", rows=1)
		
		#OPERATORI
		row = layout.row()
		row.operator("new_group.operator", text="Create", icon="NEW")
		row.operator("remove_group.operator", text="Delete", icon="CANCEL")
		row.operator("rename_group.operator", text="Rename", icon="TEXT")
		row.operator("set_scene.operator", text="Enable EG", icon="UV_SYNC_SELECT")
		
		row = layout.row()
		row.operator("refresh_groups.operator", text="Refresh", icon="FILE_REFRESH")
		
		row = layout.row()
		row.label(text="Object to Ecosystem", icon='OBJECT_DATA')
		
		row = layout.row()
		row.template_list("GroupEditor_ObjectList", "", bpy.context.scene, "hk_group_object_list", bpy.context.scene, "hk_group_object_list_index", rows=1)

		row = layout.row()
		row.operator("add_object.operator", text="Add", icon="NEW")
		row.operator("remove_object_group.operator", text="Remove", icon="CANCEL")
		row.operator("rename_object.operator", text="Rename", icon="TEXT")
		
		row = layout.row()
		row.operator("refresh_objects_group.operator", text="Refresh", icon="FILE_REFRESH")
		
		
#PANNELLO DEGLI ECOSISTEMI CORRENTI		
class LandscapeEditor(bpy.types.Panel):
	bl_category = "BEG"
	bl_label = "Landscape Editor"
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS"
	bl_options = {'DEFAULT_CLOSED'}
	
	
	def draw(self, context):
		layout = self.layout
		ob = context.object
		scena = bpy.context.scene
		
		#LISTA DI PARTICLE SYSTEM
		row = layout.row()
		if(ob != None):
			row.template_list("ParticleSystem_ObjectList", "particle_systems", ob, "particle_systems", ob.particle_systems, "active_index", rows=1)
		
		#OPERATORI
		row = layout.row()
		row.operator("new_ps.operator", text="Set Current Object", icon="NEW")
		
		row = layout.row()
		row.operator("remove_ps.operator", text="Remove", icon="CANCEL")
		row.operator("rename_ps.operator", text="Rename", icon="TEXT")
		
		row = layout.row()
		row.operator("add_group_ps.operator", text="Add Ecosystem", icon="ZOOMIN")		
		
		row = layout.row()
		row.prop(context.scene, 'path', toggle = True, text="Texture")
		row.operator("load_map.operator", text="", icon="FILE_TICK")
		
		if bpy.context.object != None:
			if len(bpy.context.object.particle_systems) > 0 :
				row = layout.row()
				row.label(text="Object to Ecosystem Editor", icon='OBJECT_DATA')
				row = layout.row()
				row.template_list("GroupEditor_ObjectList_Editable", "", bpy.context.scene, "hk_group_object_list", bpy.context.scene, "hk_group_object_list_index", rows=1)
		
		
#CREA UN NUOVO PARTICLE SYSTEM		
class New_PS(bpy.types.Operator):
	bl_idname = "new_ps.operator"
	bl_description = "Create New Particle System"
	bl_label = "Create New Particle System"
	
	def execute(self, context):
		object = bpy.context.object
		
		if(object == None):
			return {'FINISHED'}
			
		#AGGIUNGO PARTICLE SYSTEM DI TIPO HAIR 
		bpy.ops.object.particle_system_add()
		list = object.particle_systems
		if(len(list) == 0):
			return {'FINISHED'}
		else:
			psys = object.particle_systems[-1]
			psys.name = "Empty Ecosystem"
			pset = psys.settings.name
			bpy.data.particles[pset].type = 'HAIR'
			bpy.data.particles[pset].render_type = 'GROUP'
			bpy.data.particles[pset].use_group_count = True
			bpy.data.particles[pset].use_advanced_hair = True
			bpy.data.particles[pset].use_rotations = True
			bpy.data.particles[pset].rotation_mode = 'GLOB_Z'

		return {'FINISHED'}

#CREA UN NUOVO GRUPPO
class New_Group(bpy.types.Operator):
	bl_idname = "new_group.operator"
	bl_description = "Create New Group"
	bl_label = "Create New Group"
	
	def execute(self, context):		
		#AGGIUNGO GRUPPO CON IL NOME "ECOSYSTEM" DI DEFAULT
		bpy.data.groups.new(name="BG_Ecosystem") 
		refreshListGroup()
		return {'FINISHED'}

#AGGIUNGE UN OGGETTO AD UN GRUPPO
class Add_Object(bpy.types.Operator):
	bl_idname = "add_object.operator"
	bl_description = "Add Selected Object to Selected Group"
	bl_label = "Add Object to Selected Group"
	
	def execute(self, context):
		scena_db = bpy.data.scenes
		oggetto = bpy.context.object
		if oggetto == None:
			return {'FINISHED'}
		try:
			object_name = oggetto.name
			scena = bpy.context.scene
			list = scena.hk_group_list
		except:
			print("Select an object!")
		oggetto = bpy.ops.object
		if(len(list) == 0):
			bpy.ops.error.message('INVOKE_DEFAULT', message = 'Group\'s List is empty!')
			return {'FINISHED'}
		else:
			for i in scena_db.keys():
				try:
					if(bpy.data.scenes[i].scene_property == "ECOSYS"):
						index = scena.hk_group_list_index
						temp_object = bpy.context.object
						temp_object.draw_type = 'BOUNDS'
						oggetto.group_link(group = "BG_"+list[index].name)
						oggetto.make_links_scene(scene=bpy.data.scenes[i].name)
						oggetto.delete(use_global=False)
						
						refreshObjectListGroup()
						return {'FINISHED'}
				except:
					print("scena non trovata")
			bpy.ops.error.message('INVOKE_DEFAULT', message = 'Remember to enable ECOSYS scene!')
			return {'FINISHED'}

#AGGIUNGE UN GRUPPO AD UN PARTICLE SYSTEM			
class Add_Group_To_PS(bpy.types.Operator):
	bl_idname = "add_group_ps.operator"
	bl_description = "Add Selected Group to Selected Particle System"
	bl_label = "Add Selected Group to Selected Particle System"
	
	def execute(self, context):
		if(bpy.context.object == None):
			return {'FINISHED'}
			
		scena = bpy.context.scene
		oggetto = bpy.context.object
		list_group = scena.hk_group_list
		list_ps = oggetto.particle_systems
		
		if(len(list_ps) == 0 ):
			bpy.ops.error.message('INVOKE_DEFAULT', message = 'List of Particle System is empty')
			return {'FINISHED'}
		elif(len(list_group) == 0):
			bpy.ops.error.message('INVOKE_DEFAULT', message = 'List of Group is empty')
			return {'FINISHED'}
		else:
			index_group = scena.hk_group_list_index
			index_ps = list_ps.active_index
			try:
				ps = list_ps[index_ps]
			except:
				print("Index out of range")
				return {'FINISHED'}
			ps_settings = ps.settings
			nome_gruppo = list_group[index_group].name
			bpy.data.particles[ps_settings.name].dupli_group = bpy.data.groups["BG_"+nome_gruppo]
			oggetto.my_property = "BG_"+nome_gruppo
			ps.name = nome_gruppo
			return {'FINISHED'}

#RIMUOVE UN PARTICLE SYSTEM
class Remove_PS(bpy.types.Operator):
	bl_idname = "remove_ps.operator"
	bl_description = "Remove Particle System"
	bl_label = "Remove Particle System"
	
	def execute(self, context):
		if(bpy.context.object != None):
			# RIMUOVE IL PARTICLE SYSTEM SELEZIONATO
			bpy.ops.object.particle_system_remove()
		return {'FINISHED'}

#RIMUOVE UN GRUPPO		
class Remove_Group(bpy.types.Operator):
	bl_idname = "remove_group.operator"
	bl_description = "Remove Group"
	bl_label = "Remove Group"
	
	def execute(self, context):
		scena = bpy.context.scene
		list_group = scena.hk_group_list
		index_group = scena.hk_group_list_index
		list_object = scena.hk_group_object_list
		index_object = scena.hk_group_object_list_index
		
		#SE NON CI SONO ELEMENTI DA ELIMINARE TERMINA
		if(len(list_group) == 0):
			return {'FINISHED'}
		else:
			#SELEZIONO IL GRUPPO DA ELIMINARE
			try:
				gruppo = bpy.data.groups["BG_"+list_group[index_group].name]
			except:
				print("Index Error!")
				return {'FINISHED'}
			if(len(list_object) != 0):
				for obj in list_object.items():
					bpy.ops.remove_object_group.operator(passed_object = str(obj[0]))
			#ELIMINO IL GRUPPO
			bpy.data.groups.remove(gruppo)
			refreshListGroup()
			refreshObjectListGroup()
		return {'FINISHED'}

#RIMUOVE UN OGGETTO DA UN GRUPPO
class Remove_Object(bpy.types.Operator):
	bl_idname = "remove_object_group.operator"
	bl_description = "Remove Selected Object from Selected Group"
	bl_label = "Remove Object from Selected Group"
	
	passed_object = bpy.props.StringProperty()
	
	def execute(self, context):
		
		scena_db = bpy.data.scenes
		scena = bpy.context.scene
		scenaname = bpy.context.scene.name
		list_object = scena.hk_group_object_list
		list_group = scena.hk_group_list
		
		if(len(list_object) == 0 or len(list_group) == 0):	
			return {'FINISHED'}
		else:
			index_object = scena.hk_group_object_list_index
			index_group = scena.hk_group_list_index
			
			bpy.ops.object.select_all(action='DESELECT')
			
			try:
				if self.passed_object == "":
					oggetto = bpy.data.objects[list_object[index_object].name]
				else:
					oggetto = bpy.data.objects[self.passed_object]
			except:
				print("Index Error!")
				return {'FINISHED'}
			
			groupname = list_group[index_group].name
			
			if(oggetto.name not in bpy.context.scene.objects):
				for i in scena_db.keys():
					try:
						if(bpy.data.scenes[i].scene_property == "ECOSYS"):
							bpy.data.screens['Default'].scene = bpy.data.scenes[i]
							context_scene = bpy.context.scene
							for i in range(0, 20):
								context_scene.layers[i] = True
							bpy.ops.object.select_all(action='DESELECT')
							oggetto.select = True
							bpy.context.scene.objects.active = oggetto
							bpy.ops.object.make_links_scene(scene=scenaname)
							bpy.ops.object.delete(use_global=False)
							for i in range(1, 20):
								context_scene.layers[i] = False
							bpy.data.screens['Default'].scene = bpy.data.scenes[scenaname]
							context_scene = bpy.context.scene
							for i in range(0, 20):
								context_scene.layers[i] = True
							bpy.ops.object.select_all(action='DESELECT')
							oggetto.select = True
							bpy.context.scene.objects.active = oggetto
							bpy.ops.group.objects_remove(group = "BG_"+groupname)
							for i in range(1, 20):
								context_scene.layers[i] = False
							refreshObjectListGroup()
							return {'FINISHED'}
					except:
						print("no")
				bpy.ops.error.message('INVOKE_DEFAULT', message = 'Object not found! Try to recover deleted scenes!')
			else:
				bpy.ops.object.select_all(action='DESELECT')
				oggetto.select = True
				bpy.context.scene.objects.active = oggetto
				bpy.ops.group.objects_remove(group = "BG_"+groupname)
		
		refreshObjectListGroup()
		return {'FINISHED'}
			

#RINOMINA IL PARTICLE SYSTEM		
class Rename_PS(bpy.types.Operator):
	bl_idname = "rename_ps.operator"
	bl_description = "Rename Particle System"
	bl_label = "Rename Particle System"
	
	my_string = StringProperty(name = "Put Name here:")
	
	def execute(self, context):
		if(bpy.context.object == None):
			return {'FINISHED'}
			
		list = bpy.context.object.particle_systems
		
		#SE NON CI SONO ELEMENTI DA RINOMINARE TERMINA
		if(len(list) == 0):
			return {'FINISHED'}
		else:
			message = "%s" % (self.my_string)
			index = list.active_index
			#RINOMINO IL PARTICLE SYSTEM SELEZIONATO
			bpy.context.object.particle_systems[index].name = message
		return {'FINISHED'}
		
	def invoke(self, context, event):
		if(bpy.context.object == None):
			return {'FINISHED'}
		list = bpy.context.object.particle_systems
		
		#SE NON CI SONO ELEMENTI DA RINOMINARE TERMINA
		if(len(list) == 0):
			return {'FINISHED'}
		self.my_string = "Particle System"
		return context.window_manager.invoke_props_dialog(self)

#RINOMINA UN GRUPPO		
class Rename_Group(bpy.types.Operator):
	bl_idname = "rename_group.operator"
	bl_description = "Rename Group"
	bl_label = "Rename Group"
	
	my_string = StringProperty(name = "Put Name here:")
	
	def execute(self, context):
		scena = bpy.context.scene
		list = scena.hk_group_list
		
		#SE NON CI SONO ELEMENTI DA RINOMINARE TERMINA
		if(len(list) == 0):
			return {'FINISHED'}
		else:
			message = "%s" % (self.my_string)
			index = scena.hk_group_list_index
			#SCELGO NEL "DB" DEI GRUPPI QUELLO DA RINOMINARE
			bpy.data.groups["BG_"+list[index].name].name = "BG_"+message
			#RINOMINO IL GRUPPO SELEZIONATO
			list[index].name = "BG_"+message
			refreshListGroup()
		return {'FINISHED'}
		
	def invoke(self, context, event):
		scena = bpy.context.scene
		list = scena.hk_group_list
		if(len(list) == 0):
			return {'FINISHED'}
			
		self.my_string = "Group"
		return context.window_manager.invoke_props_dialog(self)

#RINOMINA UN OGGETTO
class Rename_Object(bpy.types.Operator):
	bl_idname = "rename_object.operator"
	bl_description = "Rename Object"
	bl_label = "Rename Object"
	
	my_string = StringProperty(name = "Put Name here:")
	
	def execute(self, context):
		scena = bpy.context.scene
		list = scena.hk_group_object_list
		
		#SE NON CI SONO ELEMENTI DA RINOMINARE TERMINA
		if(len(list) == 0):
			return {'FINISHED'}
		else:
			message = "%s" % (self.my_string)
			index = scena.hk_group_object_list_index
			#SCELGO NEL "DB" DEGLI OGGETTI QUELLO DA RINOMINARE
			bpy.data.objects[list[index].name].name = message

			#RINOMINO L'OGGETTO SELEZIONATO
			list[index].name = message
		return {'FINISHED'}
		
	def invoke(self, context, event):
		scena = bpy.context.scene
		list = scena.hk_group_object_list
		if(len(list) == 0):
			return {'FINISHED'}
			
		self.my_string = "Object"
		return context.window_manager.invoke_props_dialog(self)
		
#AGGIORNA LISTA DEI GRUPPI
class Refresh_Group(bpy.types.Operator):
	bl_idname = "refresh_groups.operator"
	bl_description = "Refresh Groups"
	bl_label = "Refresh Groups"
	
	def execute(self, context):
		refreshListGroup()
		return {'FINISHED'}

#AGGIORNA LISTA DEGLI OGGETTI DI UN GRUPPO		
class Refresh_Objects_Group(bpy.types.Operator):
	bl_idname = "refresh_objects_group.operator"
	bl_description = "Refresh List of Objects"
	bl_label = "Refresh Objects"
	
	def execute(self, context):
		refreshObjectListGroup()
		return {'FINISHED'}

#CREA UNA NUOVA SCENA 
class New_Scene(bpy.types.Operator):
	bl_idname = "set_scene.operator"
	bl_description = "Create ECOSYS Scene"
	bl_label = "Create ECOSYS Scene"
	
	def execute(self, context):
		lista_scene = bpy.data.scenes
		scenaname = bpy.context.scene.name
		for i in lista_scene.keys():
			try:
				if(bpy.data.scenes[i].scene_property == "ECOSYS"):
					bpy.data.screens['Default'].scene = bpy.data.scenes[i]
					return {'FINISHED'}
			except KeyError:
				print("Key Error")
		else:
			bpy.ops.scene.new(type='NEW')
			bpy.context.scene.name = "ECOSYS"
			bpy.data.scenes['ECOSYS'].scene_property = "ECOSYS"
			bpy.data.screens['Default'].scene = bpy.data.scenes[scenaname]
		return {'FINISHED'}
		
#CARICA MAPPA DI DISTRIBUZIONE 
class Load_Map(bpy.types.Operator):
	bl_idname = "load_map.operator"
	bl_description = "Select Distribution Map"
	bl_label = "Select Distribution Map"
	
	def execute(self, context):
		scn = context.scene
		load('path', scn)
		return {'FINISHED'}

	
#CAMBIA LE PROPRIETA' DI UN OGGETTO IN UN GRUPPO
class Set_Count(bpy.types.Operator):
	bl_idname = "set_count.operator"
	bl_description = "Set Count Object"
	bl_label = "Set Count"
	
	target = bpy.props.StringProperty(options={'HIDDEN'})
	value = IntProperty(name = "Count(%):", min = 0)
	
	def execute(self, context):
		scena = bpy.context.scene
	
		oggetto = bpy.context.object
			
		list_object = scena.hk_group_object_list
		if( len(list_object) == 0 or list_object == None):
			return {'FINISHED'}
		
		if self.target == None:
			bpy.ops.error.message('INVOKE_DEFAULT', message = 'Unknown Error')
			return {'FINISHED'}
			
		index_object = GetIndexFromName(self.target)
		scena.hk_group_object_list_index = index_object
		
		if(oggetto == None):
			return {'FINISHED'}
					
		list_ps = oggetto.particle_systems
		if( len(list_ps) == 0):
			return {'FINISHED'}
					
		index_ps = oggetto.particle_systems.active_index
		part_system = list_ps[index_ps]
		if(part_system == None):
			return {'FINISHED'}
			
		part_settings = part_system.settings
			
		part_settings.use_group_count = True
		i = 0
		part_settings.active_dupliweight_index = i
		object_list_group_count = part_settings.active_dupliweight
		if( object_list_group_count == None):
			return {'FINISHED'}
			
		nome = list_object[index_object].name
			
		while object_list_group_count != None:
			if ( nome + ": ") in object_list_group_count.name:
				object_list_group_count.count = self.value
				return {'FINISHED'}
			i = i+1
			part_settings.active_dupliweight_index = i
			object_list_group_count = part_settings.active_dupliweight		
		return {'FINISHED'}
		
	def invoke(self, context, event):
		self.value = 1
		self.target = self.target
		return context.window_manager.invoke_props_dialog(self)
		
		
class SetNumberParticles(bpy.types.Operator):
	bl_idname = "set_count_object.operator"
	bl_description = "Set Object's number"
	bl_label = "Set Object's number"

	value = IntProperty(name = "Count: ")
	target = bpy.props.StringProperty(options={'HIDDEN'})
	
	def execute(self, context):
		oggetto = bpy.context.object
		list_ps = oggetto.particle_systems
		index_ps = GetIndexFromNamePS(self.target)
		part_system = list_ps[index_ps]
		part_settings = bpy.data.particles[part_system.settings.name]
		part_settings.count = self.value
		return {'FINISHED'}
		
	def invoke(self, context, event):
		self.value = 1000
		self.target = self.target
		return context.window_manager.invoke_props_dialog(self)
		
	######### FUNZIONI PER REGISTRARE I MODULI ##############
	
classes = [	ParticleSystemList,
			GroupList,
			GroupObjectList,
			OkOperator, 
			MessageOperator,
			GroupEditor_ItemList,
			GroupEditor_ObjectList,
			EcosystemLibrary,
			LandscapeEditor,
			New_PS,
			New_Group,
			Add_Object,
			Add_Group_To_PS,
			Remove_PS,
			Remove_Group,
			Remove_Object,
			Rename_PS,
			Rename_Group,
			Rename_Object,
			Refresh_Group,
			Refresh_Objects_Group,
			New_Scene,
			Load_Map,
			Set_Count,
			PathProperty]
			
def register():
	for c in classes:
		bpy.utils.register_class(c)
	initSceneProperties()
	bpy.utils.register_module(__name__)
    

def unregister():
	for c in classes:
		bpy.utils.unregister_class(c)
		
	bpy.utils.unregister_module(__name__)
    

if __name__ == "__main__":
    register()