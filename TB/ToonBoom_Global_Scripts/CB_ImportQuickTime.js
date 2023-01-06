function importQTmovie()
        {
            function setSceneDefaults(resX,resY,fov,fps,defResoulutionName)
            {    
                scene.setDefaultResolution(resX,resY,fov);
                scene.setFrameRate(fps);    
                scene.setDefaultResolutionName(defResoulutionName);
            }
            function SaveBaseAsNewScene(){
            save_path = "P:/930483_Borste_film/Production//Film/S101/S101_SQ010/S101_SQ010_SH040/S101_SQ010_SH040"; //"C:/Temp/Sprinter_Project_Structure/Film/E01/sh010/sh010.xstage";
            scene.saveAs(save_path);
            MessageLog.trace("SAVING: " + save_path);
            }
        
        
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
                node.setTextAttr( readNode, "scale.x",1,"0.9");
                node.setTextAttr( readNode, "scale.y",1,"0.9");
                
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
        
            // Default parameters for the scene
            /*
            var resX = 2112;
            var resY = 1188;
            var fov = 31.417;
            var fps = 25;
            var defResoulutionName = "custom";
            //var defResoulutionName = "HDTV";
            */
            var resX = 3840;
            var resY = 2160;
            var fov = 41.112;
            var fps = 25;
            var defResoulutionName = "custom";
        
            SaveBaseAsNewScene();
            var movie = "P:/930483_Borste_film/Production//Film/S101/S101_SQ010/S101_SQ010_SH040/S101_SQ010_SH040_Animatic.mov"//"C:/Temp/Sprinter_Project_Structure/Film/E01/_Preview/sh010.mov";
            setSceneDefaults(resX,resY,fov,fps,defResoulutionName);
            scene.saveAll();
            importMovie("animatic",movie);
            scene.saveAll();
        
        }