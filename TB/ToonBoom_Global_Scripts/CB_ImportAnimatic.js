function importMovie(prefix,movie)
            {
        
                //add Composite and Display nodes
                //Find safeframe drawing
                var safe_frame = column.getName(0);
                
                
                // add element
                
                var elementId  = element.add( prefix , "COLOR", 12, "PNG", 0 );
        
                tempFolder = scene.tempProjectPathRemapped () + "/movImport/" + prefix
        
                MessageLog.trace ("Real Path : " + tempFolder);
                MovieImport.setMovieFilename( movie );
                MovieImport.setImageFolder( tempFolder );
                MovieImport.setImagePrefix(  prefix  );
                MovieImport.setAudioFile(tempFolder + "/" + prefix + ".wav");
             
                
                MessageLog.trace ( "TempFolder: " + tempFolder + " ImagePrefix: " + prefix);
                
                if( MovieImport.doImport() )
                {
                    MessageLog.trace( "Import ok : "  + MovieImport.numberOfImages() + " frames " );
                    MessageLog.trace( "Folder temp images: " + tempFolder );
                }
                else
                {
                    MessageLog.trace("import failed" );
                    return;
                }
                for (var i = 1; i <= MovieImport.numberOfImages(); i++ ) 
                {
                    Drawing.create(elementId,i,true);
                    var dstFilePath = Drawing.filename(elementId, i);
                    var dstFile = new PermanentFile(dstFilePath);
        
                    var srcFilePath = tempFolder + "/" + prefix + "-" + i.toString() + ".png";
                    
                    var srcFile = new PermanentFile( srcFilePath );
                    if (srcFile.exists()) {
                        MessageLog.trace("Copy: " + srcFile.path() + " --> " + dstFile.path());
                        var result = srcFile.copy( dstFile );
                        MessageLog.trace("Result: " + result);
                        if (dstFile.exists()) {
                            srcFile.remove();
                        } else {
                            MessageLog.trace("ERROR: file was not copied to destination (" + dstFile.path() + ")");
                        }
                    } else {
                        MessageLog.trace("ERROR: source file does not exist (" + srcFile.path() + ")");
                    }
                    
                } 
        
                var columnName  = prefix;
                var v = column.add( columnName, "DRAWING" );
                if( v == false )
                {
                    var i = 1;
                    while( v == false && i < 100 )
                    {
                        columnName = prefix +"_" + i;
                        v = column.add( columnName, "DRAWING" );
                        i = i +1;
                    }
        
                    if( i >= 100 )
                    {
                        MessageBox.critical( "reached 100");
                        return;
                    }
                }
        
                // associate the element with the column
                column.setElementIdOfDrawing( columnName, elementId );
        
        
                // Adds frames to the scene
                var numOfImages = MovieImport.numberOfImages() ;
                var oldNumFrames = frame.numberOf();
                frame.insert(0, numOfImages - oldNumFrames );
        
        
                // fill exposure
                var n = numOfImages;
                
                column.setEntry(safe_frame,1,1,1);
                column.fillEmptyCels(safe_frame,1,n);
                while( n > 0 )
                {
                    column.setEntry( columnName, 1, n, n );
                    n = n -1;
                }
                scene.setStopFrame(n-1);
                frame.remove(n-1,1);
                
                // create Basic Nodes: Composite, Display, Camera, Camera-Peg
                var yPos = -50;
                
                // original: var compNode  = node.add(node.root(),"Composite" , "COMPOSITE", 0, yPos+50, 0);
                var compNode = node.subNodeByName("Top","SCENE_Composite");		
                //var dispNode  = node.add(node.root(),"Display" , "DISPLAY", 50, yPos+100, 0);
                //var camNode = node.add(node.root(),"Camera" , "CAMERA", -150, yPos+50, 0);
                //var pegNode = node.add(node.root(),"Camera-Peg" , "PEG", -150, yPos-50, 0);
        
                // create READ
                
                var alignmentRule = "CENTER_TB";
                
                var readNode = node.add( node.root(), columnName,  "READ", 0,yPos-50,0);
                
                node.linkAttr( readNode, "DRAWING.ELEMENT", columnName );
                node.setTextAttr( readNode, "alignmentRule",1,alignmentRule );
                node.setTextAttr( readNode, "applyMatteToColor",1,"Y");
                node.setTextAttr( readNode, "scale.x",1,"1");
                node.setTextAttr( readNode, "scale.y",1,"1");
                
                // set the camera 12 field front
                //node.setTextAttr( camNode, "offset.z",1,"12" );
                        
                //Link Nodes
                //node.link(compNode,0,dispNode,0);
                node.link(readNode,0,compNode,0);
                //node.link(pegNode,0,camNode,0);
                var safe_frame_node = node.subNodeByName("Top","SafeFrame");
                //node.link(pegNode,0,safe_frame_node,0);
        
                //Create Sound Column
                if ( MovieImport.isAudioFileCreated() )
                {
                    MessageLog.trace("audio created");
                    var soundName = columnName + "_sound";
                    column.add( soundName, "SOUND");
                    column.importSound( soundName, 1, tempFolder + "/" + prefix + ".wav");
                }
                
                //MessageBox.information("Process Completed" );
                MessageLog.trace("Process Completed" );
            }

function ImportAnimatic(){
	var scene_path = scene.currentProjectPath();
	var scene_path_split =scene_path.split("/");
	scene_path_split.pop();


	var cur_scene = scene.currentVersionName();
	if(cur_scene.indexOf("_V")!= -1){
		shot = cur_scene.split("_V")[0];
	}else{
		shot = cur_scene;
	}
	animatic_path = scene_path_split.join("/") + "/" +shot + "_Animatic.mov";
	animatic_path_mp4 = scene_path_split.join("/") + "/" +shot + "_Animatic.mp4";
	animatic_path_file = new PermanentFile(animatic_path);
	animatic_path_mp4_file = new PermanentFile(animatic_path_mp4);
	MessageLog.trace("Animatic Path: " + animatic_path );
	if(animatic_path_file.exists()==true){
		MessageLog.trace("Found animatic: " + animatic_path );
		importMovie("new_animatic", animatic_path);
		
	}
	if(animatic_path_mp4_file.exists()==true){
		MessageLog.trace("Found animatic: " + animatic_path );
		importMovie("new_animatic", animatic_path_mp4);
	}
}
function ImportSoundTest(){
	path = "P:/930499_Borste_02/Production/Temp/SoundTest/S202_SQ010_SH170_Animatic.mp4";
	importMovie("mp4",path)
}


