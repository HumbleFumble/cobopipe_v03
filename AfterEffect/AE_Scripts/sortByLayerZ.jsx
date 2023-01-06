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

function sortByIndex(a,b){
    prop = "index"
    var to_return = 0
    if(a[prop]<b[prop]){
    to_return =  -1}
    if(a[prop]>b[prop]){
        to_return =  1}
     return to_return
}

function sortByZ(a,b){
    var prop = "position"
    var to_return = 0
    if(!a.threeDLayer){
        return -1
        }
    if(!b.threeDLayer){
        return 1
        }

    if(a[prop].value[2]<b[prop].value[2]){
    to_return =  -1}
    if(a[prop].value[2]>b[prop].value[2]){
        to_return =  1}
     return to_return
}


function log(msg){
    $.writeln(msg)
    }

function sortByLayerZ()
    var curlays = getCurrentSelection()
    var cur_comp = app.project.activeItem;
    curlays.sort(sortByIndex)
    var start_index = curlays[0].index

    if (start_index >=2){
            start_index = start_index -1
        }else{
            start_index = false
            }
    curlays.sort(sortByZ)

    for(var i = (curlays.length-1); i>=0;i--){
        if(start_index){
        curlays[i].moveAfter(cur_comp.layer(start_index))
        }else{
            curlays[i].moveToBeginning()
            }
        }
    }
    
sortByLayerZ()
