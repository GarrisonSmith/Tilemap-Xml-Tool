import os
from PIL import Image
from PIL import ImageChops
from xml.dom import minidom

tile_size = 64
directory_path = os.path.dirname(os.path.realpath(__file__))
tile_maps_path = os.path.join(directory_path, 'tile_maps')
spritesheets_path = os.path.join(directory_path, 'spritesheets')
tiles = list() 
#each tile is represented by an array in the form of:
#[tile's image, tile's spritesheet name, the tile's col and row in the spritesheet image, tile's col, tile's row, tile's location]
#the tile's location is a list contains arrays in the form of: [location layer, layer locations (list)]

#gets the locations list for the given layer of the given tile, if it does not currently exist then it creates and returns it.
def get_layer_locations(tile, layer):
	if tile[5] != [None]*2 :
		for location_lists in tile[5]:
			if location_lists[0] == layer:
				return location_lists[1]
	new_list = list()
	tile[5].append([layer, new_list])
	return new_list

#determines if the provided tile_image is already in tiles or not
def tile_image_is_in_tiles(tile_image):
	for unqiue_tile in tiles:
		diff = ImageChops.difference(unqiue_tile[0].convert('RGB'), tile_image.convert('RGB'))
		if (diff.getbbox() is None):
			return unqiue_tile #if tile graphic is found then the tile is returned
	return False #tile image is not in tiles

#adds the provided tile to tiles if tile is a new graphic
def add_tile(tile):
	if tile_image_is_in_tiles(tile[0]) is False:
		tiles.append(tile)
		return True #tile was added
	return False #tile was not added
			
#clears then fills tiles from the spritesheets folder
def get_spritesheet_tiles():
	tiles = list() #clears tiles

	#checks for and adds the DEBUG graphic, DEBUG also contains the empty textures.
	spritesheet_path = os.path.join(spritesheets_path, 'DEBUG.png')
	debug_image = Image.open(spritesheet_path)
	if (debug_image.size[0] % tile_size != 0 or debug_image.size[1] % tile_size != 0):
		raise Exception('DEBUG has invalid dimensions. Width: ' + debug_image.size[0] + 'Height: ' + debug_image.size[1])
	for row in range(0, debug_image.size[1], tile_size):
		for col in range(0, debug_image.size[0], tile_size):
			tile_image = debug_image.crop([col, row, col+tile_size, row+tile_size]).convert('RGB')
			tile = [tile_image, 'DEBUG', str(col//64) + ',' + str(row//64), col//64, row//64, list()]
			add_tile(tile)

	#iterates through all spritesheets
	for spritesheet in os.listdir(spritesheets_path):
		#DEBUG is already added
		if spritesheet == 'DEBUG':
			continue
		spritesheet_path = os.path.join(spritesheets_path, spritesheet)
		spritesheet_image = Image.open(spritesheet_path)
		#spritesheet does not have valid dimensions that are evenly divisible by tile dimensions
		if (spritesheet_image.size[0] % tile_size != 0 and spritesheet_image.size[1] % tile_size != 0):
			print('Error in layer dimensions')
			continue
		#iterates through each tile in a spritesheet
		for row in range(0, spritesheet_image.size[1], tile_size):
			for col in range(0, spritesheet_image.size[0], tile_size):
				tile_image = spritesheet_image.crop((col, row, col+tile_size, row+tile_size)).convert('RGB')
				tile = [tile_image, spritesheet[0:-4], str(col//64) + ',' + str(row//64), col//64, row//64, list()]
				add_tile(tile)	

#generates the tile XMLs for the current layer.	
def get_tile_xmls(map_root, map_xml): 
	for tile in tiles:
		#tile has no locations on this layer
		if (tile[5] == []): 
			continue
		
		#generates the primary 'Tile' tag
		tile_xml = map_root.createElement('Engine.Logic.Mapping.Tiling.Tile')
		tile_xml.setAttribute('id', tile[1] + '|' + tile[2])
		map_xml.appendChild(tile_xml)

		#generates the 'spritesheet' tag
		spritesheet_xml = map_root.createElement('spritesheet')
		spritesheet_xml.appendChild(map_root.createTextNode(tile[1]))
		tile_xml.appendChild(spritesheet_xml)

		#generates the 'sheet-coordinates' tag
		sheet_coordinates_xml = map_root.createElement('sheet-coordinates')
		sheet_coordinates_xml.setAttribute('col', str(tile[3]))
		sheet_coordinates_xml.setAttribute('row', str(tile[4]))
		tile_xml.appendChild(sheet_coordinates_xml)

		#generates the 'locations' tag
		for layer_location in tile[5]:
			layer_locations_xml = map_root.createElement('locations')
			layer_locations_xml.setAttribute('layer', layer_location[0])
			for location in layer_location[1]:
				coordinate_xml = map_root.createElement('coordinates')
				coordinate_xml.setAttribute('x', str(location[0]*tile_size))
				coordinate_xml.setAttribute('y', str(location[1]*tile_size))
				layer_locations_xml.appendChild(coordinate_xml)
			tile_xml.appendChild(layer_locations_xml)

#loads the location data for each tile in each layer in the current map.
def load_tile_locations(layer_image, layer_number, map_layer_path):
	#checks if the current layer dimensions are valid
	if (layer_image.size[0] % tile_size != 0 and  layer_image.size[1] % tile_size != 0):
		print('Error in layer dimensions: ' + map_layer_path)
		print('Layer XML not generated.')
		return
	
	#iterates through each tile in the current layer image
	for row in range(0, layer_image.size[0], tile_size):
		for col in range(0,  layer_image.size[1], tile_size):
			crop_area = (col, row, col+tile_size, row+tile_size)
			tile_image = layer_image.crop(crop_area).convert('RGB')
			tile = tile_image_is_in_tiles(tile_image)

			#tile was not found in a spritesheet and is a missing texture.
			if (tile is False):
				print('tile graphic not found in a spritesheet: ' + map_layer_path)
				print('DEBUG tile placed instead.')
				get_layer_locations(tiles[0], layer_number).append((col//64, row//64))
				continue

			#EMPTY tiles are not included in the XML.
			if (tile[1] == 'DEBUG' and tile[3] != 0):
				continue

			get_layer_locations(tile, layer_number).append((col//64, row//64))

#generates the map XML for the provided arguments
def get_map_xml(map_path, map_root, map_xml): 
	#clears tiles locations for new map
	for tile in tiles:
		tile[5] = list()
	#iterates through layer images of map folder
	for map_layer_name in os.listdir(map_path):
		map_layer_path = os.path.join(map_path, map_layer_name)
		layer_image = Image.open(map_layer_path)
		layer_number = map_layer_name[:-4]
		load_tile_locations(layer_image, layer_number, map_layer_path)

	get_tile_xmls(map_root, map_xml)

#generates the XML for all tile maps
def generate_maps_xml():
	#iterates through each map in the maps directory 
	for map in os.listdir(tile_maps_path):
		map_root = minidom.Document() 
		map_path = os.path.join(tile_maps_path, map)

		map_xml = map_root.createElement('Engine.Logic.Mapping.GameMap')
		map_xml.setAttribute('name', map)

		get_map_xml(map_path, map_root, map_xml)
		map_root.appendChild(map_xml)

		xml_str = map_root.toprettyxml(indent ='\t')
		save_path = os.path.join(directory_path, 'xmls')  
		save_path = os.path.join(save_path, map+".xml")
		with open(save_path, 'w') as xml_file:
			xml_file.write(xml_str)

get_spritesheet_tiles()
generate_maps_xml()