#target.photoshop
app.preferences.rulerUnits = Units.PIXELS;
app.preferences.typeUnits = TypeUnits.PIXELS;
cTID = function(s) { return app.charIDToTypeID(s); };
sTID = function(s) { return app.stringIDToTypeID(s); };


function FlattenLayerSet(unflattened_layerset){
    //alert("trying to flatten " + unflatten_layerset);
    return unflattened_layerset.merge();
    }

function Run(){
    var curDoc = app.activeDocument;
    var top_sets = curDoc.layerSets;
    var selectedLayers = getSelectedLayers(curDoc);


    for( i = (selectedLayers.length-1); i >=0; i--) {
        log(selectedLayers[i]);
        var cur_layer = selectedLayers[i];
        var cur_name = cur_layer.name;
        if(cur_layer instanceof LayerSet ){
            var new_layer = FlattenLayerSet(cur_layer);
            new_layer.name = cur_name
            log(new_layer.parent)
            if(new_layer.parent instanceof Document){
                var new_layerset = curDoc.layerSets.add()
                new_layerset.name = cur_name
                new_layerset.move(new_layer, ElementPlacement.PLACEAFTER)
                new_layer.move(new_layerset, ElementPlacement.INSIDE)
                }
            }
     }


}
function log(message){
    $.writeln(message);    
}

function newGroupFromLayers(doc) {
    var desc = new ActionDescriptor();
    var ref = new ActionReference();
    ref.putClass( sTID('layerSection') );
    desc.putReference( cTID('null'), ref );
    var lref = new ActionReference();
    lref.putEnumerated( cTID('Lyr '), cTID('Ordn'), cTID('Trgt') );
    desc.putReference( cTID('From'), lref);
    executeAction( cTID('Mk  '), desc, DialogModes.NO );
};

function undo() {
   executeAction(cTID("undo", undefined, DialogModes.NO));
};

function getSelectedLayers(doc) {
  var selLayers = [];
  newGroupFromLayers();

  var group = doc.activeLayer;
  var layers = group.layers;

  for (var i = 0; i < layers.length; i++) {
    selLayers.push(layers[i]);
  }

  undo();

  return selLayers;
};

Run()
