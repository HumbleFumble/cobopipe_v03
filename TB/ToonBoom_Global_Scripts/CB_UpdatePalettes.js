include("T:/_Pipeline/cobopipe_v01-001/TB/ToonBoom_Global_Scripts/CB_CustomSaveAs.js")


function isScenePaletteList(paletteList){
    // Palette list with an element id of -1 are scene palette lists.
    return paletteList.elementId == -1;
}
  

function removePalette(paletteName){
    var paletteList = PaletteObjectManager.getScenePaletteList();
    if(isScenePaletteList(paletteList)){
        for(var i=0; i < paletteList.numPalettes; i++){
            var palette = paletteList.getPaletteByIndex(i);
            MessageLog.trace(palette.getName())
            var name = palette.getName()
            if(name == paletteName){
                paletteList.removePaletteById(palette.id)
                return [paletteList, palette]
            } else {
                if(name.indexOf(paletteName) === 0){
                    var end_of_string = name.split('_')[name.split('_').length-1]
                    if(parseInt(end_of_string) != NaN){
                        paletteList.removePaletteById(palette.id)
                        return [paletteList, palette]
                    }
                }
            }
        }
    }
    return null
}
 

function importPalette(paletteList, palettePath){
    paletteList.addPalette(palettePath);
}


function readJson(path){
    var myFile = new PermanentFile(path);
    myFile.open(1);
    var jsonFileContent = myFile.read();
    myFile.close();
    var jsonContent = JSON.parse(jsonFileContent);
    return jsonContent;
}


function updatePaletteFiles(palette, path){
    var old_palette_path = palette.getPath() + "/" + palette.getName() + ".plt"
    var old_palette = new PermanentFile(old_palette_path)
var old_palette_path
    var new_palette = new PermanentFile(path)
    MessageLog.trace(scene.currentProjectPath())
    if(old_palette_path.indexOf(scene.currentProjectPath()) === 0){
        if(old_palette.exists){
            if(new_palette.exists){
                old_palette.remove()
                old_palette = new PermanentFile(old_palette_path)
                new_palette.copy(old_palette)
            }
        }
    }
    return old_palette_path.replace(".plt", "")
    

}

function run(path){
    var changed = false;
    var pathList = readJson(path)
    // var pathList = ["//dumpap3/production/930462_HOJ_Project/Production/Asset/Prop/GroBirk_sword/GroBrirk_sword_prop_V2/palette-library/GroBirk_sword_colours.plt",
    //                 "//dumpap3/production/930462_HOJ_Project/Production/Asset/Prop/GroBirk_shield/GroBirk_shield_prop_V2/palette-library/GroBirk_shield_colours.plt"];
    for(var i = 0; i < pathList.length; i++){
        var paletteName = pathList[i].split("/")[pathList[i].split("/").length-1].replace(".plt", "")
        //var palettePath = pathList[i].replace(".plt", "")
        var paletteOutput = removePalette(paletteName);
        if(!(paletteOutput == null)){
            var paletteList = paletteOutput[0]
            var palette = paletteOutput[1]
            var palettePath = updatePaletteFiles(palette, pathList[i]);
            importPalette(paletteList, palettePath);
            MessageLog.trace("\n\n    UPDATED :::: " + paletteName)
            System.println("\n\n    UPDATED :::: " + paletteName)
            changed = true;
        }
  
    }
    if(changed == true){
        save_new_version()
        System.println("\n    >> File saved <<\n")
    }
}