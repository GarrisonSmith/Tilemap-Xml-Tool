clear global;
clear;

cur = "Tilemap Xml Creation\xmls\";
foo = dir(cur);
for bar = foo'
    if bar.isdir && bar.name ~= "." && bar.name ~= ".."
        mapFolder = dir(string(bar.folder)+"\"+string(bar.name));
        
        mapXml = get_map_xml(mapFolder);
        
        xmlFileName = "Tilemap Xml Creation\xmls\"+string(bar.name)+"\"+string(bar.name)+".xml";
        writestruct(mapXml, xmlFileName);
    end
end
%gets the xml master node for the provided map folders txt file.
function foo = get_map_xml(mapFolder)
    animatedConfig = readstruct("Tilemap Xml Creation\tile_sets\tile_animations.xml");
    hitboxConfig = readstruct("Tilemap Xml Creation\tile_sets\tile_hitboxes.xml");
    fileArr = split(string(mapFolder(1).folder),'\');
    mapString = fileread(string(mapFolder(1).folder)+"\"+fileArr(5)+".txt");
    try
        eventStruct = readstruct(string(mapFolder(1).folder)+"\eventboxes.xml");
    catch
        eventStruct = 0; %there is no eventboxes file.
    end

    layerArr = split(mapString, '<');

    mapXml.nameAttribute = fileArr(5);
    mapXml.layer(1) = get_layer_xml(layerArr(2), animatedConfig, hitboxConfig);
    for i=3:length(layerArr)
        mapXml.layer(i-1) = get_layer_xml(layerArr(i), animatedConfig, hitboxConfig);
    end
    
    foo = add_eventBoxes(mapXml, eventStruct);
end
%gets the layer xml node for the provided layer string.
function foo = get_layer_xml(layerString, animatedConfig, hitboxConfig)
    if layerString == ""
        foo = "";
        return
    end
    
    layerName = split(layerString, '>');
    layerStruct.nameAttribute = layerName(1);
    layerChar = char(layerName(2));
    
    row = 0;
    column = 0;
    
    startDex = 1;
    tileNum = 1;
    atileNum = 1;
    for i=1:length(layerChar)
        if layerChar(i) == '|' || layerChar(i) == ';'
            if(startDex > 1)
                tileString = layerChar(startDex+1:i-1);
                if tileString ~= ""
                    if(tile_has_animation(tileString, animatedConfig))
                        layerStruct.AnimatedTile(atileNum) = create_tile_xml(tileString, animatedConfig, hitboxConfig, row, column);
                        atileNum = atileNum+1;
                    else
                        layerStruct.Tile(tileNum) = create_tile_xml(tileString, animatedConfig, hitboxConfig, row, column);
                        tileNum = tileNum+1;
                    end
                end
            end
            
            startDex=i;
            
            if layerChar(i) == '|'
                column = column+1;
            end
            if layerChar(i) == ';'
                row = row+1;
                column = 0;
            end
        end
    end
    
    foo = layerStruct;
end
%creates the xml node for the provided tile string.
function foo = create_tile_xml(tileString, animatedConfig, hitboxConfig, row, column)
     xPos = column * 64;
     yPos = (row+1) * 64;
     
     nameArr = split(tileString, '{');
     
     Tile.tileSet = nameArr(1);
     Tile.nameAttribute = tileString;
     Tile.tileSetCoordinate = nameArr(end);
     Tile.tileMapCoordinate = "{X:"+string(column)+" Y:"+string(row)+"}";
     Tile.positionBox = "{X:"+string(xPos)+" Y:"+string(yPos)+" Width:64 Height:64}";
     
     if(tile_has_hitbox(tileString, hitboxConfig))
        Tile.hitboxes = get_tile_hitbox(tileString, hitboxConfig, "{X:"+string(xPos)+" Y:"+string(yPos)+"}");
     end
     if(tile_has_animation(tileString, animatedConfig))
        Tile.animation = get_tile_animation(tileString, animatedConfig);
     end
     foo = Tile;
end
%determines if the provided tile has a animation or not.
function foo = tile_has_animation(tileString, animatedConfig)
    for i = 1:length(animatedConfig.tileSet)
        tileSetName = animatedConfig.tileSet(i).nameAttribute;
        tileSetCoordinate = "";
        try
            for j = 1:length(animatedConfig.tileSet(i).tile)
                tileSetCoordinate = animatedConfig.tileSet(i).tile(j).nameAttribute;
                if tileString == tileSetName+tileSetCoordinate
                    foo = true;
                    return;
                end
            end
        catch
                %no animated tiles in this tileSet. 
        end
    end

    foo = false;
end
%gets the animation node for the provided tile.
function foo = get_tile_animation(tileString, animatedConfig)
    for i = 1:length(animatedConfig.tileSet)
        tileSetName = animatedConfig.tileSet(i).nameAttribute;
        tileSetCoordinate = "";
        try
            for j = 1:length(animatedConfig.tileSet(i).tile)
                tileSetCoordinate = animatedConfig.tileSet(i).tile(j).nameAttribute;
                if tileString == tileSetName+tileSetCoordinate
                    foo = animatedConfig.tileSet(i).tile(j).animation;
                    return;
                end
            end
        catch
                %no animated tiles in this tileSet. 
        end
    end

    foo = false;
end
%determines if the provided tile has a hitbox or not.
function foo = tile_has_hitbox(tileString, hitboxConfig)
    for i = 1:length(hitboxConfig.tileSet)
        tileSetName = hitboxConfig.tileSet(i).nameAttribute;
        tileSetCoordinate = "";
        try
            for j = 1:length(hitboxConfig.tileSet(i).tile)
                tileSetCoordinate = hitboxConfig.tileSet(i).tile(j).nameAttribute;
                if tileString == tileSetName+tileSetCoordinate
                    foo = true;
                    return;
                end
            end
        catch
                %no animated tiles in this tileSet. 
        end
    end

    foo = false;
end
%gets the hitbox node for the provided tile.
function foo = get_tile_hitbox(tileString, hitboxConfig, position)
    for i = 1:length(hitboxConfig.tileSet)
        tileSetName = hitboxConfig.tileSet(i).nameAttribute;
        tileSetCoordinate = "";
        try
            for j = 1:length(hitboxConfig.tileSet(i).tile)
                tileSetCoordinate = hitboxConfig.tileSet(i).tile(j).nameAttribute;
                if tileString == tileSetName+tileSetCoordinate
                    foo = hitboxConfig.tileSet(i).tile(j).hitboxes;
                    for k=1:length(foo.tileBox)
                        foo.tileBox(k).position = position;
                    end
                    return;
                end
            end
        catch
            %no tiles hitbox in this tileSet.
        end
    end

    foo = false;
end
%adds the eventboxes to the mapXml.
function foo = add_eventBoxes(mapXml, eventStruct)
    if isstruct(eventStruct)
        eventNum = 1;
        for i=1:length(eventStruct.layer)
           eventNum = 1;
           for j=1:length(eventStruct.layer(i).eventBox)
                mapXml.layer(eventStruct.layer(i).nameAttribute).eventBox(eventNum) = eventStruct.layer(i).eventBox(j);
                mapXml.layer(eventStruct.layer(i).nameAttribute).nameAttribute=eventStruct.layer(i).nameAttribute;
                eventNum = eventNum+1;
           end
        end
    end
    foo = mapXml;
end