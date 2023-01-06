var base_project_path = "P:\\930499_Borste_02\\Production\\Film"

$.runScript = {

	importEpisodeClicked: function() {
		if(episode < 100){
			alert("Episode value too low.\nAn episode value should be 3 digits.\nExample: 201");
			return;
		}
		if(episode > 999){
			alert("Episode value too high.\nAn episode value should be 3 digits.\nExample: 201");
			return;
		}
	
		var episodeFolder = new Folder(getEpisodePath(episode));
		var sequenceFolders = episodeFolder.getFiles(getEpisodeName(episode) + "_SQ*");
		for(var i = 0;i < sequenceFolders.length;i++){
			importSequence(sequenceFolders[i].fsName)
		}
	},

	importSequenceClicked: function() {
		if(episode < 100){
			alert("Episode value too low.\nAn episode value should be 3 digits.\nExample: 201");
			return;
		}
		if(episode > 999){
			alert("Episode value too high.\nAn episode value should be 3 digits.\nExample: 201");
			return;
		}
		if(sequence > 999){
			alert("Sequence value too high.\nA sequence value should be maximum 3 digits.\nExample: 110");
			return;
		}
	
		var sequenceFolder = new Folder(getSequencePath(episode, sequence));
		importSequence(sequenceFolder.fsName)
	}	
    
}

function importSequence(currentPath){
    var episodeName = getEpisodeName(episode);
    var sequenceFolder = new Folder(currentPath);
    var sequenceName = currentPath.slice(currentPath.length - 5);
    if(binExists(sequenceName, null) == false){
        var sequenceBin = app.project.rootItem.createBin(sequenceName);
    } else {
        var sequenceBin = findBin(sequenceName, null);
    }
    var shotFolders = sequenceFolder.getFiles(episodeName + "_" + sequenceName + "_SH*");
    for(var j = 0;j < shotFolders.length;j++){
		var currentPath = shotFolders[j].fsName;
        var currentShot = currentPath.slice(currentPath.length - 5);
        var passesFolder = new Folder(shotFolders[j].fsName + "\\Passes");
        if (passesFolder.exists == true){
            var tgaStack = passesFolder.getFiles(episodeName + "_" + sequenceName + "_" + currentShot + "_*.tga");
            if(tgaStack != undefined){
                if(tgaStack.length > 0){
                    if(binExists('Footage', sequenceBin) == false){
                        var footageBin = sequenceBin.createBin('Footage');
                    } else {
                        var footageBin = findBin('Footage', sequenceBin);
                    }
                    var footagePath = tgaStack.sort()[0].fsName;
                    var footageName = footagePath.split("\\")[footagePath.split("\\").length - 1];
                    if(footageExists(footageName, null) == false){
                        importFootage(tgaStack.sort()[0].fsName, footageBin, true);
                    }
                }
            }
        }
        if(importSoundCheck == true){
            if(binExists('Audio', sequenceBin) == false){
                var audioBin = sequenceBin.createBin('Audio');
            } else {
                var audioBin = findBin('Audio', sequenceBin);
            }
            var soundFile = new File(shotFolders[j].fsName + "\\" + episodeName + "_" + sequenceName + "_" + currentShot + '_Sound.wav');
            if(soundFile.exists == true){
                var soundName = soundFile.fsName.split("\\")[soundFile.fsName.split("\\").length - 1];
                if(fileExists(soundName, null) == false){
                    importFootage(soundFile.fsName, audioBin, false);
                }
            }
        }
        if(importAnimPreviewCheck == true){
            if(binExists('Preview', sequenceBin) == false){
                var previewBin = sequenceBin.createBin('Preview');
            } else {
                var previewBin = findBin('Preview', sequenceBin);
            }
            var previewFile = new File(sequenceFolder.fsName + "\\_Preview\\" + episodeName + "_" + sequenceName + "_" + currentShot + ".mov");
            if(previewFile.exists == true){
                var previewName = previewFile.fsName.split("\\")[previewFile.fsName.split("\\").length - 1];
                if(footageExists(previewName, null) == false){
                    importFootage(previewFile.fsName, previewBin, false);
                }
            }

        }
    }
}

function getEpisodeName(ep){
    var episodeName = 'S' + String(ep);
    return episodeName;
}

function getEpisodePath(ep){
	var episodeName = getEpisodeName(ep);
	var episodePath = base_project_path + "\\" + episodeName;
	return episodePath;
}

function getSequenceName(seq){
    if(seq < 10){
        var sequenceName = "SQ00" + String(seq);
    } else {
        if(seq < 100){
            var sequenceName = 'SQ0' + String(seq);
        } else {
            if(seq < 1000){
                var sequence = 'SQ00' + String(seq);
            }
        }
    }
    return sequenceName;
}

function getSequencePath(ep, seq){
    var episodePath = getEpisodePath(ep);
    var episodeName = getEpisodeName(ep);
    var sequenceName = getSequenceName(seq);
    var sequencePath = episodePath + '\\' + episodeName + '_' + sequenceName;
    return sequencePath;
}

function footageExists(searchName, item){
    if(item == null){
        var item = app.project.rootItem;
    }
    for(var i=0; i < item.children.numItems;i++){
        if(item.children[i].type == ProjectItemType.CLIP){
            if(item.children[i].name == searchName){
                return true;
            }
        } else {
            if(item.children[i].type == ProjectItemType.BIN){
                result = footageExists(searchName, item.children[i]);
                if(result == true){
                    return true;
                }
            }
        }
    }
    return false;
}

function fileExists(searchName, item){
    if(item == null){
        var item = app.project.rootItem;
    }
    for(var i=0; i < item.children.numItems;i++){
        if(item.children[i].type == ProjectItemType.FILE){
            if(item.children[i].name == searchName){
                return true;
            }
        } else {
            if(item.children[i].type == ProjectItemType.BIN){
                result = footageExists(searchName, item.children[i]);
                if(result == true){
                    return true;
                }
            }
        }
    }
    return false;
}

function binExists(searchName, item){
    if(item == null){
        var item = app.project.rootItem;
    }
    for(var i=0; i < item.children.numItems;i++){
        if(item.children[i].type == ProjectItemType.BIN){
            if(item.children[i].name == searchName){
                return true;
            }
            result = binExists(searchName, item.children[i]);
            if(result == true){
                return true;
            }
        }
    }
    return false;
}

function findBin(searchName, item){
    if(item == null){
        var item = app.project.rootItem;
    }
    for(var i=0; i < item.children.numItems;i++){
        if(item.children[i].type == ProjectItemType.BIN){
            if(item.children[i].name == searchName){
                return item.children[i];
            }
            result = findBin(searchName, item.children[i]);
            if(result != null){
                if(result.name == searchName){
                    return result;
                }
            }
            
        }
    }
    return null;
}

function importFootage(paths, bin, isSequence){
    // filePaths = array of file paths to be imported
    // suppressUI = boolean wether to suppress UI when importing
    // targetBin = bin object (app.project.getInsertionBin())
    // importAsNumberedStills = boolean, import as sequence?
    // app.project.importFiles(filePaths, suppressUI, targetBin, importAsNumberedStills)
    if(bin == null){
        var bin = app.project.getInsertionBin();
    }
    app.project.importFiles(paths, true, bin, isSequence);
}