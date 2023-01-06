function importFootage(paths, sequence){
    // filePaths = array of file paths to be imported
    // suppressUI = boolean wether to suppress UI when importing
    // targetBin = bin object (app.project.getInsertionBin())
    // importAsNumberedStills = boolean, import as sequence?
    // app.project.importFiles(filePaths, suppressUI, targetBin, importAsNumberedStills)
    var bin = app.project.getInsertionBin();
    return app.project.importFiles(paths, true, bin, sequence)
}

importFootage(["P:\\_WFH_Projekter\\930486_MiaMagicPlayground_S3-4\\4_Production\\Film\\E01\\E01_SQ010\\E01_SQ010_SH010\\05_CompOutput\\E01_SQ010_SH010_CompOutput.mov"], false);