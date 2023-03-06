function FindFilepath(){
    var curDoc = app.activeDocument;
    var temp_name = (curDoc.name).split(".")

    var base_path = curDoc.path;
    log(base_path);
    if(String(base_path).search("_WIP")==-1){
        return null
        }
    base_path = String(base_path).split("_WIP")[0] + "Anim"

    // Extenstion. Might need to differ between psd and PSB, or whatever the new bigger format is called.
    var extension = '.psd';

    // Document name
    var docName = curDoc.name;
    //var extension = docName.split(".")[0]
//    var new_name = extension;
    // Gets rid of the extension
//    var docName  = docName.substring( 0, docName.indexOf('_bg_') );
    var new_name = docName.split("_V0")[0]

    full_output_path = base_path + '/' + new_name + "_Anim" + extension;
    return full_output_path
}

function SaveAsPSD( current_document, full_path ) {
    // Options for the soon to be Auto Saved PSD file
    var psd_Opt               = new PhotoshopSaveOptions();
    psd_Opt.layers            = true; // Preserve layers.
    psd_Opt.embedColorProfile = true; // Preserve color profile.
    psd_Opt.annotations       = true; // Preserve annonations.
    psd_Opt.alphaChannels     = true; // Preserve alpha channels.
    psd_Opt.spotColors        = true; // Preserve spot colors.

    // Save active document in the Auto Save folder
    current_document.saveAs( File(full_path), psd_Opt, false );

    }

function log(message){
    $.writeln(message);
}

function Pad(n, width, z) {
  z = z || '0';
  n = n + '';
  return n.length >= width ? n : new Array(width - n.length + 1).join(z) + n;
}

function CreateFolderIfNone(my_folder_path){
    //creates the path given, if it doesn't already exist.
    create_folder = new Folder (my_folder_path);
    if(!my_folder_path.exists) create_folder.create();
    return create_folder
    }

function CreateIncrement(filepath){
    var orig_file = new File(filepath)
    var orig_folder = orig_file.path
    var new_file_name = orig_file.name.split(".")[0];
    var version = 1
    var increment_folder = orig_folder + "/_History/"
    var inc_folder_obj = CreateFolderIfNone(increment_folder)
    inc_files = inc_folder_obj.getFiles("*"+new_file_name+"*")
    version = version + inc_files.length;
    new_file_name = increment_folder + new_file_name + "_V" + Pad(version,3) + "." + orig_file.name.split(".")[1]
    log(new_file_name)
    orig_file.copy(new_file_name);
}

function Run(){
    var filepath = FindFilepath()
    if(!filepath){
        alert("Not a WIP file!");
        return null
        }
    log(filepath);
    file_obj = new File(filepath)
    if(file_obj.exists){
        log("Already Exists");
        CreateIncrement(filepath)
    }
    var curDoc = app.activeDocument;
    SaveAsPSD(curDoc,filepath);
}
Run()