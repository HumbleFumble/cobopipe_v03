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

var docRef = app.activeDocument;
var selectedLayers = getSelectedLayers(app.activeDocument);


for( i = 0; i < selectedLayers.length; i++) {
    log(selectedLayers[i]);
    //flatten the current selections
    //make new layerSet named the same as the original layerSet
    //place the new layer in that layerSet
    //
    /*
    selectedLayers[i].selected = true;
    docRef.activeLayer = selectedLayers[i];
    log(docRef.activeLayer.name)*/
 }
