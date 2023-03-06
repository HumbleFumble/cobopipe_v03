function Run(){
    var curDoc = app.activeDocument;
    var temp_name = (curDoc.name).split(".")
    var doc_duplicate = curDoc.duplicate( temp_name[0] + "_Temp." + temp_name[1]);
    var curDoc = app.activeDocument;
    }
Run()