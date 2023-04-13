#target Photoshop
app.bringToFront();
main();

function getSelectedLayersIdx(){
      var selectedLayers = new Array;
      var ref = new ActionReference();
      ref.putEnumerated( charIDToTypeID("Dcmn"), charIDToTypeID("Ordn"), charIDToTypeID("Trgt") );
      var desc = executeActionGet(ref);
      if( desc.hasKey( stringIDToTypeID( 'targetLayers' ) ) ){
         desc = desc.getList( stringIDToTypeID( 'targetLayers' ));
          var c = desc.count
          var selectedLayers = new Array();
          for(var i=0;i<c;i++){
            try{
               activeDocument.backgroundLayer;
               selectedLayers.push(  desc.getReference( i ).getIndex() );
            }catch(e){
               selectedLayers.push(  desc.getReference( i ).getIndex()+1 );
            }
          }
       }else{
         var ref = new ActionReference();
         ref.putProperty( charIDToTypeID("Prpr") , charIDToTypeID( "ItmI" ));
         ref.putEnumerated( charIDToTypeID("Lyr "), charIDToTypeID("Ordn"), charIDToTypeID("Trgt") );
         try{
            activeDocument.backgroundLayer;
            selectedLayers.push( executeActionGet(ref).getInteger(charIDToTypeID( "ItmI" ))-1);
         }catch(e){
            selectedLayers.push( executeActionGet(ref).getInteger(charIDToTypeID( "ItmI" )));
         }
     var vis = app.activeDocument.activeLayer.visible;
        if(vis == true) app.activeDocument.activeLayer.visible = false;
        var desc9 = new ActionDescriptor();
    var list9 = new ActionList();
    var ref9 = new ActionReference();
    ref9.putEnumerated( charIDToTypeID('Lyr '), charIDToTypeID('Ordn'), charIDToTypeID('Trgt') );
    list9.putReference( ref9 );
    desc9.putList( charIDToTypeID('null'), list9 );
    executeAction( charIDToTypeID('Shw '), desc9, DialogModes.NO );
    if(app.activeDocument.activeLayer.visible == false) selectedLayers.shift();
        app.activeDocument.activeLayer.visible = vis;
      }
      return selectedLayers;
};

function getLayerNameByIndex( idx ) {
    var ref = new ActionReference();
    ref.putProperty( charIDToTypeID("Prpr") , charIDToTypeID( "Nm  " ));
    ref.putIndex( charIDToTypeID( "Lyr " ), idx );
    return executeActionGet(ref).getString(charIDToTypeID( "Nm  " ));
};

function putLayerNameByIndex( idx, name ) {
     if( idx == 0 ) return;
    var desc = new ActionDescriptor();
        var ref = new ActionReference();
        ref.putIndex( charIDToTypeID( 'Lyr ' ), idx );
    desc.putReference( charIDToTypeID('null'), ref );
    desc.putBoolean( charIDToTypeID( "MkVs" ), false );
        var nameDesc = new ActionDescriptor();
        nameDesc.putString( charIDToTypeID('Nm  '), name );
    desc.putObject( charIDToTypeID('T   '), charIDToTypeID('Lyr '), nameDesc );
    executeAction( charIDToTypeID( 'slct' ), desc, DialogModes.NO );
    executeAction( charIDToTypeID('setd'), desc, DialogModes.NO );
};

function checkName(name){
    //log("replace" + path);
    var new_name = name
    var t = new RegExp('(BG_|FG_|MG_)','g')
    var n = new RegExp('([0-9]{3}_)','g')
    var m = name.match(t,name)
    var m_n = name.match(n,name)
    if(m){
        new_name = new_name.replace(m,"");
        }
    if(m_n){
        new_name = new_name.replace(m_n,"");
        }
    return new_name
}

function Pad(n, width, z) {
  z = z || '0';
  n = n + '';
  return n.length >= width ? n : new Array(width - n.length + 1).join(z) + n;
}


function main(){
    if(!documents.length) return;

// DIALOG
// ======
var dialog = new Window("dialog", undefined, undefined, {resizeable: true});
    dialog.text = "Dialog";
    dialog.orientation = "column";
    dialog.alignChildren = ["center","top"];
    dialog.spacing = 10;
    dialog.margins = 16;

// GRP
// ===
var grp = dialog.add("group", undefined, {name: "grp"});
    grp.orientation = "row";
    grp.alignChildren = ["left","center"];
    grp.spacing = 10;
    grp.margins = 0;

var st_prefix = grp.add("statictext", undefined, undefined, {name: "st_prefix"});
    st_prefix.text = "Prefix";

var dd_prefix_array = ["FG","MG","BG"];
var dd_prefix = grp.add("dropdownlist", undefined, undefined, {name: "dd_prefix", items: dd_prefix_array});
    dd_prefix.selection = 0;

// DIALOG
// ======
var run_bttn = dialog.add("button", undefined, undefined, {name: "run_bttn"});
    run_bttn.text = "Ok";
    

var cancel_bttn = dialog.add("button", undefined, undefined, {name: "cancel_bttn"});
    cancel_bttn.text = "Cancel";


run_bttn.onClick = function(){
    var selection = getSelectedLayersIdx()
    for(x=0;x<selection.length;x++){
        var cur_name = getLayerNameByIndex(selection[x])
        var new_name = checkName(cur_name)
        var new_name = String(dd_prefix.selection) +"_" +Pad(((selection.length-x)*10),3) + "_"+ new_name
        putLayerNameByIndex(selection[x],new_name)
    }
    dialog.close();
}
dialog.show();

};