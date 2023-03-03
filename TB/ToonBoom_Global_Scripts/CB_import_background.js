var Utils = require("CB_VectorizeUtils.js");
var GetInfo = require("CB_GetInfo.js")


function main(){
    MessageLog.trace('Script is running.');
    var file_path = 'P:/930462_HOJ_Project/Production/Asset/Environment/Nidavellir/HollowMountain/MagnusOffice/Anim/MagnusOffice_INT_0100_Anim.psd';
    var object = import_psd(file_path)
    var nodes = []

    for(var i=0;i<object.layers.length;i++){
        if(object.layers[i].layer.split(':').length < 1){
            MessageLog.trace('No group');
            var name = object.baseElementName + "_";
            var node_path = 'Top/' + name;
        } else {
            var name = object.baseElementName + "_" + object.layers[i].layer.split(':')[0];
            var node_path = 'Top/' + name;
        }
        disconnect_all_connections(node_path);
        nodes.push(node_path);
    }

    nodes = group_nodes(nodes, object.baseElementName);
    nodes = remove_basename(nodes, object.baseElementName);
    nodes = split_frame_nodes(nodes);
    var frame_nodes = nodes[0]
    nodes = nodes[1]
    
    group_nodes(frame_nodes, 'Frames');
}

function import_psd(path){
    var options = {
        showProgressUI : true,
        noScale : true,
        importType : Utils.IMPORT_TYPE.TVG_BITMAP,
        bitmapAlignment : Utils.ALIGNMENT.ACTUAL_SIZE,
        premultiply : Utils.PREMULTIPLY.STRAIGHT,
        forceSingleLayer : false
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
    node.createGroup(nodes, name);
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

// var script_path = System.getenv("BOM_PIPE_PATH")+"/TB/CB_SelectionPreset.py"
// var myPythonObject = PythonManager.createPyObject(script_path);
// myPythonObject.py.run();