
/**
 *  Utilities to import and vectorize images.
 
  * This Library is available through the require function. It implements import bitmap operation. The import can be done in 3 different ways. 
 * As a plain bitmap, as a TVG Bitmap layer or by vectorizing the bitmap.
 
 @example
   // To use the class
   var Utils = require("VectorizeUtils.js");
   
   // There are 2 methods that can be called: importDrawingInNewElementNode and importDrawingInElementNode.
   // the 2 methods take the bitmap filename as argument and an options object.
   
   // This will create a new element for the bitmap
   // It will create the timing in the timeline using the imported bitmap.
   // If the bitmap is a multi-layer (e.g. PSD) it will create one element module per
   // top level group in the PSD document. It will also create an exposure per layer in each
   // of these groups.
   Utils.importDrawingInNewElementNode("c:/myImages/MyBitmap.png", { undoLabel : "Custom Undo/redo label", importType :  Utils.IMPORT_TYPE.TVG_BITMAP});

   // This will import the bitmap in the first selected node
   // It will not change the timing in the timeline
   Utils.importDrawingInElementNode("c:/myImages/MyBitmap.png", { node: selection.selectedNode(0) });
   
   // Here are the general options
   // They are all optional except the elementId or the node.
   var options = { 
	   elementId : 1, node : "",                          // elementId or node must be set to either the elementId to importTo or the Element Module linked to the element to import to.
	   showProgressUI : true,                             // If set to false, will not show progress bar. Useful if doing batch processing
	   noScale : false,                                   // If true, will not scale the bitmap when importing to TVG. Will use the default scaling.
	   importType : Utils.IMPORT_TYPE.TVG_BITMAP          // One of the IMPORT_TYPE enum
	   bitmapAlignment : Utils.ALIGNMENT.VERTICAL_FIT,    // One of the ALIGNMENT enum
	   premultiply : Utils.PREMULTIPLY.STRAIGHT,          // One of the PREMULTIPLY enum                      
	   timing: "",                                        // The timing of the drawing in case of single layer file
	   timingPrefix : "myfile-",                          // The timing prefix to which the layer name will be appended in case of multi layer file
	   forceSingleLayer : false,                          // If true, will for multi-layer bitmap (e.g. PSD) to single layer
	   vectorizeOptions : [ ]                             // The options to pass to the Vectorize function.
    };

	// Here are the importDrawingInNewElementNode options
	// They are all optional. The composite used is determined
	// by the selection if a single composite is selected or the
	// first composite reached from the scene default display.
	// The base element name will be based on the drawing filename
	var newElementOptions = {
		composite : "Top/Composite", 
		baseElementName : "MyDrawing" 
    };
	
    // Here are the options specific to Utils.IMPORT_TYPE.PLAIN_BITMAP import	
	var plainOptions = {
		pixmapType : "PNG",            // The pixmap type of the created element. If omitted the filename extension will be used
		fieldChart : 12               // The field size of the newly created element
    };
	
	 
 
 */
 
    (function()
    {
        /*
         *  Private helper functions
         */
          function computeScaleForAlignment()
          {
             return scene.defaultPixelPerModelUnitForBitmapLayers();
          };
         
        function getUIFile(filename)
        {
          return specialFolders.resource + "/scripts/" + filename;
        }
    
        /*!
         * Progress UI methodes
         */
        function setupProgressUI(options)
        {
          if (!options.showProgressUI)
            return;
            
          if (options.progressUI)
          {
            options.progressUI.level++;
            return;
          }
           
          var uifile = getUIFile("VectorizeUtilsResources/Progress.ui");
          options.progressUI = UiLoader.load(uifile);
          options.progressUI.level = 1;
          options.progressUI.show();  
        }
        
        function setProgress(options, title, v)
        {
          if (!options.showProgressUI)
            return;
            
          if (!options.progressUI)
             return;
          options.progressUI.message.setText(title);
          options.progressUI.progressBar.value = v;
          System.processOneEvent();    
        }
        
        function hideProgress(options)
        {
          if (!options.showProgressUI)
            return;
            
          if (!options.progressUI)
          {
            return;
          }
          options.progressUI.level--;
          if (options.progressUI.level < 1)
          {
            options.progressUI.hide();
            options.progressUI = null;
          }
        }
        
       function fileExists(filename)
       {
        return QFile.exists(filename);
       }
       
       function getElementNameFromFilename(filename)
       {
         if (!filename)
           return "Drawing";
         var p = filename.split("/");
         if (p.length == 0)
            return "Drawing";
         var f = p[p.length-1].split("-");
         if (f.length == 1)
            return f[0].split(".")[0];
         f.pop();   
         return f.join("-");      
       }
       
       function getTimingPrefixFromFilename(filename)
       {
         var p = filename.split("/");
         if (p.length == 0)
            return "1_";
         var f = p[p.length-1].split("-");
         if (f.length == 1)
            return "1_";
         return f[f.length-1].split(".")[0] + "_";   
       }
       
       function getTimingFromFilename(filename)
       {
         var p = filename.split("/");
         if (p.length == 0)
            return "1";
         var f = p[p.length-1].split("-");
         if (f.length == 0)
            return "1";
         return f[f.length-1].split(".")[0];             
       }
       
       function extendObject(obj1, obj2)
       { 
         if (!obj1 || !obj2)
            return;
         for(var i in obj2)
         {
            if (!obj1.hasOwnProperty(i))
              obj1[i] = obj2[i];
          }     
       }
       
       function getConnectedElement(n)
       {
         var col =  node.linkedColumn(n, "DRAWING.ELEMENT");
         return column.getElementIdOfDrawing(col);
       }
       
       function getCompositeToUse() 
       {
        if (selection.numberOfNodesSelected() == 1)
        {
          var n = selection.selectedNode(0);
          if (node.type(n) == "COMPOSITE")
          {
            return n;
          }
          var k = node.numberOfOutputLinks(n, 0);
          for(var i = 0 ; i<k ; ++i)
          {
            var d = node.dstNode(n, 0, i);
            if (node.type(d) == "COMPOSITE")
            {
              return d;
            }
          }
          
        }
        var d = scene.getDefaultDisplay();
        
        var i = 0;
        while (d)
        {
          d = node.flatSrcNode(d, 0);
          if (node.type(d) == "COMPOSITE")
            return d;
          ++i;
          if (i > 1000)
             break;      
        }
        
        var nn = node.subNodes(node.root());
        for(var i in nn)
        {
          if (node.type(nn[i]) == "COMPOSITE")
            return nn[i];    
        }
        
        return null;
       }
       
       function createNewElement(options)
       {
         var elemName = options.baseElementName;
         for(var i=0 ; i<1000 ; ++i)
         {
            var n = elemName;
            if (i)
            {
               n += "_" + i;
            }
            var elemId = element.add(n, "COLOR", options.fieldChart, options.pixmapType, options.vectorType ? "TVG" : "None");       
            if ( elemId != -1 )
            {
              return elemId;
            }
         }
         return -1;     
       }
       
       function createOneElementModule(elemName, compNode, elementId)
       {
         var yPos = 100;
         var xPos = 0;
         var vnode = node.add(node.parentNode(compNode), elemName, "READ", xPos, yPos, 0);
    
         column.add(vnode, "DRAWING");          
         column.setElementIdOfDrawing( vnode, elementId );
         node.linkAttr(vnode, "DRAWING.ELEMENT", vnode);
         node.link(vnode, 0 , compNode, 0);
         return vnode;
       }
        
       function createElementNodes(options)
       {
          var created = {};
          var elementId = createNewElement(options);
          if (elementId == -1)
            throw("Could not create element");
            
          options.elementId = elementId;
          
          if (options.layers)
          {
            for(var i in options.layers)
            {
              var layer = options.layers[i];
              if (!layer.visible)
                 continue;
              var comp = layer.layer.split(":");  
              var g;
              g = comp.length == 1 ? "" : ("_" + comp[0]);
              var elemName = options.baseElementName + g;
              if (created.hasOwnProperty(elemName))
                continue;
              var n = createOneElementModule(elemName, options.composite, elementId);
              created[elemName] = n;  
            }
          }
          else
          {
              var n = createOneElementModule(options.baseElementName, options.composite, elementId);      
              created[options.baseElementName] = n;  
          }
          
          for(var i in created)
          {
            var elem = created[i];
            var mode = "Vector";
            if (options.importType == VectorizeUtils.IMPORT_TYPE.TVG_BITMAP)
            {
              mode = "Bitmap";
            }
            node.setTextAttr(elem, "overlayArtDrawingMode", 1, mode);
            node.setTextAttr(elem, "lineArtDrawingMode", 1, mode);
            node.setTextAttr(elem, "colorArtDrawingMode", 1, mode);
            node.setTextAttr(elem, "underlayArtDrawingMode", 1, mode);
            if (options.importType == VectorizeUtils.IMPORT_TYPE.PLAIN_BITMAP && options.bitmapAlignment.hasOwnProperty("value"))
            {
              MessageLog.trace("SETTING ALIGNMENT " + options.bitmapAlignment.value);
              node.setTextAttr(elem, "ALIGNMENT_RULE", 1, options.bitmapAlignment.value);
              if (options.hasOwnProperty("moduleScale"))
              {
                MessageLog.trace("SET SCALE: " + options.moduleScale);
                node.setTextAttr(elem, "SCALE.X", 1, options.moduleScale);
                node.setTextAttr(elem, "SCALE.Y", 1, options.moduleScale);
              }
              node.setTextAttr(elem, "APPLY_MATTE_TO_COLOR", 1, options.premultiply.plainBitmapValue);
            }
          }
          return created;
       }
       
       function importPlainBitmapInNewElementNode(filename, options)
       {
         scene.beginUndoRedoAccum(options.undoLabel ? options.undoLabel : "Import Plain Bitmap in New Element Module");
          setupProgressUI(options);
          setProgress(options, "Importing Bitmap", 0);
          var s = filename.split(".");
          var extension = s[s.length-1].toUpperCase();
          try
          {            
            extendObject(options, { bitmapAlignment : VectorizeUtils.ALIGNMENT.FIT, pixmapType : extension, vectorType :0, fieldChart : scene.numberOfUnitsZ(), composite : getCompositeToUse(), baseElementName : getElementNameFromFilename(filename) } );
            options.layers = options.forceSingleLayer ? null : CELIO.getLayerInformation(filename);
            if (options.bitmapAlignment == VectorizeUtils.ALIGNMENT.PROJECT_RESOLUTION)
            {
              var scale = getImportItemScaleFactors(filename);
              options.moduleScale = scale.scaleY;
            }
            
            if (options.composite == null)
            { 
               reportInvalidComposite();
               return false;
            }
            MessageLog.trace("Importing in " + options.baseElementName);
            var elemMap = createElementNodes(options);
            
            var dlist = column.getDrawingColumnList();
            var addedTiming = importPlainBitmapInElement(filename, options);
            
            var exposureCount = {};
            if (addedTiming) {
               setProgress(options, "Importing Bitmap", 25);
               
              if (options.layers)
              {
                for(var i in options.layers)
                {
                  var layer = options.layers[i];
                  if (!layer.visible)
                    continue;
                  var comp = layer.layer.split(":");  
                  var g;
                  g = comp.length == 1 ? "" : ("_" + comp[0]);
                  var elemName = options.baseElementName + g;
                  if (elemMap.hasOwnProperty(elemName))
                  {
                     var n = elemMap[elemName];
                     if (!exposureCount.hasOwnProperty(n))
                      exposureCount[n] = 0;
                     var f = ++exposureCount[n]; 
                     var newTiming = addedTiming + ":" + layer.layer;
                     var rr = column.setEntry(n, 1, f, newTiming);
                  }
                }
              }
              else
              {
                for(var f = 1; f <= frame.numberOf() ; ++f)
                  column.setEntry(elemMap[options.baseElementName], 1, f, addedTiming);
              }
            }
            hideProgress(options);
           }
           catch(e)
           {
             MessageLog.trace("Exception" + e);
             scene.cancelUndoRedoAccum();
             hideProgress(options);
             return;
           }
          scene.endUndoRedoAccum ();   
       }
       
       function reportInvalidComposite()
       {
         MessageLog.error("Cannot find a suitable composite to connect the element to.");
       } 
       function importPlainBitmapInElement(filename, options)
       {
        var elemId = options.elementId || getConnectedElement(options.node);        
        if (elemId == -1)
          return false;
        if (element.vectorType(elemId) != 0)
        {
           MessageLog.error("Trying to import a plain bitmap in a Vector Element.");
           return false;
        }    
        var destinationType = element.pixmapFormat(elemId);
        var s = filename.split(".");
        var extension = s[s.length-1].toUpperCase();
    
        var timing = options.timing ? options.timing : false;
        try
        {
          scene.beginUndoRedoAccum(options.undoLabel ? options.undoLabel : "Import Drawing in New Element Module");
    
          setupProgressUI(options);
          setProgress(options, "Importing Bitmap", 0);
          
          MessageLog.trace("Importing to " + destinationType + " from " + extension);
          if (!timing)
          {
            for(var i=1 ;  i< 1000 ; ++i)
            {
              if (!Drawing.isExists(elemId, i))
              {
                if (Drawing.create(elemId, i, true))
                {
                  timing = i;
                  break;
                }
              }
            }
          }
          else
          {
              if (!Drawing.isExists(elemId, timing))
              {
                if (!Drawing.create(elemId, timing, true))
                {
                  timing = false;
                }
              } 
          }
          if (timing)
          {
            var destinationFile = Drawing.filename(elemId, timing);
            if (extension == destinationType)
            {
               // Plain copy...
               QFile.copy(filename, destinationFile);
            }
            else
            {
              // use UTransform to convert to proper type...
              var r = CELIO.getInformation(filename);
              Utransform("-outformat", destinationType, "-resolution", r.width, r.height, "-outfile", destinationFile, filename);
            }
          }
          hideProgress(options);
          scene.endUndoRedoAccum();
        }
        catch(e)
        {
           MessageLog.trace("Exception" + e);
           scene.cancelUndoRedoAccum();
           hideProgress(options);
           return;    
        }
        return timing;
       }
          function getImportItemScaleFactors(imageFilename)
          {
             var r = CELIO.getInformation(imageFilename);
             if (!r)
             {
               return { scaleX : 1, scaleY : 1 };
             }
             var resX = scene.defaultResolutionX() * 1.0;
             var resY = scene.defaultResolutionY() * 1.0;
             return {
                scaleX : r.width / resX,
                scaleY : r.height / resY
             };
          };
       
      var VectorizeUtils = {
         /**
           * One of these values can be passed to the bitmapAlignment option.  They 
           * give the same result as their equivalent in the Import Bitmap dialog of the Application.
           * @namespace
           * @property {Object} HORIZONTAL_FIT - For TVG Bitmap import
           * @property {Object} VERTICAL_FIT - For TVG Bitmap import
           * @property {Object} ACTUAL_SIZE - For TVG Bitmap import
           * @property {Object} FIT - For Plain Bitmap import
           * @property {Object} PAN - For Plain Bitmap import
           * @property {Object} PROJECT_RESOLUTION - For Plain Bitmap import
          */
         ALIGNMENT : {
           HORIZONTAL_FIT : { tvg_bitmap : true},
           VERTICAL_FIT : {tvg_bitmap : true},
           ACTUAL_SIZE : {tvg_bitmap : true},
           FIT : { tvg_bitmap : false, value : "CENTER_FIT"},
           PAN : {tvg_bitmap : false, value : "CENTER_FIRST_PAGE"},
           PROJECT_RESOLUTION : {tvg_bitmap : false, value : "ASIS"}
         },
         
         /**
          *  One of these values can be passed in the premultiply option
             *  @namespace
                *  @property {Object} STRAIGHT - Import the color as is. i.e. Consider the pixels as premultiplied by alpha.
                *  @property {Object} WHITE   - Consider the pixels as premultiplied on white.
                *  @property {Object} BLACK   - Consider the pixels as premultiplied on black.
                *  @property {Object} CLAMP    - Same as straight but clamp the channel values to the alpha
           */
         PREMULTIPLY : {
            STRAIGHT : { value : "straight", plainBitmapValue : "Y" },
            WHITE : { value : "white", plainBitmapValue : "W" },
            BLACK : { value : "black", plainBitmapValue : "N" },
            CLAMP : { value : "straight", plainBitmapValue : "M" }
         },
         /**
           *  One of these values can be passed in the importType option
              * @namespace
                *  @property {Object} TVG_BITMAP - Import the bitmap in a bitmap TVG layer.
                *  @property {Object} TVG_VECTOR   - Import and vectorize ithe bitmap in a vector TVG.
                *  @property {Object} PLAIN_BITMAP   - Import the bitmap as a plain bitmap.
           */
         IMPORT_TYPE : {
            TVG_BITMAP : {},
            TVG_VECTOR : {},
            PLAIN_BITMAP : {}
         },
          /**
           *  Will import the drawing in filename in new element node(s). Many nodes might 
           *  get created if the input file is a multi-layer file like PSD with proper grouping.
           *  @param {String} filename The bitmap filename.
           *  @param {Object} options A javascript object containing the list of import options.
           */
          importDrawingInNewElementNode : function(filename, options)
          {
            if (!options)
                options = {};
    
            extendObject(options, { importType : VectorizeUtils.IMPORT_TYPE.TVG_BITMAP, premultiply : VectorizeUtils.PREMULTIPLY.STRAIGHT } );
                
            if (options.importType && options.importType == VectorizeUtils.IMPORT_TYPE.PLAIN_BITMAP)
            {
              importPlainBitmapInNewElementNode(filename, options);
              return;
            }
            
            var shortFile = filename.split("/");  
            shortFile = shortFile[shortFile.length-1];
            
            scene.beginUndoRedoAccum(options.undoLabel ? options.undoLabel : "Import Drawing in New Element Module");
            setupProgressUI(options);
            setProgress(options, shortFile, 0);
            try
            {            
              extendObject(options, { fieldChart : scene.numberOfUnitsZ(), vectorType: 1, pixmapType: "PNG", importType : VectorizeUtils.IMPORT_TYPE.TVG_BITMAP, composite : getCompositeToUse(), baseElementName : getElementNameFromFilename(filename) } );
              options.layers = options.forceSingleLayer ? null : CELIO.getLayerInformation(filename);
              options.extension = "TVG";
              if (options.composite == null)
              { 
                reportInvalidComposite();
                return false;
              }
              MessageLog.trace("Importing in " + options.baseElementName);
              var elemMap = createElementNodes(options);
              var addedTiming = VectorizeUtils.importDrawingInElementNode(filename, options);
              var exposureCount = {};
              MessageLog.trace("Bitmap have been imported: " + JSON.stringify(addedTiming) + " " + JSON.stringify(options.layers));
              if (addedTiming) {
                for(var i=0 ; i < addedTiming.length ; ++i)
                {
                   var timing = addedTiming[i].timing;
                   if (options.layers)
                   {
                     var layer = addedTiming[i].layer;
                     
                     var g = layer.split(":");
                     if (g.length == 0) // means something is very wrong should not happen
                       continue;
                     
                     var n = options.baseElementName;
                     if (g.length > 1)
                     {
                         n += "_" + g[0];
                     }
                     if (!exposureCount.hasOwnProperty(n))
                      exposureCount[n] = 0;
                     var f = ++exposureCount[n]; 
                     column.setEntry(elemMap[n], 1, f, timing);
                   }
                   else
                   {
                    for(var f = 1; f <= frame.numberOf() ; ++f)
                      column.setEntry(elemMap[options.baseElementName], 1, f, timing);
                   }
                }
              }
              hideProgress(options);
             }
             catch(e)
             {
               MessageLog.trace("Exception" + e);
               scene.cancelUndoRedoAccum();
               hideProgress(options);
               return;
             }
            scene.endUndoRedoAccum ();

            return options
          },
          /**
           *  Will import the drawing in filename in existing element node(s) based on the options.  
           *  options:
           *  @param {String} filename The bitmap filename.
           *  @param {Object} options A javascript object containing the list of import options.
           */
          importDrawingInElementNode : function(filename, options)
          {
            try
            {
              if (!options)
              {
                options = {};
              }
              
              if (!filename || !options || (!options.node && !options.elementId))
                return false;
    
              extendObject(options, { importType : VectorizeUtils.IMPORT_TYPE.TVG_BITMAP } );
              
              if (options.importType == VectorizeUtils.IMPORT_TYPE.PLAIN_BITMAP)
              {
                return importPlainBitmapInElement(filename, options);
              }
    
                extendObject(options, { elementId : false, 
                            showProgressUI : true,
                            noScale : false,
                            bitmapAlignment : VectorizeUtils.ALIGNMENT.VERTICAL_FIT,    
                            premultiply : VectorizeUtils.PREMULTIPLY.STRAIGHT,                       
                            timing: getTimingFromFilename(filename), // The timing of the drawing in case of single layer file
                            timingPrefix : getTimingPrefixFromFilename(filename), // The timing prefix to which the layer name will be appended in case of multi layer file
                            vectorizeOptions : [ ] 
                          } );
    
              scene.beginUndoRedoAccum(options.undoLabel ? options.undoLabel : "Import and Vectorize Drawing in Element Module");
                
              var shortFile = filename.split("/");  
              shortFile = shortFile[shortFile.length-1];
        
              var addedTiming = [];
                        
              var additionalVectorizeOptions = [];
              if (options.importType == VectorizeUtils.IMPORT_TYPE.TVG_BITMAP)
              {
                additionalVectorizeOptions.push("-asBitmap");            
                additionalVectorizeOptions.push("-no_color_art");
              }
       
              setupProgressUI(options);
                 
              var elemId = options.elementId || getConnectedElement(options.node);        
              if (elemId != -1)
              {
                // The input is always a file
                var inputDesc = { "filename" : filename };
                var bitmapResolutionScaleFactor = 1.0;
                var pixelPerModelUnit = computeScaleForAlignment();
                var resolutionScaling = { scaleX : 1, scaleY  :1};
                if (!options.noScale)
                {
                  resolutionScaling = getImportItemScaleFactors(filename);
                }
                if (options.importType == VectorizeUtils.IMPORT_TYPE.TVG_BITMAP)
                {
                  if (options.bitmapAlignment == VectorizeUtils.ALIGNMENT.VERTICAL_FIT)
                  {
                    bitmapResolutionScaleFactor = resolutionScaling.scaleY;              
                  }
                  else if (options.bitmapAlignment == VectorizeUtils.ALIGNMENT.HORIZONTAL_FIT)
                  {
                    bitmapResolutionScaleFactor = resolutionScaling.scaleX;
                  }
                }
                additionalVectorizeOptions.push("-pixelPerModelUnit");
                additionalVectorizeOptions.push(bitmapResolutionScaleFactor * pixelPerModelUnit);
                additionalVectorizeOptions.push("-premultiply");
                additionalVectorizeOptions.push(options.premultiply.value);
                
                var layers = options.layers || (options.forceSingleLayer ? null : CELIO.getLayerInformation(filename));
                
                if (layers)
                {
                  for(var i in layers)
                  {
                    var layer = layers[i];
                    if (!layer.visible)
                      continue;
                      
                     setProgress(options,  shortFile + " -> " + layer.layer, i / layers.length * 100.0);
      
                    var g = layer.layer.split(":");
                    var timing = options.timingPrefix + g.join("_");
    
                    // Create the timing
                    if (!Drawing.isExists(elemId, timing))
                    {
                      Drawing.create(elemId, timing, true);
                      addedTiming.push({ layer : layer.layer, timing : timing});
                    }
                    var destinationFile = Drawing.filename(elemId, timing);
                    var dk = Drawing.Key(elemId, timing);
                    
                    // If file does not exist yet, use directly the filename
                    if (!fileExists(destinationFile))
                    {
                      dk = { filename : destinationFile };
                    }
                                                   
                    res = DrawingTools.vectorize(inputDesc, dk, options.vectorizeOptions.join(" "), additionalVectorizeOptions.join(" "), "-layer", layer.layer );
                  }
                }
                else
                {
                    var timing = options.timing;
                    if (!Drawing.isExists(elemId, timing))
                    {
                      Drawing.create(elemId, timing, true);
                      addedTiming.push({ timing : timing});
                    }
                    var destinationFile = Drawing.filename(elemId, timing);
                    var dk = Drawing.Key(elemId, timing);
                    
                    // If file does not exist yet, use directly the filename
                    if (!fileExists(destinationFile))
                    {
                      dk = { filename : destinationFile };
                    }
    
                    setProgress(options, shortFile, 0);
                    res = DrawingTools.vectorize(inputDesc, dk, options.vectorizeOptions.join(" "), additionalVectorizeOptions.join(" ") );
                }
              }
              hideProgress(options);
              scene.endUndoRedoAccum();
            }
            catch(e)
            {
               MessageLog.trace("Exception" + e);
               scene.cancelUndoRedoAccum();
               return [];
            }
            return addedTiming;
          }
      };
      for(var i in VectorizeUtils)
        exports[i] = VectorizeUtils[i];
    })();
    
      
      
      
    