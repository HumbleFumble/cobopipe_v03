include("CB_GetInfo.js")

function getCamera(){
    var defaultCamera = "Top/" + node.getDefaultCamera();
    var nodeType = node.type(defaultCamera);
  
    if (nodeType != "CAMERA")
    {
        MessageLog.trace("The camera does not seem to be in the Top level group. Looking in selection for it.");
      var n = selection.numberOfNodesSelected();
      for(var i =0 ; i<n ; ++i) 
      {
        var name = selection.selectedNode(i);
        var t = node.type(name);
        if (t == "CAMERA" && node.getName(name) == node.getDefaultCamera())
        {
           nodeType = t;
          defaultCamera = name;
          break;
        }
      }
    }
    if (nodeType != "CAMERA")
    {
       MessageBox.information("The camera is not in the top level group. Please select it from the Timeline or the Node View and call this function again."); 
       return;
    }
    return defaultCamera;
}


function getDrawings(nodes){
	var drawings = [];
	for (var i in nodes){
		if(node.type(nodes[i]) == "READ"){
			drawings.push(nodes[i]);
		};
		if(node.type(nodes[i]) == "GROUP"){
			var out = getDrawings(node.subNodes(nodes[i]));
			drawings = drawings.concat(out);
		};
	}
	MessageLog.trace("Exporting these: " + drawings)
	return drawings;
}


function createSettingsObject()
{
    return {
        type: "Settings",
        frameRate : scene.getFrameRate(), 
        unitsAspectRatioX : scene.unitsAspectRatioX(), 
        unitsAspectRatioY : scene.unitsAspectRatioY(), 
	unitsX: scene.numberOfUnitsX(),
	unitsY: scene.numberOfUnitsY(),
        unitsZ : scene.numberOfUnitsZ(),
	originX: scene.coordAtCenterX(),
	originY: scene.coordAtCenterY(),
        resolutionX : scene.currentResolutionX(),
        resolutionY: scene.currentResolutionY(),
        defaultResolutionFOV : scene.defaultResolutionFOV(),
	startFrame: scene.getStartFrame(),
	endFrame: scene.getStopFrame()
    };
}


function createExportObject(nodePath)
{
    if(node.type(nodePath) == "CAMERA"){
	    var obj = {
        		type : node.type(nodePath),
        		name : node.getName(nodePath),
        		position : [],
        		scale : [],
        		rotation : [],
                override_scene_fov : [],
                fov : []
        }
    } else {
        var obj = {
        		type : node.type(nodePath),
        		name : node.getName(nodePath),
        		position : [],
        		scale : [],
        		rotation : []
        }
    }
    
    for(var i=0 ; i< frame.numberOf() ; ++i)
    {
        var frameNumber = 1+i;
        if(node.type(nodePath) == "CAMERA"){
            var matrix = scene.getCameraMatrix(frameNumber);
        } else {
            var matrix = node.getMatrix(nodePath, frameNumber);
        }

        var position = scene.fromOGL(matrix.extractPosition());
        obj.position.push([i, position.x, position.y, position.z]);

        var rotation = matrix.extractRotation();
        obj.rotation.push([i, rotation.x, rotation.y, rotation.z]);

        var scale = matrix.extractScale();
        obj.scale.push([i, scale.x, scale.y, scale.z]);

        if(node.type(nodePath) == "CAMERA"){
            var override_scene_fov = node.getAttr(nodePath, i, "OVERRIDE_SCENE_FOV")
            obj.override_scene_fov.push([i, override_scene_fov.boolValue()])

            var fov = node.getAttr(nodePath, i, "FOV")
            obj.fov.push([i, fov.doubleValue()])
        }
    }

    return obj;
}
  

function ExportSceneData()
{
    var sceneName = scene.currentScene();
    var splitSceneName = sceneName.split('_');
    var episode = splitSceneName[0];
    var sequence = splitSceneName[1];
    var shot = splitSceneName[2];
    var project_paths = GetProjectPaths();
    var path_a = project_paths.shot_path;
    var path_b = path_a.replace("<seq_path>", project_paths.seq_path)
    var path_c = path_b.replace("<episode_path>", project_paths.episode_path)
    var path_d = path_c.replace("<film_path>", project_paths.film_path)
    var path_e = path_d.replace("<base_path>", project_paths.base_path)
    var path_f = path_e.replace(/\<episode_name>/g, episode)
    var path_g = path_f.replace(/\<seq_name>/g, sequence)
    var path_h = path_g.replace(/\<shot_name>/g, shot)
    var directory = new Dir(path_h)
    if(directory.fileExists(path_h)){
        var path_i = project_paths.shot_comp_folder
        var path_j = path_i.replace('<shot_path>', path_h)
        var comp_directory = new Dir(path_j);
        comp_directory.mkdirs();
        var filename = path_j + "/" + episode + "_" + sequence + "_" + shot + "_SceneData.jsonx"
    } else {
        var filename = FileDialog.getSaveFileName("*.jsonx", "Please select the export filename");
    }
   
    if (!filename)
    {
        MessageLog.trace("No filename specified. Aborting.");
        return;
    }
    var file = new File( filename );
    MessageLog.trace("Exporting in file: " + filename);
    file.open(FileAccess.WriteOnly);

    var defaultCamera = getCamera();
    var data = [createSettingsObject(), createExportObject(defaultCamera)];
    var drawings = getDrawings(selection.selectedNodes());
    for(var i in drawings){
        data.push(createExportObject(drawings[i]))
    }

    file.write(JSON.stringify(data)); 
    file.close();
}