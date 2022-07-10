clear global;
clear;

global uniqueTiles %contains the 64x64 pixel data of all unique tiles. Index corresponds to tileIdentities.
global tileIdentities %contains the assigned/generated name for all unique tiles. Index corresponds to uniqueTiles.
uniqueTiles(1:128,1:64,1:3) = imread("squares.png");
tileIdentities = ["","";"",""];

cur = "Tilemap Xml Creation\area_maps\";
foo = dir(cur);
for bar = foo'
    if bar.isdir && bar.name ~= "." && bar.name ~= ".."
        mapFolder = dir(string(bar.folder)+"\"+string(bar.name)+"\*.png");
        
        mapString = "";
        mapString = get_map_string(mapFolder);
        
        try
            mkdir("Tilemap Xml Creation\xmls", string(bar.name));
        catch
            %folder already exists
        end

        textFileName = "Tilemap Xml Creation\xmls\"+string(bar.name)+"\"+string(bar.name)+".txt";
        fileID = fopen(textFileName,'w');
        fprintf(fileID, mapString);
    end
end
%creates the map string from the provided map folder.
function foo = get_map_string(mapFolder)
    global uniqueTiles
    global tileIdentities
    tile_sets = dir("Tilemap Xml Creation\tile_sets\*.png");
    area_maps = mapFolder;
    for tileSetFile = tile_sets'
        tileSet = imread(string(tileSetFile.folder)+"\"+string(tileSetFile.name));
        [rows, columns, ~] = size(tileSet);
        if mod(rows, 64) ~= 0
            disp("rows wasnt a factor of 64.")
            break;
        end
        if mod(columns, 64) ~= 0
            disp("columns wasnt a factor of 64.")
            break;
        end
        get_tiles_from_set(tileSet,char(tileSetFile.name));
    end
    index = 1;
    for tileMapFile = area_maps'
        mapString(index) = "";
        mapString(index) = mapString(index) + "<" +tileMapFile.name(end-4:end-4) + ">";
        tileMap = imread(string(tileMapFile.folder)+"\"+string(tileMapFile.name));
        mapLayer = construct_map_string(tileMap);
        mapString(index) = mapString(index) + remove_empty_columns(mapLayer);
        index = index + 1;
    end
    mapString = remove_empty_rows(mapString);
    %mapString = remove_empty_columns(mapString);
    foo= "";
    for index = 1:length(mapString) 
        foo = foo + mapString(index);
    end
end
%adds all the unique tiles to uniqueTiles
function get_tiles_from_set(tileSet, name)
    [rows, columns, ~] = size(tileSet);
    for i=1:64:rows
        for j=1:64:columns
            add_unique_tile(tileSet(i:i+63,j:j+63,1:3), name(1:end-4), "{X:"+string(j-1)+" Y:"+string(i-1)+"}");
        end
    end
end
%add tiles only if a duplicate hasnt already been added.
function add_unique_tile(new, name, coordinates) 
    global uniqueTiles
    [rows, ~, ~] = size(uniqueTiles);
    unique = true;
    for k=1:64:rows
        if(new == uniqueTiles(k:k+63,1:64,1:3))
            unique = false;
            break;
        end
    end
    if(unique)
        uniqueTiles(rows+1:rows+64,1:64,1:3) = new;
        add_tile_identity(name, coordinates);
    end
end
%adds corresponding tile identity to the unique tile.
function add_tile_identity(name, coordinates) 
    global tileIdentities
    [rows, ~] = size(tileIdentities);
    tileIdentities(rows+1,1:2) = [name, coordinates];
end
%generates the map string by interating through the 64x64 tiles in the provided image and finding their unique tile and tile identity.
function foo = construct_map_string(tileMap) 
    foo = "";
    [rows, columns, ~] = size(tileMap);
    for i=1:64:rows
        for j=1:64:columns
            foo = foo+get_tile_string(tileMap(i:i+63,j:j+63,1:3))+"|"; %splits columns
        end
        foo = foo + ";"; %splits rows
    end
            
end
%gets the provided tile's string from tileIdentities.
function foo = get_tile_string(tile) 
    global uniqueTiles    
    global tileIdentities
    [rows, ~, ~] = size(uniqueTiles);
    index = 1;
    for i=1:64:rows
        if tile == uniqueTiles(i:i+63,1:64,1:3)
            foo = tileIdentities(index,1)+tileIdentities(index,2);
            break;
        end
        index=index+1;
    end
end
%removes the max amount of empty rows from the mapString layers.
function foo = remove_empty_rows(mapString) 
    
    lengthDif = intmax;
    for index=1:1:length(mapString)
        layerString = mapString(index);
        
        for i=1:1:strlength(layerString)
            empty = true;
            if(layerString{1}(i) == ';')
                for j = i:1:strlength(layerString)
                    if(layerString{1}(j) ~= '|' && layerString{1}(j) ~= ';')
                        empty = false;
                        break;
                    end
                end
            
                if (empty)
                    if (lengthDif > (strlength(layerString)-i))
                        lengthDif = (strlength(layerString)-i);
                    end
                    break;
                end
            end
        end
    end
    
    for index=1:1:length(mapString)
        layerString = mapString(index);
        layerString = layerString{1}(1:(strlength(layerString)-lengthDif));
        mapString(index) = layerString;
    end
    foo = mapString;
end
%removes the max amount of empty columns from the mapString layers.
function foo = remove_empty_columns(mapString)
    foo = strrep(mapString,"||;","|;");
    while foo ~= strrep(foo,"||;","|;")
        foo = strrep(foo,"||;","|;");
    end
end