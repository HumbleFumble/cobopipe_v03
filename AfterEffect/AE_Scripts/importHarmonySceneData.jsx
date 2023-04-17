 #include "includes/json2.js";

function loadJson(path){
    var scriptFile = File(path);
    scriptFile.open('r');
    var data = scriptFile.read();
    scriptFile.close();
    return JSON.parse(data);
}

// Adding missing cotangent math function
function cot(n){
    // Could be rewritten as 1/tan(n)
	return (Math.cos(n)/Math.sin(n))
}


function calculateZoom(height, fov){
    return height/(2*Math.tan(((fov/2)*Math.PI)/180));
}

function findComp(tb_duration,rex,rey){
    var cur_comp = app.project.selection[0];
    if(cur_comp==undefined){
        return false;
        }
    if(cur_comp.typeName != "Composition"){
        return false;
        }
    var cur_length = cur_comp.duration;
    var cur_framerate = cur_comp.frameDuration;
    cur_comp.width = rex
    cur_comp.height = rey
    if(cur_length < tb_duration){
        cur_comp.duration = tb_duration;
        alert("Changed length of " + cur_comp.name + " to fit the length from toonboom")
    }

    return cur_comp
}

function importSceneData(path){
    var data = loadJson(path);
    var resolutionX = data[0].resolutionX;
    var resolutionY = data[0].resolutionY;
    var uAspectX = data[0].unitsAspectRatioX;
    var uAspectY = data[0].unitsAspectRatioY;
    var numOfUnitsX = data[0].unitsX;
    var numOfUnitsY = data[0].unitsY;
    var numOfUnitsZ = data[0].unitsZ;
    var originX = data[0].originX;
    var originY = data[0].originY;
    var default_fov = data[0].defaultResolutionFOV;
    var active_fov = {};
    var fps = data[0].frameRate;
    var startFrame = data[0].startFrame;
    var endFrame = data[0].endFrame;
    var duration = ((endFrame - startFrame).toFixed(2) + 1.00)/fps.toFixed(2);
    var startTimecode = (startFrame.toFixed(2)+1)/fps.toFixed(2);
    var compCreationDuration = duration + startTimecode
    var defaultZoom = calculateZoom(resolutionY, default_fov);
    var comp = findComp(compCreationDuration,resolutionX,resolutionY)
    if(!comp){
        var comp = app.project.items.addComp("CameraExport", resolutionX, resolutionY, 1, compCreationDuration, fps);
        }
    comp.displayStartTime = startTimecode // Keyframes not being placed correctly when this is active I think?
//    var objects = sort_data(data)
    var objects = data.slice(1, data.length);
    
    for(var i=0; i < objects.length; i++){

        if(objects[i].type == "CAMERA"){
            var layers = comp.layers;
            var node = layers.addCamera(objects[i].name, [0,0]);
            node.autoOrient = AutoOrientType.NO_AUTO_ORIENT;
            node.resolutionX, node.property("ADBE Camera Options Group").property("ADBE Camera Zoom").setValue(resolutionX)

        }
        

        if(objects[i].type == "READ"){
            var layers = comp.layers;
            var node = layers.addNull();
            node.threeDLayer = true;
            node.name = objects[i].name;
            node.source.name = objects[i].name + "_FromTB";
        }

        var firstFrame = objects[i].position[0][0];
        var lastFrame = objects[i].position[objects[i].position.length - 1][0];

        var posAttr = node.property("Transform").property("Position");
        // var orientation = node.property("Transform").property("Orientation")
        var xrotAttr = node.property("Transform").property("xRotation");
        var yrotAttr = node.property("Transform").property("yRotation");
        var zrotAttr = node.property("Transform").property("zRotation");

        if(objects[i].type == "CAMERA"){
            var zoomAttr = node.property("ADBE Camera Options Group").property("ADBE Camera Zoom")
        }

        if(objects[i].type == "READ"){
            var scaAttr = node.property("Transform").property("Scale");
        }
        
        
        for(var f = firstFrame; f <= lastFrame; f++){
            if(objects[i].type == "CAMERA"){
                var override_scene_fov = objects[i].override_scene_fov[f][1];
                if(override_scene_fov == true){
                    active_fov[f] = objects[i].fov[f][1];
                } else {
                    active_fov[f] = default_fov
                }
            }
        }


        for(var f = firstFrame; f <= lastFrame; f++){
            var timestamp = (f.toFixed(2) + 1.00)/fps.toFixed(2);

            // Based on a rearranged formula for calculating fov     fov = 2 * arctan(height / (2 * width)) * (180 / pi)
            var posX = objects[i].position[f][1] * (((1/2) * resolutionY * cot((Math.PI * active_fov[f])/360))/numOfUnitsX) + (resolutionX/2) - originX;

            // Multiplied by reverse unit aspect ratio and inversed for After Effects y-axis.
            var posY = objects[i].position[f][2] * (((1/2) * resolutionY * cot((Math.PI * active_fov[f])/360))/numOfUnitsY) * (uAspectY/uAspectX) * -1 + (resolutionY/2) - originY;
            
            // Converting Harmony unit based depth to After Effects pixel based depth.
            var posZ = (objects[i].position[f][3]/numOfUnitsZ) * defaultZoom * -1;

            var rotX = objects[i].rotation[f][1];
            var rotY = objects[i].rotation[f][2];
            var rotZ = objects[i].rotation[f][3];

            var rx = rotX * (Math.PI/180) // Converting degrees to radians
            var ry = rotY * (Math.PI/180) 
            var rz = rotZ * (Math.PI/180)

            // Converting Euler Angles to a 3x3 3D Rotation Matrix
            var m11 = Math.cos(rz) * Math.cos(ry)
            var m12 = (Math.cos(rz) * Math.sin(ry) * Math.sin(rx)) - (Math.cos(rx) * Math.sin(rz))
            var m13 = (Math.sin(rz) * Math.sin(rx)) + (Math.cos(rz) * Math.cos(rx) * Math.sin(ry))
            var m21 = Math.cos(ry) * Math.sin(rz)
            var m22 = (Math.cos(rz) * Math.cos(rx)) + (Math.sin(rz) * Math.sin(ry) * Math.sin(rx))
            var m23 = (Math.cos(rx) * Math.sin(rz) * Math.sin(ry)) - (Math.cos(rz) * Math.sin(rx))
            var m31 = -1 * Math.sin(ry)
            var m32 = Math.cos(ry) * Math.sin(rx)
            var m33 = Math.cos(ry) * Math.cos(rx)

            // Converting Rotation Matrix to euler angles with an XYZ rotation order
            var xyz_x_rad = Math.atan((-m23)/ m33);
            var xyz_y_rad = Math.atan(m13 / Math.sqrt(1-(m13*m13)));
            var xyz_z_rad = Math.atan(m12/(-1 * m11));

            var xyz_x = xyz_x_rad / (Math.PI / 180) // Convertinng radians to degrees
            var xyz_y = -xyz_y_rad / (Math.PI / 180) // Needs to be negative to match up in After Effects
            var xyz_z = -xyz_z_rad / (Math.PI / 180) // Needs to be negative to match up in After Effects
            

            if(objects[i].type == "CAMERA"){
                var override_scene_fov = objects[i].override_scene_fov[f][1];
                if(override_scene_fov == true){
                    var fov = objects[i].fov[f][1];
                    var zoom = calculateZoom(resolutionY, fov) / (((objects[i].scale[f][1] + objects[i].scale[f][2])/2)*(4/3)); // This might only work for our current pipeline on høj;
                } else {
                    var zoom = defaultZoom / (((objects[i].scale[f][1] + objects[i].scale[f][2])/2)*(4/3)); // This might only work for our current pipeline on høj
                }
            }

            if(objects[i].type == "READ"){
                var scaX = objects[i].scale[f][1] * 100;
                var scaY = objects[i].scale[f][2] * 100;
            }
            
            posAttr.setValueAtTime(timestamp, [posX, posY, posZ]);
            xrotAttr.setValueAtTime(timestamp, xyz_x);
            yrotAttr.setValueAtTime(timestamp, xyz_y);
            zrotAttr.setValueAtTime(timestamp, xyz_z);
            
            if(objects[i].type == "CAMERA"){
                zoomAttr.setValueAtTime(timestamp, zoom)
            }

            if(objects[i].type == "READ"){
                scaAttr.setValueAtTime(timestamp, [scaX, scaY]);
            }
        }
    }
}

function getCurrentSelection(){
    var cur_comp = app.project.activeItem;
     var cur_layers = null;
    if(cur_comp!=null){
        var cur_layers = cur_comp.selectedLayers;
        }
    if(cur_layers.length>0){
        return cur_layers
        }
    else{
        return false
        }
    }

function sort_data(data){
    var objects = data.slice(1, data.length);
    var camera_objects = [];
    var fg_objects = [];
    var mg_objects = [];
    var bg_objects = [];
    var to_remove = [];

    for(var i=0; i < objects.length; i++){
        var name = objects[i].name
        var type = objects[i].type
        
        if(type == 'CAMERA'){
            camera_objects.push(objects[i]);
            to_remove.push(objects[i]);
        }

        if(name.slice(0, 2) == 'FG'){
            fg_objects.push(objects[i]);
            to_remove.push(objects[i]);
        }

        if(name.slice(0, 2) == 'MG'){
            mg_objects.push(objects[i]);
            to_remove.push(objects[i]);
        }

        if(name.slice(0, 2) == 'BG'){
            bg_objects.push(objects[i]);
            to_remove.push(objects[i]);
        }
    }
    for(i in to_remove){
        objects.splice(objects.indexOf(to_remove[i]), 1);
    }

    var sorted_list = fg_objects.sort();
    sorted_list = sorted_list.concat(mg_objects.sort())
    sorted_list = sorted_list.concat(bg_objects.sort())
    sorted_list = sorted_list.concat(objects.sort())
    sorted_list = sorted_list.concat(camera_objects.sort().reverse())
    sorted_list = sorted_list.reverse()

    return sorted_list
}

function sort_layers_by_stage(ls){
    var camera_objects = [];
    var fg_objects = [];
    var mg_objects = [];
    var bg_objects = [];
    var to_remove = [];

    for(var i=0; i < objects.length; i++){
        var name = objects[i].name
//        var type = objects[i].type

//        if(type == 'CAMERA'){
//            camera_objects.push(objects[i]);
//            to_remove.push(objects[i]);
//        }

        if(name.slice(0, 2) == 'FG'){
            fg_objects.push(objects[i]);
            to_remove.push(objects[i]);
        }

        if(name.slice(0, 2) == 'MG'){
            mg_objects.push(objects[i]);
            to_remove.push(objects[i]);
        }

        if(name.slice(0, 2) == 'BG'){
            bg_objects.push(objects[i]);
            to_remove.push(objects[i]);
        }
    }
    for(i in to_remove){
        objects.splice(objects.indexOf(to_remove[i]), 1);
    }

    var sorted_list = fg_objects.sort();
    sorted_list = sorted_list.concat(mg_objects.sort())
    sorted_list = sorted_list.concat(bg_objects.sort())
    sorted_list = sorted_list.concat(objects.sort())
    sorted_list = sorted_list.concat(camera_objects.sort().reverse())
    sorted_list = sorted_list.reverse()

    return sorted_list
}
function alert_list(ml){
    alert_print = [];
    for(var i=0;i<ml.length;i++){
        alert_print.push(ml[i].name)
    }
    $.writeln(alert_print);
}

function ui_func(){
    var my_source = "window {text: 'Import Toonboom Scene Data', alignChildren: 'left' , alignment: ['top','fill'],preferredSize: [215,150], properties: {resizeable: false},\
                base_panel: Panel {text: 'Pick scene-data.jsonx:', \
                    alignment:['fill','top'], alignChildren: 'left',\
                    file_info_st: StaticText {text:'Current File:',preferredSize: [215,22], justify:'left' }, \
                    file_et: EditText{text:'', preferredSize: [200,22]},\
                    browse_button: Button{ text: 'Browse to file'}, \
                    },\
                options_panel: Panel {text: 'Options:', \
                    alignment:['fill','left'], alignChildren: 'left', orientation: 'row',\
                        at_file_check: Checkbox {text: 'start browsing at file location',value: true},\
                        at_project_check: Checkbox {text: 'start browsing at project root',value: true}, \
                    },\
                action_panel: Panel {text: 'Run this : ', alignChildren: 'left' ,\
                    info_label : StaticText {text:'If a Composition is selected in the project window import to that. Otherwise make new.'},\
                    button_group: Group{ orientation:'row', \
                    import_data_button: Button{ text: 'Import Data from file', helpTip: ''}\
                    compare_and_sort: Button{ text: 'Try to sort layers from naming'}\
                    },\
                },\
            }";
     var my_window = new Window(my_source);
     my_window.data = null;
     my_window.base_panel.browse_button.onClick=function(){
        var start_folder = "P:/930462_HOJ_Project/Production/";
        if( my_window.options_panel.at_project_check.value){
            start_folder = "P:/930462_HOJ_Project/Production/";
            }
        if( my_window.options_panel.at_file_check.value){
//            start_folder = "P:/930462_HOJ_Project/Production/";
            var cur_file = app.project.file;
            if(cur_file){
                start_folder = cur_file.parent;
                }
            }
        my_window.jsonx_file = new File(start_folder).openDlg("Select .jsonx file", "JSON:*.json;*.jsonx,All files:*.*", false);
        if(my_window.jsonx_file != null){
            my_window.base_panel.file_et.text = my_window.jsonx_file.fullName;
            return;
        }
        

     }
     //        if(data != null){
//            importSceneData(data)
//        }
//        run();
    my_window.action_panel.button_group.import_data_button.onClick=function(){
        var data = new File(my_window.base_panel.file_et.text);
        if(data != null){
            importSceneData(data)
            }
    }
    my_window.action_panel.button_group.compare_and_sort.onClick=function(){
        sort_layers ()
    }
     return my_window
}

// function run(){
//     defaultFolder = "C:/" // Find shot folder based on file name?
//     var data = new File(defaultFolder).openDialog("JavaScript:*.jsx;All files:*.*");
//     if(data != null){
//         importSceneData(data)
//     }
    
// }


// This func is intended to sort fast & stable an array of objects


// along a property `prop` that takes UINT values in [0..0xFFFF].


// (Performance gain should be sensible for array.length≈10^3.)


function n_compare(a,b){
    prop = 'name'
    //$.writeln("A: " + a[prop])
    //$.writeln("B: " + b[prop])
    var to_return = 0
    if(a[prop].toLowerCase()<b[prop].toLowerCase()){
    to_return =  -1}
    if(a[prop].toLowerCase()>b[prop].toLowerCase()){
        to_return =  1}
    // $.writeln(a[prop]  + " < " + b[prop] + " = " + String(to_return))
     return to_return
}

function sort_layers(){
    var c_layers = getCurrentSelection()
    c_layers.sort(n_compare)

    for (var i=c_layers.length-1; i>=0; i--){
        c_layers[i].moveToBeginning();
    }    
}


dia = ui_func()
dia.show()
