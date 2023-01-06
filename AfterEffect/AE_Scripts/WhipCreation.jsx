//This is meant to be a script to quickly connect layers, like using the pick-whip manually in after effects

//This could have an ui where you can pick which attributes you want to connect

function log(message){
$.write(message + "\n");
//alert(message);
    }

//Otherwise get the selected layers dynamically

//It seems the pick-whip really just creates expressions on the individual attribute/property
//So an example would be:
function create_whip(source_layer, dest_layer){
    app.beginUndoGroup("WhipConnect")
    //Check the ui checkboxes which connections should be made
    var property_list = []
    if(dia.property_panel.position_check.value){
        property_list.push("position");
        }
    if(dia.property_panel.scale_check.value){
        property_list.push("scale");
        }
    if(dia.property_panel.rotation_check.value){
        property_list.push("xRotation");
        property_list.push("yRotation");
        property_list.push("zRotation");
        }

    //zero out the current value to avoid double transform
    //property_list = ["position","scale","orientation"]
    //make connections
    for(var i=0;i<property_list.length;i++){
        var cur_prop = property_list[i];
        var cur_value = dest_layer.property(cur_prop).value;
        if(dia.property_panel.zero_check.value){
            var end_value = [];
            for(var x=0;x<cur_value.length;x++){
                end_value.push(0.0);
                }
            }else{
                var end_value = cur_value;
               }
        if(source_layer.threeDLayer){
            dest_layer.threeDLayer = true;
            }
        dest_layer.property(cur_prop).setValue(end_value);
        dest_layer.property(cur_prop).expression = 'thisComp.layer("' + source_layer.name + '").transform.' + cur_prop + '+value';
    }
app.endUndoGroup();

}

function my_window(){
    var my_source = "window {text: 'Create Whip from Layers', alignChildren: 'left' , alignment: ['top','fill'],preferredSize: [215,150], properties: {resizeable: false},\
            base_panel: Panel {text: 'Pick the layers:', \
                alignment:['fill','top'], alignChildren: 'left',\
                source_info_st: StaticText {text:'Pick the source layer',preferredSize: [215,22], justify:'left' }, \
                source_et: EditText{text:'Source Layer', preferredSize: [200,22]},\
                source_button: Button{ text: 'Pick Source'}, \
                dest_info_st: StaticText {text:'Pick the dest layer',preferredSize: [215,22], justify:'left' }, \
                dest_et: EditText{text:'dest Layer', preferredSize: [200,22]},\
                dest_button: Button{ text: 'Pick dest'}, \
                },\
            property_panel: Panel {text: 'Options:', \
                alignment:['fill','left'], alignChildren: 'left', orientation: 'row',\
                    position_check: Checkbox {text: 'position',value: true},\
                    scale_check: Checkbox {text: 'scale',value: true}, \
                    rotation_check: Checkbox {text: 'rotation',value: true}\
                    zero_check: Checkbox {text: 'zero out',value: true}\
                },\
            action_panel: Panel {text: 'Run this : ', alignChildren: 'left' ,\
                button_group: Group{ orientation:'row', \
                quick_select_button: Button{ text: 'Quick Select', helpTip: 'Select both at once, first the destination layer, than the source layer'}\
                create_mass_whip_button: Button{ text: 'Mass Connect'}\
                create_whip_button: Button{ text: 'Create Connections'}\
                },\
            },\
        }";
       var my_window = new Window(my_source);
       my_window.source_layer = null;
       my_window.dest_layer = null;
        my_window.base_panel.source_button.onClick = function(){
            var my_layer = getCurrentSelection()[0]
            if(my_layer){
                my_window.base_panel.source_et.text = my_layer.name;
                my_window.source_layer = my_layer;
                } 
            }
        my_window.base_panel.dest_button.onClick = function(){
            var my_layer = getCurrentSelection()[0]
            if(my_layer){
                my_window.base_panel.dest_et.text = my_layer.name;
                my_window.dest_layer = my_layer;
                } 
            }
        my_window.action_panel.button_group.create_whip_button.onClick = function(){
            create_whip (my_window.source_layer, my_window.dest_layer)
            }
        my_window.action_panel.button_group.create_mass_whip_button.onClick = function(){
            mass_create_whip()
        }
        my_window.action_panel.button_group.quick_select_button.onClick = function(){ quickSelect()}
        //my_window.action_panel.button_group.save_button.onClick = SaveCompFile;
    //    my_window.onClose = function(){
    //        SaveWindow(my_window);
    //	}

        return my_window;
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

function quickSelect(){
    var cur_layers = getCurrentSelection()
    if(cur_layers.length>1){
        var source = cur_layers[1];
        var dest = cur_layers[0];
        var str = source.name + " : " + dest.name;
        dia.base_panel.dest_et.text = dest.name;
        dia.dest_layer = dest;
        dia.base_panel.source_et.text = source.name;
        dia.source_layer = source;
        }
    else{
        alert("Pick both layers for this to work");
        }
   }

function index_sort(a,b){
    prop = "index"
    //$.writeln("A: " + a[prop])
    //$.writeln("B: " + b[prop])
    var to_return = 0
    if(a[prop]<b[prop]){
    to_return =  -1}
    if(a[prop]>b[prop]){
        to_return =  1}
    // $.writeln(a[prop]  + " < " + b[prop] + " = " + String(to_return))
     return to_return
}

function mass_create_whip(){
    var selection = getCurrentSelection();
    selection.sort(index_sort)
    var source = null;
    for(var layer in selection){
        if(selection[layer].nullLayer){
            var source = selection[layer]
        } else {
            if(source != null){
                create_whip(source, selection[layer])
            } else {
                alert(String(selection[layer].name) + " is not beneath a null layer.")
            }
        }
    }
}
//run()
dia = my_window();
dia.show()
// mass_create_whip()