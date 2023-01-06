//CF_CopyPastePivots v.1.0.1 by www.cartoonflow.com 
//CARTOONFLOW - October 2017

function __execDialog(uiPath)
{  
  var pivotAttributes = [undefined,undefined,undefined,undefined, undefined];
  this.copyPivot = function()
  {    
      pivotAttributes[0] = undefined;
      pivotAttributes[1] = undefined;
      pivotAttributes[2] = undefined;
      pivotAttributes[3] = undefined;
      pivotAttributes[4] = 'pivot';
      var n=selection.selectedNode(0);
      var nodeName = n.slice(n.indexOf("/") + 1); 
      pivotAttributes[3] = node.getTextAttr(n, 1, "PIVOT.SEPARATE");
      pivotAttributes[0] = node.getTextAttr(n, 1, "PIVOT.X");
      pivotAttributes[1] = node.getTextAttr(n, 1, "PIVOT.Y");
      pivotAttributes[2] = node.getTextAttr(n, 1, "PIVOT.Z");
      if (pivotAttributes[0] != undefined)
      {
        this.ui.SourceNodeName_Label.text = 'source: ' + nodeName + ' (Pivot)';
        if (pivotAttributes[0].length == 0)
        {
            this.ui.SourceNodeName_Label.text = 'source: --';
        }
      }
      else
      {
        this.ui.SourceNodeName_Label.text = 'source: --';
      }
  }
  this.copyPosition = function()
  {    
      pivotAttributes[0] = undefined;
      pivotAttributes[1] = undefined;
      pivotAttributes[2] = undefined;
      pivotAttributes[3] = undefined;
      pivotAttributes[4] = 'position';
      var n=selection.selectedNode(0);
      var nodeName = n.slice(n.indexOf("/") + 1); 
      var crFrm = frame.current();  
      //pivotAttributes[3] = node.getTextAttr(n, crFrm , "POSITION.SEPARATE");
      pivotAttributes[0] = node.getTextAttr(n, crFrm , "POSITION.X");
      pivotAttributes[1] = node.getTextAttr(n, crFrm , "POSITION.Y");
      //pivotAttributes[2] = node.getTextAttr(n, crFrm , "POSITION.Z");
      if (pivotAttributes[0].length == 0)
      {
        //pivotAttributes[3] = node.getTextAttr(n, crFrm , "POS.SEPARATE");
        pivotAttributes[0] = node.getTextAttr(n, crFrm , "POS.X");
        pivotAttributes[1] = node.getTextAttr(n, crFrm , "POS.Y");
        //pivotAttributes[2] = node.getTextAttr(n, crFrm , "POS.Z");      
      }
      if (pivotAttributes[0].length == 0)
      {
        //pivotAttributes[3] = node.getTextAttr(n, crFrm , "OFFSET.SEPARATE");
        pivotAttributes[0] = node.getTextAttr(n, crFrm , "OFFSET.X");
        pivotAttributes[1] = node.getTextAttr(n, crFrm , "OFFSET.Y");
        //pivotAttributes[2] = node.getTextAttr(n, crFrm , "OFFSET.Z");      
      }
      if (pivotAttributes[0] != undefined)
      {
        this.ui.SourceNodeName_Label.text = 'source: ' + nodeName + ' (Position)';
        if (pivotAttributes[0].length == 0)
        {
            this.ui.SourceNodeName_Label.text = 'source: --';
        }
      }
      else
      {
        this.ui.SourceNodeName_Label.text = 'source: --';
      }
  }
  this.pastePivots = function ()
  {
    if (pivotAttributes[0] != undefined)
    {
      if (pivotAttributes[0].length > 0)  
      {
        scene.beginUndoRedoAccum("Paste Pivots");
        var selLen = selection.numberOfNodesSelected();     
        for (var i = 0 ; i < selLen; i++)
        {
          var n = selection.selectedNode(i);
          node.setTextAttr( n, "PIVOT.X", 1, pivotAttributes[0]);        
          node.setTextAttr( n, "PIVOT.Y", 1, pivotAttributes[1]);
          //node.setTextAttr( n, "PIVOT.Z", 1, pivotAttributes[2]);  //Not needed for pivot points      
        }
        scene.endUndoRedoAccum();
      }
      else
      {
        MessageBox.information("No pivot or position copied"); 
      }    
    }
    else
    {
      MessageBox.information("No pivot or position copied"); 
    }    
  }
  this.pastePositions = function ()
  {
    if (pivotAttributes[0] != undefined)
    {
      if (pivotAttributes[0].length > 0)  
      {
        scene.beginUndoRedoAccum("Paste Positions");
        var selLen = selection.numberOfNodesSelected(); 
        var crFrm = frame.current();   
        for (var i = 0 ; i < selLen; i++)
        {
          var n = selection.selectedNode(i);
          node.setTextAttr(n, "OFFSET.X", crFrm, pivotAttributes[0]); 
          node.setTextAttr(n, "OFFSET.Y", crFrm, pivotAttributes[1]);
          //node.setTextAttr( n, "OFFSET.Z", crFrm, pivotAttributes[2]);  //Not needed for pivot points      
          node.setTextAttr(n, "POSITION.X", crFrm, pivotAttributes[0]); 
          node.setTextAttr(n, "POSITION.Y", crFrm, pivotAttributes[1]);
          //node.setTextAttr( n, "POSITION.Z", crFrm, pivotAttributes[2]);  //Not needed for pivot points 
          node.setTextAttr( n, "POS.X", crFrm, pivotAttributes[0]);        
          node.setTextAttr( n, "POS.Y", crFrm, pivotAttributes[1]);
          //node.setTextAttr( n, "POS.Z", crFrm, pivotAttributes[2]);  //Not needed for pivot points   
        }
        scene.endUndoRedoAccum();
      }
      else
      {
        MessageBox.information("No pivot or position copied"); 
      }    
    }
    else
    {
      MessageBox.information("No pivot or position copied"); 
    }    
  }  
  this.ui = UiLoader.load(uiPath);
  this.ui.GroupBox_1.GetPivot_Button.released.connect(this, this.copyPivot);
  this.ui.GroupBox_1.GetPosition_Button.released.connect(this, this.copyPosition);
  this.ui.GroupBox_2.SetPivots_Button.released.connect(this, this.pastePivots);
  this.ui.GroupBox_2.SetPositions_Button.released.connect(this, this.pastePositions);
}
function CF_CopyPastePivots()
{
  //This piece of code is based William Saito's script 'Selection Sets 2.0' - START// 
  //The scipt can be downloaded at https://toonboomscripts.com/2016/03/29/selection-sets-2/
  if(specialFolders.userConfig.indexOf("USA_DB") != -1)
  {
  	localPath = fileMapper.toNativePath(specialFolders.userConfig);
  	var idxOf = localPath.indexOf("users");
  	localPath_ui = localPath.slice(0, idxOf) + "scripts";
  }
  else
  {
  	localPath = specialFolders.userConfig;
  	var idxOf_full = localPath.indexOf("full-");
  	var version = localPath.slice(idxOf_full + 5, -5);
  	localPath_ui = localPath.replace("/full-" + version + "-pref","/" + version +"-scripts");
  }
  //This piece of code is based William Saito's script 'Selection Sets 2.0' - END// 
  localResourcePath_ui = localPath_ui + "/CF_CopyPastePivots-Resources/v.1.0.1";
  var uiFile = 'CF_CopyPastePivots.ui';
  var uiPath = localResourcePath_ui + "/" + uiFile;
  var uif = new File(uiPath);
  if( !uif.exists )
  {
    MessageBox.information('"' + uiFile + '"' + ' file not found.' + '\n'  + '\n' +  'Please paste the file into the following directory:' + '\n' + '\n' +  localResourcePath_ui + '/');
    return;
  }
  var f = new __execDialog(uiPath);
  f.ui.show();
}