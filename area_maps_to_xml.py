import os
from PIL import Image
from PIL import ImageChops
from xml.dom import minidom

tile_size = 64
directory_path = os.path.dirname(os.path.realpath(__file__))
tile_maps_path = os.path.join(directory_path, 'tile_maps')
spritesheets_path = os.path.join(directory_path, 'spritesheets')
tiles = list()

def tile_image_is_in_tiles(tile_image): #determines if the provided tile_image is already in tiles or not
	for unqiue_tile in tiles:
		diff = ImageChops.difference(unqiue_tile[0].convert('RGB'), tile_image.convert('RGB'))
		if (diff.getbbox() is None):
			return [unqiue_tile[1], unqiue_tile[2]] #if tile graphic is found then the tile ID is returned
	return False #tile image is not in tiles

def add_tile(tile): #adds the provided tile to tiles if tile is a unique graphic
	if tile_image_is_in_tiles(tile[0]) == False:
		tiles.append(tile)
		return True #tile was added
	return False #tile was not added
			
def get_spritesheet_tiles(): #clears then fills tiles
	tiles = list() #clears tiles

	try: #checks for a DEBUG graphic
		spritesheet_path = os.path.join(spritesheets_path, 'DEBUG.png')
		tile_image = Image.open(spritesheet_path)
		if (tile_image.size[0] != tile_size & tile_image.size[1] != tile_size):
			raise Exception('DEBUG has invalid dimensions.')
		tile = [tile_image, 'DEBUG', '{X:0 Y:0}']
		add_tile(tile)
	except:
		print('No DEBUG png found')

	try: #checks for a EMPTY graphic
		spritesheet_path = os.path.join(spritesheets_path, 'EMPTY.png')
		tile_image = Image.open(spritesheet_path)
		if (tile_image.size[0] != tile_size & tile_image.size[1] != tile_size):
			raise Exception('EMPTY has invalid dimensions.')
		tile = [tile_image, 'EMPTY', '{X:0 Y:0}']
		add_tile(tile)
	except:
		print('No EMPTY png found')

	for spritesheet in os.listdir(spritesheets_path): #iterates through all spritesheets
		spritesheet_path = os.path.join(spritesheets_path, spritesheet)
		spritesheet_image = Image.open(spritesheet_path)
		horizontal_length = spritesheet_image.size[0]; vertical_length = spritesheet_image.size[1]
		if (horizontal_length % tile_size & vertical_length % tile_size):
			print("Error in layer dimensions")
			continue
		for row in range(0, horizontal_length, tile_size): #iterates through each tile in a spritesheet
			for col in range(0, vertical_length, tile_size):
				crop_area = (row, col, row+tile_size, col+tile_size)
				tile_image = spritesheet_image.crop(crop_area)
				tile = [tile_image, spritesheet[0:-4], '{X:'+str(row)+' Y:'+str(col)+'}']
				add_tile(tile)	

def get_tile_xml(tile_image, tile_coordinates, map_root, layer_xml): #generates the tile XML for the provided arguments
	tile_ID = tile_image_is_in_tiles(tile_image)
	
	if (tile_ID == False):
		print('tile graphic not found in a spritesheet')
		tile_ID = ['DEBUG', '{X:0 Y:0']

	if (tile_ID[0] == 'EMPTY'):
		return

	tile_xml = map_root.createElement('Tile')
	tile_xml.setAttribute('ID', tile_ID[0]+tile_ID[1])
	layer_xml.appendChild(tile_xml)

	tile_set = map_root.createElement('tileSet')
	tile_set.setAttribute('name', tile_ID[0])
	tile_xml.appendChild(tile_set)
	
	tile_set_coordinates = map_root.createElement('tileSetCoordinates')
	tile_set_coordinates.setAttribute('coordinates', tile_ID[1])
	tile_xml.appendChild(tile_set_coordinates)

	tile_map_coordinates = map_root.createElement('tileMapCoordinates')
	tile_map_coordinates.setAttribute('coordinates', str(tile_coordinates))
	tile_xml.appendChild(tile_map_coordinates)

def get_layer_xml(layer_image, map_root, layer_xml): #generates the layer XML for the provided arguments
	horizontal_length = layer_image.size[0]; vertical_length = layer_image.size[1]
	
	if (horizontal_length % tile_size != 0 & vertical_length % tile_size != 0):
		print("Error in layer dimensions")
		return
	
	for row in range(0, horizontal_length, tile_size):
		for col in range(0, vertical_length, tile_size):
			tile_coordinates = '{X:'+str(row)+' Y:'+str(col)+'}'
			crop_area = (row, col, row+tile_size, col+tile_size)
			tile_image = layer_image.crop(crop_area)
			get_tile_xml(tile_image, tile_coordinates, map_root, layer_xml)

def get_map_xml(map_path, map_root, map_xml): #generates the map XML for the provided arguments
	for map_layer_name in os.listdir(map_path):
		map_layer_path = os.path.join(map_path, map_layer_name)
		layer_image = Image.open(map_layer_path)
		
		layer_xml = map_root.createElement('layer')
		layer_xml.setAttribute('name', map_layer_name[:-4])
		map_xml.appendChild(layer_xml)

		get_layer_xml(layer_image, map_root, layer_xml)

def generate_maps_xml(): #generates the XML for all tile maps
	for map in os.listdir(tile_maps_path):
		map_path = os.path.join(tile_maps_path, map)
		
		map_root = minidom.Document()
		map_xml = map_root.createElement(map)
		map_root.appendChild(map_xml)

		get_map_xml(map_path, map_root, map_xml)

		xml_str = map_root.toprettyxml(indent ="\t")  
		save_path = os.path.join(directory_path, map+".xml")
		with open(save_path, "w") as xml_file:
			xml_file.write(xml_str)

get_spritesheet_tiles()
generate_maps_xml()