#target.aftereffects

function getKeySelection(){
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

function SetKeys(pr,start_key, end_key){
    var frame_step = 2;
    var fps = 0.04;
    var start_time = start_key.time + (fps*frame_step);
    var new_keytimes = [];
    log("END TIME: " + end_key.time)
    for(var st = start_time; st<(end_key.time-0.01);st = st + (fps*frame_step)){
        log(st)
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

function log(message){
$.writeln(message);
}

app.beginUndoGroup("SteppedKeys")
getKeySelection()
app.endUndoGroup();


