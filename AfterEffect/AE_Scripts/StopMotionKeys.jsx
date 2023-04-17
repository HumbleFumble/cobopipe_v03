#target.aftereffects

function initialiseSteppedKeys(){
    var cur_props = app.project.activeItem.selectedProperties;
    if(cur_props){
        for(p=0; p<cur_props.length;p++){
            var cur_p = cur_props[p]
            if (cur_p.selectedKeys.length >1){
                steppedKeys(cur_p,cur_p.selectedKeys)
                }
            }
        }
}

function steppedKeys(pr,key_index_list){

    var key_obj_list = [];
    for(var k = (key_index_list.length-1);k>=0;k--){
        key_index = key_index_list[k]
        var key_obj = new Object;
        key_obj.key_index = key_index
        key_obj.time = pr.keyTime(key_index)
        key_obj_list.push(key_obj)
        }
    for(kp=(key_obj_list.length-1);kp>=1;kp--){
            var start_key = key_obj_list[kp];
            var end_key = key_obj_list[kp-1];
            SetKeys(pr,start_key,end_key)
        }

    }

function CreateNullLayer(){
    var frame_step = parseInt(cur_win.grp.panel_group.frame_group.et_frame.text);
    var fps = 0.04; // 1/25
    var cur_comp = app.project.activeItem;
    if(!cur_comp.layers.byName(cur_win.grp.panel_group.null_group.et_null.text)){
        var null_layer = cur_comp.layers.addNull()
        null_layer.name = cur_win.grp.panel_group.null_group.et_null.text
        var slider = null_layer.effect.addProperty("ADBE Slider Control");
        for(var ct = cur_comp.displayStartTime; ct<(cur_comp.displayStartTime+cur_comp.duration);ct  = ct  + (fps*frame_step)){
            slider("Slider").addKey(ct)
            }
        }
    }

function SetKeys(pr,start_key, end_key){
    var frame_step = parseInt(cur_win.grp.panel_group.frame_group.et_frame.text);
    var fps = 0.04; // 1/25
    var start_time = start_key.time + (fps*frame_step);
    var new_keytimes = [];
    for(var st = start_time; st<(end_key.time-0.01);st = st + (fps*frame_step)){
        pr.addKey(st);
        new_keytimes.push(st)
        }
    
    for(var nk = 0; nk < new_keytimes.length; nk++){
        var cur_key = pr.nearestKeyIndex(new_keytimes[nk])
        pr.setInterpolationTypeAtKey(cur_key,KeyframeInterpolationType.HOLD,KeyframeInterpolationType.HOLD)
        }
    
    cur_start_key = pr.nearestKeyIndex(start_key.time)
    cur_end_key = pr.nearestKeyIndex(end_key.time)
    log(pr.keyOutInterpolationType(cur_end_key))
    pr.setInterpolationTypeAtKey(cur_start_key, pr.keyInInterpolationType(cur_start_key), KeyframeInterpolationType.HOLD)
    pr.setInterpolationTypeAtKey(cur_end_key, KeyframeInterpolationType.HOLD, pr.keyOutInterpolationType(cur_end_key) )
    }

function initializeSetExpression(){
    var cur_props = app.project.activeItem.selectedProperties;
        if(cur_props.length >0){
            for(p=0; p<cur_props.length;p++){
                var cur_p = cur_props[p]
                setExpression(cur_p)
                }
                return true
        }else{
            return null
        }
    }

function log(message){
$.writeln(message);
}


function setExpression(pr){
    pr.expression = 'src = thisComp.layer("'+ cur_win.grp.panel_group.null_group.et_null.text+ '").effect("Slider Control")("Slider");\
    try {\
    k = src.nearestKey(time).index;\
    if (src.key(k).time > time && src.key(k).index > 1) k--;\
    kTime = src.key(k).time;\
    thisProperty.valueAtTime(kTime);\
    } catch(err) {value};'
    
    }

function clearExpression(){
    var cur_props = app.project.activeItem.selectedProperties;
        if(cur_props){
            for(p=0; p<cur_props.length;p++){
                var cur_p = cur_props[p]
                cur_p.expression = ''
                }
        }
    }





var cur_win = (function(thisObj){
    var isPanel = thisObj instanceof Panel; // true or false
    var dialog = isPanel  ? thisObj : new Window("window", "Stop Motion Keys");

//    var cfg = getConfig()

    dialog.alignChildren = 'left'
    dialog.alignment = ['top','fill']

    dialog.grp = dialog.add("Group{orientation:'column',alignment:['fill','fill'],\
    panel_group: Group{orientation: 'column',\
    null_group: Group{orientation: 'row',alignment:['left','fill'], st_null: StaticText {text: 'Ctrl Layer Name: ', preferredSize: ['90','20']},et_null: EditText{text: 'EFFECTS_TIMESTEP', preferredSize: ['120','20']} },\
    frame_group: Group{orientation: 'row',alignment:['left','fill'], st_frame: StaticText {text: 'Frame Step #', preferredSize: ['90','20']}, et_frame: EditText{text: '2', preferredSize: ['50','20']} } }}")

    dialog.grp.button_group = dialog.grp.add("Group {orientation: 'row', expr_button: Button{text:'Set Expression'},key_button: Button{text: 'Set Keys Directly'}}")
    dialog.grp.extra_button_group = dialog.grp.add("Group {orientation: 'row', clear_button: Button{text:'Clear Expression'}, help_button: Button{text: '?'} }")

    
    

    dialog.name = "Stop Motion Keys";

    dialog.grp.button_group.key_button.onClick = function(){
        app.beginUndoGroup("SteppedKeys")
        initialiseSteppedKeys()

        app.endUndoGroup();
    }
        dialog.grp.button_group.expr_button.onClick = function(){
        app.beginUndoGroup("ExprKeys")
        if(initializeSetExpression()){
            CreateNullLayer()
        }
        app.endUndoGroup();
    }
        dialog.grp.extra_button_group.clear_button.onClick = function(){
        app.beginUndoGroup("clearExpr")
        clearExpression()
        app.endUndoGroup();
    }

    dialog.grp.extra_button_group.help_button.onClick = function(){
        alert("Set Keys Direcly:\nRequires a selection of minimum 2 keys on the same property.\nSets a stepped key in between those for every frame step given\
Set Expression:\nSets an expression that links up with a slider on the layer given in Ctrl Layer Name\nThen it will only update the value where there is keys on that slider")
    }


    if (!isPanel) {
      // if it's a window
      dialog.show();
    } else {
      // if it's a panel
      dialog.layout.layout(true);
      dialog.layout.resize();
      }
    return dialog
})(this);








