// #include "json.jsx";

// var base_project_path = "P:\\930499_Borste_02\\Production\\Film";
// var base_project_path = "P:\\_WFH_Projekter\\930486_MiaMagicPlayground_S3-4\\4_Production\\Film";
var sqPresetPath = "T:\\_Pipeline\\cobopipe_v01-001\\PremierePro\\sequencePresets\\1920x1080-25fps.sqpreset";
var episode = 22;
var sequence = 20;
var importSoundCheck = true;
var importAnimPreviewCheck = true;
var importFastRenderCheck = true;
var importCompPreviewCheck = true;
var importCompMovCheck = true;
var importCompEXRCheck = true;
var importHighestStepOnlyCheck = true;
var createEpisodeTimeCodeCheck = true; // Not done yet
var createShotFrameCountCheck = true;
var createShotNameplateCheck = true;

var defaultFolder = "T:\\_Pipeline\\cobopipe_v01-001\\Configs"
var path = new File(defaultFolder).openDlg("Select .jsonx file");
// var path = "T:\\_Pipeline\\cobopipe_v01-001\\Configs\\Config_MiasMagic2.json"
var configData = loadJson(path);
var config = process_config(configData)
// var sqPresetPath = config.project_paths.premiere_sqpreset
var base_project_path = config.project_paths.base_path.replace("/", "\\") + "\\Film"
var episode_prefix_padding = decipher_regex(config.regex_strings.episode_regex)
var sequence_prefix_padding = decipher_regex(config.regex_strings.seq_regex)
var shot_prefix_padding = decipher_regex(config.regex_strings.shot_regex)


///////////// CONFIG FUNCTIONS ////////////////
function unpack_config(object){
    var update_object = {};

    for(key in object){
        if(typeof object[key] === 'object' && !(object[key] instanceof Array)){
            var output = unpack_config(object[key]);
            for(output_key in output){
                if(!(output_key in update_object)){
                    update_object[output_key] = output[output_key]
                }
            }
        } else {
            update_object[key] = object[key]
        }
    }
    return update_object;
}

function pack_config(ref_object, object){

    for(key in ref_object){
        if(typeof ref_object[key] === 'object' && !(ref_object[key] instanceof Array)){
            
            var output = pack_config(ref_object[key], object);
            for(output_key in output){
                if(output_key in ref_object){
                    ref_object[key] = output[output_key]
                }
            }
        } else {
            ref_object[key] = object[key] 
        }


    }
    
    return ref_object;
}

function process_config(object){
    var update_object = unpack_config(object)

    var number_of_updates = 1
    while(number_of_updates > 0){
        number_of_updates = 0
        for(key in update_object){
            if(typeof update_object[key] === 'string'){
                if(update_object[key].indexOf('<') > -1){
                    var start_index = update_object[key].indexOf('<') + 1 
                    var end_index = update_object[key].indexOf('>') - 1
                    var replace_key = update_object[key].substr(start_index, end_index)

                    if(replace_key in update_object){
                        update_object[key] = update_object[key].replace("<" + replace_key + ">", update_object[replace_key])
                        number_of_updates = ++number_of_updates
                    }
                }
            }
        }
    }

    return pack_config(object, update_object)
}

function process_path(_path, _dict){
    var new_path = _path
    for(key in _dict){
        while(new_path.indexOf("<" + key + ">") > -1){
            new_path = new_path.replace("<" + key + ">", _dict[key])
        }
    }   
    return new_path
}

function loadJson(_path){
    var json_file = File(_path);
    json_file.open('r');
    var data = json_file.read();
    json_file.close();

    return JSON.parse(data);
}
///////////////////////////////////////////////

function importEpisodeClicked(){
    var episode_padding = episode_prefix_padding[1]

    if(episode < 1){
        alert("Episode value too low.\nAn episode value should be " + String(episode_padding) + " digits.");
        return;
    }
    if(episode > Math.pow(10, episode_padding)-1){
        alert("Episode value too high.\nAn episode value should be " + String(episode_padding) + " digits.");
        return;
    }

    var episodeName = getEpisodeName(episode);
    if(footageExists(episodeName, null) == false){
        createSequence(episodeName);
    }
    var episodeSequence = findFootage(episodeName);
    var episodeSequenceObject = findSequence(episodeName)
    var episodeFolder = new Folder(process_path(config.project_paths.episode_path, {"episode_name": episodeName}));
    var sequenceFolders = episodeFolder.getFiles(episodeName + sequence_prefix_padding[0] + "*");
    


    for(var i = 0;i < sequenceFolders.length;i++){
        var sequenceName = getSequenceName(sequenceFolders[i].fsName.substring(sequenceFolders[i].fsName.length - sequence_prefix_padding[1]))
        importSequence(sequenceFolders[i].fsName);

        
        var sequenceItem = findFootage(sequenceName)
        var videoTrack = episodeSequenceObject.videoTracks[0];
        previousClipEnd = new Time()
        if(videoTrack != null){
            if(videoTrack.clips.length > 0){
                var previousClipEnd = videoTrack.clips[videoTrack.clips.length-1].end;
            }
        }
        episodeSequenceObject.insertClip(sequenceItem, previousClipEnd, 0, 0);
    }
    
    if(createEpisodeTimeCodeCheck == true){
        if(binExists('Timecode') == false){
            app.project.rootItem.createBin('Timecode');
        }
        var timecodeBin = findBin('Timecode');
        timecodeFootage = createTransparentVideo(episodeName + '_Timecode', timecodeBin);

        // var time = new Time();
        episodeSequenceObject.insertClip(timecodeFootage, new Time(), 2, 0);
        var timecode_videoTrack = episodeSequenceObject.videoTracks[2];
        var timecode_clip = timecode_videoTrack.clips[0];

        timecode_clip.end = episodeSequenceObject.videoTracks[0].clips[videoTrack.clips.length-1].end;
        addVideoEffect(episodeSequenceObject, timecode_videoTrack, timecode_clip, "Timecode");
        
        var effect;
        for(var l = 0; l < timecode_clip.components.numItems; l++){
            if(timecode_clip.components[l].displayName == "Timecode"){
                var effect = timecode_clip.components[l];
            }
        }

        for(var m = 0; m < effect.properties.numItems; m++){
            var property = effect.properties[m]
            
            if(property.displayName === "Position"){
                var width = episodeSequenceObject.frameSizeHorizontal
                var height = episodeSequenceObject.frameSizeVertical
                property.setValue([((width/2) / width), ((height-50)/height)], 1)
            }

            if(property.displayName === "Size"){
                property.setValue(40, 0)
            }

            // Field Symbol
            if(m === 3){
                // alert(String(property.getValue()))
                property.setValue(false, 0)
            }

            if(property.displayName === "Format"){
                property.setValue(0, 0)
            }

            if(property.displayName === "Timecode Source"){
                property.setValue(0, 0)
            }

            if(property.displayName === "Time Display"){
                if(config.project_settings.fps == "25fps"){
                    property.setValue(1, 0)
                } else {
                    alert('Episode Timecode is not set to the correct framerate.')
                }
            }

            if(property.displayName === "Offset"){
                property.setValue(0, 0)
            }
        }
    }
}

function importSequenceClicked(){
    var episode_padding = episode_prefix_padding[1]
    var sequence_padding = sequence_prefix_padding[1]

    if(episode < 1){
        alert("Episode value too low.\nAn episode value should be " + String(episode_padding) + " digits.");
        return;
    }
    if(episode > Math.pow(10, episode_padding)-1){
        alert("Episode value too high.\nAn episode value should be " + String(episode_padding) + " digits.");
        return;
    }
    if(sequence > Math.pow(10, sequence_padding)-1){
        alert("Sequence value too high.\nA sequence value should be maximum " + String(sequence_padding) + " digits.");
        return;
    }

    var episodeName = getEpisodeName(episode)
    var sequenceName = getSequenceName(sequence)

    var sequenceFolder = new Folder(process_path(config.project_paths.seq_path, {"episode_name": episodeName,
                                                                                 "seq_name": sequenceName}));
    importSequence(sequenceFolder.fsName)
}

function importSequence(currentPath){
    var episodeName = getEpisodeName(episode);
    var sequenceName = getSequenceName(currentPath.substring(currentPath.length - sequence_prefix_padding[1]))
    var sequenceFolder = new Folder(currentPath);
    
    // if(footageExists(episodeName, null) == false){
    //     createSequence(episodeName)
    // }

    if(binExists(sequenceName, null) == false){
        app.project.rootItem.createBin(sequenceName);
    }
    var sequenceBin = findBin(sequenceName, null);

    if(footageExists(sequenceName, null) == false){
        createSequence(sequenceName);
    }
    var sequenceItem = findFootage(sequenceName);
    var sequenceObject = findSequence(sequenceName);

    // Have to add extra tracks
    for(var i = 0; i < 3; ++i){
        addTrack(sequenceObject)
    }
    
    for(var i = 0; i < sequenceObject.audioTracks.length; i++){
        if(i != 0){
            track = sequenceObject.audioTracks[i];
            track.setMute(1)
        }
    }

    var latest_time = new Time();
    var shotFolders = sequenceFolder.getFiles(episodeName + "_" + sequenceName + "_" + shot_prefix_padding[0].replace('_', '') + "*");
    for(var j = 0;j < shotFolders.length;j++){
        var currentPath = shotFolders[j].fsName;
        var currentShot = getShotName(currentPath.slice(currentPath.length - shot_prefix_padding[1]))
        var temp_latest_time = new Time();
        var highestStepAchieved = false

        
        if(importHighestStepOnlyCheck == false || highestStepAchieved == false){
            if(importCompEXRCheck == true){
                var compExrFile = new File(process_path(config.project_paths.shot_comp_output_file, {"episode_name": episodeName,
                                                                                                     "seq_name": sequenceName,
                                                                                                     "shot_name": currentShot}));
                if(compExrFile.exists == true){
                    var compExrName = compExrFile.fsName.split("\\")[compExrFile.fsName.split("\\").length - 1];
                    if(footageExists(compExrName, null) == false){
                        if(binExists('Comp EXR', sequenceBin) == false){
                            var compExrBin = sequenceBin.createBin('Comp EXR');
                        } else {
                            var compExrBin = findBin('Comp EXR', sequenceBin);
                        }
                        var compExrFootage = importFootage(compExrFile.fsName, compExrBin, true);
                        var compExrFootageName = compExrFile.fsName.split('\\')[compExrFile.fsName.split('\\').length-1];
                        var compExrFootageItem = findFootage(compExrFootageName);
                        var videoTrackIndex = 4;
                        var audioTrackIndex = videoTrackIndex + 1;
                        var videoTrack = sequenceObject.videoTracks[videoTrackIndex];
                        var previousClipEnd = new Time();
                        if(videoTrack != null){
                            if(videoTrack.clips.length > 0){
                                var previousClipEnd = videoTrack.clips[videoTrack.clips.length-1].end;
                            }
                        }
                        if(previousClipEnd.ticks < latest_time.ticks){
                            previousClipEnd = latest_time;
                        }
                        sequenceObject.insertClip(compExrFootageItem, previousClipEnd, videoTrackIndex, audioTrackIndex);

                        var videoTrack = sequenceObject.videoTracks[videoTrackIndex];
                        if(videoTrack != null){
                            if(videoTrack.clips.length > 0){
                                var latest_clip = videoTrack.clips[videoTrack.clips.length-1];
                                temp_latest_time = latest_clip.end;
                                scaleFootageToFit(latest_clip, compExrFootageItem, sequenceObject)
                            }
                        }
                        highestStepAchieved = true
                    }
                }
            }
        }


        if(importHighestStepOnlyCheck == false || highestStepAchieved == false){
            if(importCompMovCheck == true){
                var compMovFile = new File(process_path(config.project_paths.shot_comp_output_file_mov, {"episode_name": episodeName,
                                                                                                         "seq_name": sequenceName,
                                                                                                         "shot_name": currentShot}));
                if(compMovFile.exists == true){
                    var compMovName = compMovFile.fsName.split("\\")[compMovFile.fsName.split("\\").length - 1];
                    if(footageExists(compMovName, null) == false){
                        if(binExists('Comp Mov', sequenceBin) == false){
                            var compMovBin = sequenceBin.createBin('Comp Mov');
                        } else {
                            var compMovBin = findBin('Comp Mov', sequenceBin);
                        }
                        importFootage(compMovFile.fsName, compMovBin, false);
                        var compMovFootageName = compMovFile.fsName.split('\\')[compMovFile.fsName.split('\\').length-1];
                        var compMovFootageItem = findFootage(compMovFootageName);
                        var videoTrackIndex = 3;
                        var audioTrackIndex = videoTrackIndex + 1;
                        var videoTrack = sequenceObject.videoTracks[videoTrackIndex];
                        var previousClipEnd = new Time();
                        if(videoTrack != null){
                            if(videoTrack.clips.length > 0){
                                var previousClipEnd = videoTrack.clips[videoTrack.clips.length-1].end;
                            }
                        }
                        if(previousClipEnd.ticks < latest_time.ticks){
                            previousClipEnd = latest_time;
                        }
                        sequenceObject.insertClip(compMovFootageItem, previousClipEnd, videoTrackIndex, audioTrackIndex);

                        var videoTrack = sequenceObject.videoTracks[videoTrackIndex];
                        if(videoTrack != null){
                            if(videoTrack.clips.length > 0){
                                var latest_clip = videoTrack.clips[videoTrack.clips.length-1];
                                temp_latest_time = latest_clip.end;
                                scaleFootageToFit(latest_clip, compMovFootageItem, sequenceObject)
                            }
                        }
                        highestStepAchieved = true
                    }
                }
            }
        }


        if(importHighestStepOnlyCheck == false || highestStepAchieved == false){
            if(importCompPreviewCheck == true){
                var compPreviewFile = new File(process_path(config.project_paths.shot_comp_preview_file, {"episode_name": episodeName,
                                                                                                          "seq_name": sequenceName,
                                                                                                          "shot_name": currentShot}));
                if(compPreviewFile.exists == true){
                    var compPreviewName = compPreviewFile.fsName.split("\\")[compPreviewFile.fsName.split("\\").length - 1];
                    if(footageExists(compPreviewName, null) == false){
                        if(binExists('Comp Preview', sequenceBin) == false){
                            var compPreviewBin = sequenceBin.createBin('Comp Preview');
                        } else {
                            var compPreviewBin = findBin('Comp Preview', sequenceBin);
                        }
                        importFootage(compPreviewFile.fsName, compPreviewBin, false);
                        var compPreviewFootageName = compPreviewFile.fsName.split('\\')[compPreviewFile.fsName.split('\\').length-1];
                        var compPreviewFootageItem = findFootage(compPreviewFootageName);
                        var videoTrackIndex = 2;
                        var audioTrackIndex = videoTrackIndex + 1;
                        var videoTrack = sequenceObject.videoTracks[videoTrackIndex];
                        var previousClipEnd = new Time();
                        if(videoTrack != null){
                            if(videoTrack.clips.length > 0){
                                var previousClipEnd = videoTrack.clips[videoTrack.clips.length-1].end;
                            }
                        }
                        if(previousClipEnd.ticks < latest_time.ticks){
                            previousClipEnd = latest_time;
                        }
                        sequenceObject.insertClip(compPreviewFootageItem, previousClipEnd, videoTrackIndex, audioTrackIndex);

                        var videoTrack = sequenceObject.videoTracks[videoTrackIndex];
                        if(videoTrack != null){
                            if(videoTrack.clips.length > 0){
                                var latest_clip = videoTrack.clips[videoTrack.clips.length-1];
                                temp_latest_time = latest_clip.end;
                                scaleFootageToFit(latest_clip, compPreviewFootageItem, sequenceObject)
                            }
                        }
                        highestStepAchieved = true
                    }
                }
            }
        }


        if(importHighestStepOnlyCheck == false || highestStepAchieved == false){
            if(importFastRenderCheck == true){
                var passesFolder = new Folder(process_path(config.project_paths.shot_2D_passes_folder, {"episode_name": episodeName,
                                                                                                        "seq_name": sequenceName,
                                                                                                        "shot_name": currentShot}));
                var fastRenderFolders = passesFolder.getFiles("Fast*");
                if(fastRenderFolders.length > 0){
                var fastRenderFile = fastRenderFolders[fastRenderFolders.length-1].getFiles("*.exr")[0]
                    if(fastRenderFile.exists == true){
                        var fastRenderName = fastRenderFile.fsName.split("\\")[fastRenderFile.fsName.split("\\").length - 1];
                        if(footageExists(fastRenderName, null) == false){
                            if(binExists('Fast Render', sequenceBin) == false){
                                var fastRenderBin = sequenceBin.createBin('Fast Render');
                            } else {
                                var fastRenderBin = findBin('Fast Render', sequenceBin);
                            }
                            importFootage(fastRenderFile.fsName, fastRenderBin, true);
                            var fastRenderFootageName = fastRenderFile.fsName.split('\\')[fastRenderFile.fsName.split('\\').length-1];
                            var fastRenderFootageItem = findFootage(fastRenderFootageName);
                            var videoTrackIndex = 1;
                            var audioTrackIndex = videoTrackIndex + 1;
                            var videoTrack = sequenceObject.videoTracks[videoTrackIndex];
                            var previousClipEnd = new Time();
                            if(videoTrack != null){
                                if(videoTrack.clips.length > 0){
                                    var previousClipEnd = videoTrack.clips[videoTrack.clips.length-1].end;
                                }
                            }
                            if(previousClipEnd.ticks < latest_time.ticks){
                                previousClipEnd = latest_time;
                            }
                            sequenceObject.insertClip(fastRenderFootageItem, previousClipEnd, videoTrackIndex, audioTrackIndex);

                            var videoTrack = sequenceObject.videoTracks[videoTrackIndex];
                            if(videoTrack != null){
                                if(videoTrack.clips.length > 0){
                                    var latest_clip = videoTrack.clips[videoTrack.clips.length-1];
                                    temp_latest_time = latest_clip.end;
                                    scaleFootageToFit(latest_clip, fastRenderFootageItem, sequenceObject)
                                }
                            }
                            highestStepAchieved = true
                        }
                    }
                }
            }
        }


        if(importHighestStepOnlyCheck == false || highestStepAchieved == false){
            if(importAnimPreviewCheck == true){
                var previewFile = new File(process_path(config.project_paths.shot_anim_preview_file, {"episode_name": episodeName,
                                                                                                      "seq_name": sequenceName,
                                                                                                      "shot_name": currentShot}));
                if(previewFile.exists == true){
                    var previewName = previewFile.fsName.split("\\")[previewFile.fsName.split("\\").length - 1];
                    if(footageExists(previewName, null) == false){
                        if(binExists('Anim Preview', sequenceBin) == false){
                            var previewBin = sequenceBin.createBin('Anim Preview');
                        } else {
                            var previewBin = findBin('Anim Preview', sequenceBin);
                        }
                        importFootage(previewFile.fsName, previewBin, false);
                        
                        var previewFootageName = previewFile.fsName.split('\\')[previewFile.fsName.split('\\').length-1];
                        var previewFootageItem = findFootage(String(previewFootageName));

                        var videoTrackIndex = 0;
                        var audioTrackIndex = videoTrackIndex + 1;
                        var videoTrack = sequenceObject.videoTracks[videoTrackIndex];
                        var previousClipEnd = new Time();
                        if(videoTrack != null){
                            if(videoTrack.clips.length > 0){
                                var previousClipEnd = videoTrack.clips[videoTrack.clips.length-1].end;
                            }
                        }
                        if(previousClipEnd.ticks < latest_time.ticks){
                            previousClipEnd = latest_time;
                        }
                        sequenceObject.insertClip(previewFootageItem, previousClipEnd, videoTrackIndex, audioTrackIndex);

                        var videoTrack = sequenceObject.videoTracks[videoTrackIndex];
                        if(videoTrack != null){
                            if(videoTrack.clips.length > 0){
                                var latest_clip = videoTrack.clips[videoTrack.clips.length-1];
                                temp_latest_time = latest_clip.end;
                                scaleFootageToFit(latest_clip, previewFootageItem, sequenceObject)
                            }
                        }



                        highestStepAchieved = true
                    }
                }
            }
        }


        if(importSoundCheck == true){
            var soundFile = new File(process_path(config.project_paths.shot_sound_file, {"episode_name": episodeName,
                                                                                                "seq_name": sequenceName,
                                                                                                "shot_name": currentShot}))
            if(soundFile.exists == true){
                var soundName = soundFile.fsName.split("\\")[soundFile.fsName.split("\\").length - 1];
                if(fileExists(soundName, null) == false){
                    if(binExists('Audio', sequenceBin) == false){
                        var audioBin = sequenceBin.createBin('Audio');
                    } else {
                        var audioBin = findBin('Audio', sequenceBin);
                    }
                    importFootage(soundFile.fsName, audioBin, false);
                    var soundFootageName = soundFile.fsName.split('\\')[soundFile.fsName.split('\\').length-1];
                    var soundFootageItem = findFootage(soundFootageName);
                    var videoTrackIndex = 0;
                    var audioTrackIndex = 0;
                    var audioTrack = sequenceObject.audioTracks[audioTrackIndex];
                    var previousClipEnd = new Time();
                    if(audioTrack != null){
                        if(audioTrack.clips.length > 0){
                            var previousClipEnd = audioTrack.clips[audioTrack.clips.length-1].end;
                        }
                    }
                    if(previousClipEnd.ticks < latest_time.ticks){
                        previousClipEnd = latest_time;
                    }
                    sequenceObject.insertClip(soundFootageItem, previousClipEnd, videoTrackIndex, audioTrackIndex);

                    var audioTrack = sequenceObject.videoTracks[audioTrackIndex];
                    if(audioTrack != null){
                        if(audioTrack.clips.length > 0){
                            temp_latest_time = audioTrack.clips[audioTrack.clips.length-1].end;
                        }
                    }
                }
            }
        }



        if(temp_latest_time.seconds != latest_time.seconds){
            if(binExists('Nameplates', sequenceBin) == false){
                var nameplateBin = sequenceBin.createBin('Nameplates');
            } else {
                var nameplateBin = findBin('Nameplates', sequenceBin);
            }
            // importFootage(previewFile.fsName, nameplateBin, false);
            nameplate = episodeName + "_" + sequenceName + "_" + currentShot
            var nameplateItem = createTransparentVideo(nameplate, nameplateBin)
            var videoTrackIndex = 5;
            var audioTrackIndex = 0;
            var videoTrack = sequenceObject.videoTracks[videoTrackIndex];
            var previousClipEnd = new Time();
            if(videoTrack != null){
                if(videoTrack.clips.length > 0){
                    var previousClipEnd = videoTrack.clips[videoTrack.clips.length-1].end;
                }
            }

            if(previousClipEnd.ticks < latest_time.ticks){
                previousClipEnd = latest_time;
            }

            // Inserting clip into sequence
            sequenceObject.insertClip(nameplateItem, previousClipEnd, videoTrackIndex, audioTrackIndex);

            // Setting the length of the transparent video
            var videoTrack = sequenceObject.videoTracks[videoTrackIndex];
            if(videoTrack != null){
                if(videoTrack.clips.length > 0){
                    var latest_clip = videoTrack.clips[videoTrack.clips.length-1];
                    latest_clip.end = temp_latest_time

                    if(createShotFrameCountCheck == true){
                        addVideoEffect(sequenceObject, videoTrack, latest_clip, "Timecode");
                        var effect;
                        for(var l = 0; l < latest_clip.components.numItems; l++){
                            if(latest_clip.components[l].displayName == "Timecode"){
                                var effect = latest_clip.components[l];
                            }
                        }

                        for(var m = 0; m < effect.properties.numItems; m++){
                            var property = effect.properties[m]
                            
                            if(property.displayName === "Position"){
                                var width = sequenceObject.frameSizeHorizontal
                                var height = sequenceObject.frameSizeVertical
                                property.setValue([((width - 75) / width), (95/height)], 1)
                            }

                            if(property.displayName === "Size"){
                                property.setValue(30, 0)
                            }

                            // Field Symbol
                            if(m === 3){
                                // alert(String(property.getValue()))
                                property.setValue(false, 0)
                            }

                            if(property.displayName === "Format"){
                                property.setValue(1, 0)
                            }

                            if(property.displayName === "Timecode Source"){
                                property.setValue(0, 0)
                            }

                            if(property.displayName === "Offset"){
                                property.setValue(1, 0)
                            }
                        }
                    }

                    // Add Nameplate
                    if(createShotNameplateCheck == true){
                        addVideoEffect(sequenceObject, videoTrack, latest_clip, "Clip Name");
                        var effect;
                        for(var l = 0; l < latest_clip.components.numItems; l++){
                            if(latest_clip.components[l].displayName == "Clip Name"){
                                var effect = latest_clip.components[l];
                            }
                        }

                        for(var m = 0; m < effect.properties.numItems; m++){
                            var property = effect.properties[m]
                            
                            if(property.displayName === "Position"){
                                var width = sequenceObject.frameSizeHorizontal
                                var height = sequenceObject.frameSizeVertical
                                property.setValue([((width - 10) / width), (35/height)], 1)
                            }

                            if(property.displayName === "Justification"){
                                property.setValue(2, 0)
                            }

                            if(property.displayName === "Size"){
                                property.setValue(30, 0)
                            }
                        }
                    }
                }
            }
        }

        latest_time = temp_latest_time
    }
}

function createSequence(name){
    app.enableQE();
    sq = qe.project.newSequence(name, config.project_paths.premiere_sqpreset.replace("/", "\\"));
    return sq
}

function getEpisodeName(ep){
    var episodeName = episode_prefix_padding[0]
    for(var i=0; i<String(episode_prefix_padding[1]);++i){
        episodeName = episodeName + "0"
    }
    episodeName = episodeName.slice(0, episodeName.length-String(ep).length) + String(ep)
    return episodeName;
}

function getSequenceName(seq){
    var sequenceName = sequence_prefix_padding[0].replace("_", "")
    for(var i=0; i<String(sequence_prefix_padding[1]);++i){
        sequenceName = sequenceName + "0"
    }
    sequenceName = sequenceName.slice(0, sequenceName.length-String(seq).length) + String(seq)
    return sequenceName;
}

function getShotName(sh){
    var shotName = shot_prefix_padding[0].replace("_", "")
    for(var i=0; i<String(shot_prefix_padding[1]);++i){
        shotName = shotName + "0"
    }
    shotName = shotName.slice(0, shotName.length-String(sh).length) + String(sh)
    return shotName;
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

function findFootage(searchName, item){
    if(item == null){
    var item = app.project.rootItem;
    }
    for(var i=0; i < item.children.numItems;i++){
        if(item.children[i].type == ProjectItemType.CLIP){
            if(item.children[i].name == searchName){
                return item.children[i];
            }
        } else {
            if(item.children[i].type == ProjectItemType.BIN){
                result = findFootage(searchName, item.children[i]);
                if(result != null){
                    if(result.name == searchName){
                        return result;
                    }
                }
            }
        }
    }
    return null;
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

function findFile(searchName, item){
    if(item == null){
        var item = app.project.rootItem;
    }
    for(var i=0; i < item.children.numItems;i++){
        if(item.children[i].type == ProjectItemType.FILE){
            if(item.children[i].name == searchName){
                return item.children[i];
            }
        } else {
            if(item.children[i].type == ProjectItemType.BIN){
                result = findFile(searchName, item.children[i]);
                if(result != null){
                    if(result.name == searchName){
                        return result;
                    }
                }
            }
        }
    }
    return null;
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

function findSequence(searchName){
    app.enableQE();

    for(var i = 0; i < app.project.sequences.numSequences;++i){
        if(app.project.sequences[i].name == searchName){
            return app.project.sequences[i]
        }
    }
}

function addTrack(sequenceObject){
    app.project.activeSequence = sequenceObject
    app.enableQE();
    var seq = qe.project.getActiveSequence();
    seq.addTracks()
}

function addVideoEffect(sequenceObject, videoTrack, clip, effect_name){
    app.enableQE();

    for(var i = 0; i < qe.project.numSequences; i++){
        var qeSequence = qe.project.getSequenceAt(i);
        if(qeSequence.name === sequenceObject.name){
            for(var j = 0; j < sequenceObject.videoTracks.length; j++){
                var qeVideoTrack = qeSequence.getVideoTrackAt(j)
                if(qeVideoTrack.name === videoTrack.name){
                    for(var k = 0; k < videoTrack.clips.length; ++k){
                        var qeClip = qeVideoTrack.getItemAt(k)
                        if(qeClip.name === clip.name){
                            qeClip.addVideoEffect(qe.project.getVideoEffectByName(effect_name));
                        }
                    }
                }
            }
        }
    }
}


function scaleFootageToFit(clip, projectItem, sequenceObject){
    var metadata = JSON.parse(projectItem.getProjectColumnsMetadata())
    var videoInfo;
    var width;
    var height;
    var scaleMultiplier;

    for(i in metadata){
        if(metadata[i]['ColumnName'] === "Video Info"){
            videoInfo = metadata[i]['ColumnValue']
        }
    }

    if(videoInfo != null){
        width = parseInt(videoInfo.split(' ')[0])
        height = parseInt(videoInfo.split(' ')[2])
        
        var widthScaleMultiplier = sequenceObject.frameSizeHorizontal/width
        var heightScaleMultipler = sequenceObject.frameSizeVertical/height
        if(widthScaleMultiplier > heightScaleMultipler){
            scaleMultiplier = widthScaleMultiplier;
        } else {
            scaleMultiplier = heightScaleMultipler
        }
    }

    if(scaleMultiplier != null){
        if(scaleMultiplier != 0){
            var effect;

            for(var l = 0; l < clip.components.numItems; l++){
                if(clip.components[l].displayName == "Motion"){
                    var effect = clip.components[l];
                }
            }

            if(effect != null){
                for(var m = 0; m < effect.properties.numItems; m++){
                    var property = effect.properties[m]
                    if(property.displayName === "Scale"){
                        property.setValue(scaleMultiplier * 100, 1)
                    }
                }
            }
        }
    }
}

    // qeClip = qe.project.getActiveSequence().getVideoTrackAt(5).getItemAt(0);
    // qeClip.addVideoEffect(qe.project.getVideoEffectByName(effect_name));

    // for(var i; i < sequenceObject.videoTracks.length; ++i){
        
    // }

function createTransparentVideo(name, bin){
    app.enableQE();
    qe.project.newTransparentVideo(1920, 1080, 0, 1, 1);
    var transparentVideo = findFootage('Transparent Video')
    transparentVideo.name = name
    transparentVideo.moveBin(bin)
    return transparentVideo
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
    return app.project.importFiles(paths, true, bin, isSequence);
}

function decipher_regex(regex){
    var _string = regex.replace('^', '')
    var _items = _string.split('\\')
    var prefix = false
    var padding = false
    for(i in _items){
        if(_items[i][0] == '('){
            if(_items[i][_items[i].length-1] == ')'){
                prefix = _items[i].slice(1, _items[i].length-1).toUpperCase()
            }
        }
        if(_items[i][0] == 'd'){
            if(_items[i][1] == '{'){
                if(_items[i][_items[i].length-1] == '}'){
                    padding = parseInt(_items[i].slice(2, _items[i].length-1))
                }
            }
        }
    }

    return [prefix, padding]
}


function clearProjectItems(){
    app.project.rootItem.createBin('__DELETE__')
    var deleteBin = findBin('__DELETE__')
    while(app.project.rootItem.children.length > 1){
        var i = 0;
        if(app.project.rootItem.children[i] != null){
            if(app.project.rootItem.children[i] === deleteBin){
                i++
            } else {
                app.project.rootItem.children[i].moveBin(deleteBin)
            }
        } else {
            i = 0
        }
    }
    deleteBin.deleteBin()

}

function run(){
    clearProjectItems();
    importEpisodeClicked();
}

run()