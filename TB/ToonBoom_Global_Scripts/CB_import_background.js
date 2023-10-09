var Utils = require("CB_VectorizeUtils.js");
var GetInfo = require("CB_GetInfo.js")


function import_background(){
    var all_nodes = node.subNodes('Top')
    var biggest_number = 0;
    for(var i=0; i<all_nodes.length; i++){
        if(all_nodes[i].substring(0, 15) == 'Top/BACKGROUND_'){
            if(isNumber(all_nodes[i].substring(15, 17))){
                var number = Math.round(all_nodes[i].substring(15, 17))
                if(number > biggest_number){
                    biggest_number = number
                }
            }
        }
    }
    biggest_number = biggest_number + 1;
    var number_string = pad(biggest_number, 2, '0');
    var group_name = 'BACKGROUND_' + number_string;

    //Insert python script here:
    var file_path = FileDialog.getOpenFileName("*.psd", "Please select the background to import");
    // var file_path = 'P:/930462_HOJ_Project/Production/Asset/Environment/Nidavellir/HollowMountain/MagnusOffice/Anim/MagnusOffice_INT_0100_Anim.psd'; // For testing
    
    if  (file_path === undefined){
        MessageLog.trace('File Dialog was cancelled.')
        return;
    }
    
    var object = import_psd(file_path)
    var nodes = []

    for(var i=0;i<object.layers.length;i++){
        var basename = object.baseElementName;
        if(object.layers[i].layerPathComponents.length === 0){
            var node_path = 'Top/' + basename
        } else {
            var node_path = 'Top/' + basename + '_' + object.layers[i].layerPathComponents[0];
        }
        if(nodes.indexOf(node_path) >= 0){
            continue; 
        }
        disconnect_all_connections(node_path);
        nodes.push(node_path);
    }

    nodes = group_nodes(nodes, group_name);
    nodes = remove_basename(nodes, object.baseElementName);
    nodes = split_frame_nodes(nodes);
    var frame_nodes = nodes[0];
    nodes = nodes[1];
    var frames_group = null;
    
    if(frame_nodes.length>0){
        frame_nodes = group_nodes(frame_nodes, 'Frames');
        frames_group = node.parentNode(frame_nodes[0]);
        var frames_input = node.getGroupInputModule(frames_group, "", 0, 0, 0);
        var frames_output = node.getGroupOutputModule(frames_group, "", 0, 0, 0);
        var frame_name = frame_nodes[0].split('/')[frame_nodes[0].split('/').length-1];
        var frames_composite = frame_nodes[0].replace(frame_name, 'Composite');
        disconnect_all_connections(frames_composite);
        node.link(frames_composite, 0, frames_output, 0, false, false);
        node.setCoord(frames_input, 0-node.width(frames_input)/2, -100);
        node.setCoord(frames_composite, 0-node.width(frames_composite)/2, 100);
        node.setCoord(frames_output, 0-node.width(frames_output)/2, 200);
        var node_spacing = 200;
        var node_fan_width = (frame_nodes.length - 1) * node_spacing;
        frame_nodes = frame_nodes.sort()
    
        for(var i=0; i<frame_nodes.length; i++){
            disconnect_all_connections(frame_nodes[i]);
            node.link(frames_input, 0, frame_nodes[i], 0, false, false);
            node.link(frame_nodes[i], 0, frames_composite, 0);
            var x_coord = node_spacing * i - (node_fan_width / 2);
            var y_coord = 0; // -150 + ((250 / frame_nodes.length) * i)
            node.setCoord(frame_nodes[i], x_coord-node.width(frame_nodes[i])/2, y_coord);
        }
    }


    nodes = custom_sort_nodes(nodes);
    nodes = add_bgnode_tag(nodes);
    if(frames_group != null){
        nodes.splice(0, 0, frames_group);
    }
    var group = node.parentNode(nodes[0]);
    var input = node.getGroupInputModule(group, "", 0, 0, 0);
    var output = node.getGroupOutputModule(group, "", 0, 0, 0);
    composite = group + '/Composite'
    disconnect_all_connections(input);
    node.setCoord(input, 0-node.width(input)/2, -400)
    var main_peg = node.add(group, 'Main-P', 'PEG', 0, -300, 0);
    var frames_peg = node.add(group, 'Frames-P', 'PEG', -400, -200, 0);
    var fg_peg = node.add(group, 'FG-P', 'PEG', -200, -200, 0);
    var mg_peg = node.add(group, 'MG-P', 'PEG', 0, -200, 0);
    var bg_peg = node.add(group, 'BG-P', 'PEG', 200, -200, 0);
    var misc_peg = node.add(group, 'Misc-P', 'PEG', 400, -200, 0);
    node.setCoord(main_peg, 0-(node.width(main_peg)/2), -300);
    node.setCoord(frames_peg, -400-(node.width(frames_peg)/2), -200);
    node.setCoord(fg_peg, -200-(node.width(fg_peg)/2), -200);
    node.setCoord(mg_peg, 0-(node.width(mg_peg)/2), -200);
    node.setCoord(bg_peg, 200-(node.width(bg_peg)/2), -200);
    node.setCoord(misc_peg, 400-(node.width(misc_peg)/2), -200);
    node.link(input, 0, main_peg, 0, false, false)
    node.link(main_peg, 0, frames_peg, 0, false, false)
    node.link(main_peg, 0, fg_peg, 0, false, false)
    node.link(main_peg, 0, mg_peg, 0, false, false)
    node.link(main_peg, 0, bg_peg, 0, false, false)
    node.link(main_peg, 0, misc_peg, 0, false, false)
    var node_spacing = 250;
    var node_fan_width = (nodes.length - 1) * node_spacing;
    for(var i=0; i<nodes.length; i++){
        disconnect_all_connections(nodes[i])
        var name = nodes[i].split('/')[nodes[i].split('/').length-1];
        var peg_name = name.replace('BGNODE_', '') + '-P';
        var x_coord = node_spacing * i - (node_fan_width / 2);
        var y_coord = 0; // -150 + ((250 / frame_nodes.length) * i)
        var peg_node = node.add(group, peg_name, 'PEG', x_coord, y_coord-100, 0);
        node.setCoord(peg_node, x_coord - (node.width(peg_node) / 2), y_coord-100);
        node.setCoord(nodes[i], x_coord - (node.width(nodes[i]) / 2), y_coord);
        if(name.substring(0, 6) == "Frames"){
            node.link(frames_peg, 0, peg_node, 0, false, false);
        } else if (name.substring(0, 9) == "BGNODE_FG") {
            node.link(fg_peg, 0, peg_node, 0, false, false);
        } else if (name.substring(0, 9) == "BGNODE_MG") {
            node.link(mg_peg, 0, peg_node, 0, false, false);
        } else if (name.substring(0, 9) == "BGNODE_BG") {
            node.link(bg_peg, 0, peg_node, 0, false, false);
        } else {
            node.link(misc_peg, 0, peg_node, 0, false, false);
        }
        node.link(peg_node, 0, nodes[i], 0, false, false);
        node.link(nodes[i], 0, composite, 0)

        extend_exposure(nodes[i])
    }
    node.setCoord(composite, 0-node.width(composite)/2, 100);
    node.setCoord(output, 0-node.width(output)/2, 200);

    node.getElementId(nodes)


    currentDate = new Date();
    var date_string = pad(currentDate.getDate(), 2, '0') + "/" + pad((currentDate.getMonth() + 1), 2, '0') + "/" + currentDate.getFullYear();
    var time_string = pad(currentDate.getHours(), 2, '0') + ":" + pad(currentDate.getMinutes(), 2, '0') + ":" + pad(currentDate.getSeconds(), 2, '0');
    var import_info = "Directory: " + file_path + "\nTimestamp: " + date_string + " - " + time_string + "\n";
    
    backdrop_x_coord = Math.round((-node_fan_width / 2) * 1.4);
    backdrop_y_coord = Math.round(-400 * 1.2);
    backdrop_width = Math.abs(backdrop_x_coord * 2);
    backdrop_height = Math.abs(Math.round(600 * 1.4));
    var myBackdrop = {
        "position"    : {"x": backdrop_x_coord, "y" :backdrop_y_coord, "w":backdrop_width, "h":backdrop_height},
        "title"       : {"text" : object.baseElementName},
        "description" : {"text" : import_info},
        "color"       : fromRGBAtoInt(80, 87, 95, 255)
    };
    Backdrop.addBackdrop(group, myBackdrop)
}

function isNumber(value) {
    if (typeof value === "string") {
        return !isNaN(value);
    }
}

function pad(n, width, z) {
    z = z || '0';
    n = n + '';
    return n.length >= width ? n : new Array(width - n.length + 1).join(z) + n;
}

function import_psd(path){
    var options = {
        showProgressUI : true,
        noScale : true,
        importType : Utils.IMPORT_TYPE.TVG_BITMAP,
        bitmapAlignment : Utils.ALIGNMENT.ACTUAL_SIZE,
        premultiply : Utils.PREMULTIPLY.STRAIGHT,
        forceSingleLayer : false,
    };
    return Utils.importDrawingInNewElementNode(path, options);
}

function disconnect_all_connections(node_path){
    var number_of_inputs = node.numberOfInputPorts(node_path);
    for(var j=0; j<number_of_inputs; j++){
        var current_input = node.srcNode(node_path, j);
        node.unlink(node_path, j);
    }

    var number_of_outputs = node.numberOfOutputPorts(node_path);
    var list_of_destinations = [];
    for(var i=0; i<number_of_outputs; i++){
        var number_of_links = node.numberOfOutputLinks(node_path, i);
        for(var j=0; j<number_of_links; j++){
            list_of_destinations.push(node.dstNode(node_path, i, j));
        }
    }
    for(var i=0; i<list_of_destinations.length; i++){
        var number_of_inputs = node.numberOfInputPorts(list_of_destinations[i]);
        for(var j=0; j<number_of_inputs; j++){
            var current_input = node.srcNode(list_of_destinations[i], j);
            if(current_input === node_path){
                node.unlink(list_of_destinations[i], j);
            }
        }
    }
}

function group_nodes(nodes, name){
    node.createGroup(nodes.toString(), name);
    new_paths = [];
    for(var i=0; i<nodes.length; i++){
        var node_path = nodes[i].replace(
            nodes[i].split('/')[nodes[i].split('/').length-1],
            name + '/' + nodes[i].split('/')[nodes[i].split('/').length-1]
        );
        new_paths.push(node_path);
    }
    return new_paths
}

function remove_basename(nodes, basename){
    renamed_nodes = []
    for(var i=0; i<nodes.length; i++){
        var old_name = nodes[i].split('/')[nodes[i].split('/').length-1];
        var new_name = old_name.replace(basename + '_', '');
        var success = node.rename(nodes[i], new_name);
        if(success === true){
            var new_path = nodes[i].replace(old_name, new_name);
            renamed_nodes.push(new_path);
        } else {
            MessageLog.trace('Failed to rename ' + nodes[i])
            renamed_nodes.push(nodes[i]);
        }
    }
    return renamed_nodes;
}

function split_frame_nodes(nodes){
    var frame_nodes = [];
    var non_frame_nodes = [];
    for(var i=0; i<nodes.length; i++){
        var name = nodes[i].split('/')[nodes[i].split('/').length-1]
        if(is_frame(name) === true){
            frame_nodes.push(nodes[i])
        } else {
            non_frame_nodes.push(nodes[i])
        }
    }
    return [frame_nodes, non_frame_nodes]
}

function is_frame(name){
    var matches = name.match(RegExp('.*(SQ)\\d{3}(_SH)\\d{3}'));
    if(matches === null){
        return false
    }
    return true
}

function add_bgnode_tag(nodes){
    new_paths = [];
    for(var i=0; i<nodes.length; i++){
        var old_name = nodes[i].split('/')[nodes[i].split('/').length-1];
        var new_name = 'BGNODE_' + old_name;
        node.rename(nodes[i], new_name);
        var new_path = nodes[i].replace(old_name, new_name);
        new_paths.push(new_path)
    }
    return new_paths;
}

function custom_sort_nodes(nodes){
    var fg_nodes = [];
    var mg_nodes = [];
    var bg_nodes = [];
    var to_remove = [];

    for(i in nodes){
        var node_name = nodes[i].split('/')[nodes[i].split('/').length-1]
        if(node_name.slice(0, 2) == 'FG'){
            fg_nodes.push(nodes[i]);
            to_remove.push(nodes[i]);
        }
        if(node_name.slice(0, 2) == 'MG'){
            mg_nodes.push(nodes[i]);
            to_remove.push(nodes[i]);
        }
        if(node_name.slice(0, 2) == 'BG'){
            bg_nodes.push(nodes[i]);
            to_remove.push(nodes[i]);
        }
    }

    for(i in to_remove){
        nodes.splice(nodes.indexOf(to_remove[i]), 1);
    }

    var sorted_list = fg_nodes.sort();
    sorted_list = sorted_list.concat(mg_nodes.sort());
    sorted_list = sorted_list.concat(bg_nodes.sort());
    sorted_list = sorted_list.concat(nodes.sort());

    return sorted_list;
}

function fromRGBAtoInt(r, g, b, a)
{
  return ((a & 0xff) << 24) | ((r & 0xff) << 16) | ((g & 0xff) << 8) | (b & 0xff);
}

function extend_exposure(node_path){
    startFrame = scene.getStartFrame();
	endFrame = scene.getStopFrame();
    current_column = node.linkedColumn(node_path, 'DRAWING.ELEMENT');
    for(var i = startFrame; i<endFrame+1; i++){
        drawing_substitution = column.getEntry(current_column, 1, 1);
        column.setEntry(current_column, 1, i, drawing_substitution);
    }
}

// var script_path = System.getenv("BOM_PIPE_PATH")+"/TB/CB_SelectionPreset.py"
// var myPythonObject = PythonManager.createPyObject(script_path);
// myPythonObject.py.run();