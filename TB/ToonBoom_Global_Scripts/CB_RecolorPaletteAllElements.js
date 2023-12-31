
 /*
  * This is a dialog for remapping colors and recoloring drawings. 
  * It can be used to remap the colors in a palette to those of another palette, associating them by index
  * Added a line that selects everything in scene, so the changes are "scene global" instead of only on selected layers. -UPDATED- Removed that line again.
  *
  * The Recoloring is applied to all drawings of each selected element. 
  * The mapping generated can be saved to file, in json format. You could write it yourself, or join two together.
  * The colornames are for informative and validation purpose, only the color ids (from: and to: fields) are necessary
  * 
  */


function RecolorDrawingsDialog(ui)
{
  this.ui = ui;
  this.show = ui.show;
  
  this.srcPalette = null;
  this.destPalette = null;
  this.mapping = null;

  this.updateTextEdit = function ()
  {
    var str =  JSON.stringify(this.mapping);
    this.ui.mapTextEdit.setText(str);
  }
    
  var validate = function (obj)
  {
      if(typeof(obj) == typeof([]))
      {
        return true;
      }
      return false;
  }
  this.updateMapping = function()
  {
    try
    {
      obj = JSON.parse(this.ui.mapTextEdit.plainText);
      if(!validate(obj))
      {
        throw "Not an Array" ;
      }
      this.mapping = obj;
      return true;
    }
    catch(err)
    {
      MessageBox.information("Error while parsing the edited mapping");
      return false;
    }
  }
  
  
  // Button Actions

  var getSrcAction = function ()
  {
    this.srcPalette = PaletteObjectManager.getPalette(PaletteManager.getCurrentPaletteId());
    this.ui.srcPaletteName.setText(this.srcPalette.getName());
  }
  
  var getDstAction = function ()
  {
    this.destPalette = PaletteObjectManager.getPalette(PaletteManager.getCurrentPaletteId());
    this.ui.destPaletteName.setText(this.destPalette.getName());
  }

  
  
  var createMappingAction = function ()
  {
    var size = Math.min(this.srcPalette.nColors, this.destPalette.nColors);

    this.mapping = [];
    for(var i = 0 ; i < size ;  i++)
    {
      var color1 = this.srcPalette.getColorByIndex(i);
      var color2 = this.destPalette.getColorByIndex(i);

      if(color1.isValid && color2.isValid)
      {
        this.mapping.push(  {  firstColorName: color1.name, secondColorName: color2.name, from: color1.id, to: color2.id }  );
      }
    }
    this.updateTextEdit();
  }
  
  
  var searchSubNodes = function(nodeName, allNodes)
  {
    var nSubNodes = node.numberOfSubNodes(nodeName);
    if(nSubNodes!=0)
    {
      for(var subNodeIndex = 0; subNodeIndex < nSubNodes; subNodeIndex++)
      {
        var curSubNode = node.subNode(nodeName,subNodeIndex);
        if(node.type(curSubNode)=='READ')
        {
          allNodes[curSubNode] = curSubNode;
        }
        searchSubNodes(curSubNode,allNodes);
      }
    }
  }

  var applyToSelectionAction = function ()
  {
    if(!this.updateMapping())
    {
      return;
    }
    //selection.selectAll();
    var selectedNodes = selection.selectedNodes();
	MessageLog.trace(selectedNodes);
    var allNodes = {};
    for(var i = 0 ;  i < selectedNodes.length ; i++)
    {
      if(node.type(selectedNodes[i])=='READ')
      {       
        allNodes[selectedNodes[i]] = selectedNodes[i];
      }
      searchSubNodes(selectedNodes[i],allNodes);      
    }
    
    
    var drawingCount = 0;
    var showProgressDlg = false;
    var progressDlg; 
    for(var nodeIt in allNodes)
    {
      if(allNodes.hasOwnProperty(nodeIt))
      {
        var ElementId = node.getElementId(allNodes[nodeIt]);
        drawingCount += Drawing.numberOf(ElementId);
      }
    }
    
    var labelString = "Recolouring: ";
    if(drawingCount > 50 )
    {
      showProgressDlg = true;
      progressDlg =new QProgressDialog();
      progressDlg.modal = true;
      progressDlg.open();
    }
    try
    {
      scene.beginUndoRedoAccum("Recolor Drawings");
      var count =0;
      for(var nodeIt in allNodes)
      {
        if(allNodes.hasOwnProperty(nodeIt))
        {
          var layerName = node.getTextAttr(allNodes[nodeIt], 1, "drawing.element.layer");
          var ElementId = node.getElementId(allNodes[nodeIt]);
          for(var j = 0 ; j < Drawing.numberOf(ElementId); j++  )
          {
            var drawingId = Drawing.name(ElementId,j);
            if(showProgressDlg)
            {
              if(progressDlg.wasCanceled)
              {
                throw "Canceled";
              }
              count+=1;
              progressDlg.setLabelText(labelString + element.getNameById(ElementId) + " - " + drawingId);
              progressDlg.setValue(100 * count/drawingCount);
            }

            DrawingTools.recolorDrawing({ elementId : ElementId,  layer : layerName, exposure : drawingId },this.mapping);
          }
        }

      }
      
      if(showProgressDlg)
      {
        progressDlg.hide();
      }
      scene.endUndoRedoAccum();
    }
    catch(err)
    {
      if(err=="Canceled")
      {
        MessageBox.information("Canceling Redraw...");
      }
      else
      {
        MessageBox.information("Error " + err +" while Recoloring Drawings, canceling...");
      }
      
      if(showProgressDlg)
      {
        progressDlg.hide();
      }
      // We should probably cancel the operation ?
      scene.cancelUndoRedoAccum();
    }
  }

  
  var saveMappingAction = function ()
  {
    if(!this.updateMapping()||this.ui.mapTextEdit.plainText.length==0)
    {
      return;
    }
    var path = FileDialog.getSaveFileName("*.json", "Save Mapping File...");
    if(path  === undefined)
    {
       return false;
     }
    var file = new File( path );
    try
    {
      file.open( 2 );
      file.write( JSON.stringify(this.mapping) );
      file.close();
    }
    catch(err)
    {
      MessageBox.information("Error while saving file as JSON");
    }
  }
  
  var loadMappingAction = function()
  {
    var path = FileDialog.getOpenFileName("*.json", "Load MappingFile");
    if(path  === undefined)
    {
       return false;
     }
    var file = new File( path );
    try
    {
      file.open( 1 );
      var content = file.read(  );
      file.close();
      obj = JSON.parse(content);
      if(validate(obj))
      {
        this.mapping = obj;
        this.updateTextEdit();
      }
    }
    catch(err)
    {
      MessageBox.information("Error while loading Mapping file");
    }
    
  }  

  this.ui.getSrcButton.clicked.connect(this, getSrcAction);
  this.ui.getDestButton.clicked.connect(this, getDstAction);
  this.ui.createMappingButton.clicked.connect(this, createMappingAction);
  this.ui.applyToSelectionButton.clicked.connect(this, applyToSelectionAction);
  this.ui.saveButton.clicked.connect(this, saveMappingAction);
  this.ui.loadButton.clicked.connect(this, loadMappingAction);
  this.ui.discardChangesButton.clicked.connect(this, this.updateTextEdit);
  
}


function TB_RecolorDrawings()
{
  var scriptFolder = specialFolders.resource+ "/scripts";
  var uiPath = scriptFolder + "/TB_RecolorDrawings.ui";
  var uiTemplate = UiLoader.load(uiPath, scriptFolder);
  var ui = new RecolorDrawingsDialog(uiTemplate);

  ui.show();
}
