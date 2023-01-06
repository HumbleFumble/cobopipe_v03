"use strict"

/*
 *  
 *  TB_RemoveUnusedColors()
 *
 *  This Script checks the scene and all its drawings for the colors they use.
 *  Any color and palettes that are not used can be deleted. 
 *  The run time can be pretty long if there are a lot of drawings in the scene,
 *
 */

function noMoreColorsToDelete(paletteColor)
{
  for(var color in paletteColor.Colors)
  {
    return false;
  }
  return true;
}

function containsPalette(Palettes, PaletteID)
{
  if (Palettes[PaletteID] != undefined)
  {
    return true;
  }
  return false;
}

function getPalettesAndColors ( palettes, paletteList )
{  
  for(var j = 0; j < paletteList.numPalettes ; j++)
  {
    var colors = {};
    var palette = paletteList.getPaletteByIndex(j);
    if(!containsPalette(palettes,palette.id))
    {
      for(var colorIndex = 0 ; colorIndex < palette.nColors ; colorIndex++)
      {
        var curColor = palette.getColorByIndex(colorIndex);
        colors[curColor.id] = curColor;
      }
      palettes[palette.id] = {Palette: palette, Colors: colors};
    }
  }
}

function GetAllPalettesAndColors ()
{
  var palettes ={};
  
  for(var i = 0; i < element.numberOf();i++)
  {
    var elementId = element.id(i);
    var paletteList = PaletteObjectManager.getPaletteListByElementId(elementId);
    getPalettesAndColors(palettes,paletteList);    
  } 
  var scenePaletteList = PaletteObjectManager.getScenePaletteList();
  getPalettesAndColors(palettes,scenePaletteList);
  return palettes;
}
  
  
var createTreeItem = function( palette_Colors, treeWidget, colorItemList)
{
  var item = {};
  var treeItem = new QTreeWidgetItem(treeWidget);
  var palette = palette_Colors.Palette;
  treeItem.setText(0, palette.getName());
  treeItem.setCheckState(0,Qt.Checked);
  treeItem.setText(1,palette.getPath());
  var colors = palette_Colors.Colors;
   
  for(var color in colors)
  {
    var colorItem = new QTreeWidgetItem(treeItem);
    colorItem.setText(0,colors[color].name);
    colorItem.setCheckState(0,Qt.Checked);
    colorItemList.push({ ColorItem: colorItem, Palette: palette, ColorID: color  });
  }
  treeItem.setExpanded(true);
}



function RemoveUnusedColorsDialog(ui)
{
  this.ui = ui;
  this.exec = ui.exec;
  this.palettes = GetAllPalettesAndColors();
   
  var currentCount = 0;
  var drawingCount = 0;
  var showProgressDlg = false;
  var progressDlg; 
  for(var i = 0 ; i < element.numberOf(); i++)
  {
    var ElementId = element.id(i);
    drawingCount += Drawing.numberOf(ElementId);
  }
  if(drawingCount==0)
  {
    drawingCount = 1;
  }
  progressDlg = new QProgressDialog();
  progressDlg.modal = true;
  progressDlg.open();


  var usedColorIds = {};
  
  for(var i = 0; i < element.numberOf();i++) 
  {
    var ElementId = element.id(i);
    var elementPaletteList = PaletteObjectManager.getPaletteListByElementId(ElementId);
    var DrawingKeys = [];
    for ( var j = 0; j < Drawing.numberOf(ElementId);j++)
    {
      if(progressDlg.wasCanceled)
      {
        this.executeDlg = false;
        MessageBox.information("Canceled");
        return;
      }
      currentCount += 1;
      progressDlg.setLabelText("Inspecting " + element.getNameById(ElementId) + " - " + drawingId);
      progressDlg.setValue(100 * currentCount/drawingCount);
      var drawingId = Drawing.name(ElementId,j);
      var colorArray = DrawingTools.getDrawingUsedColors({ elementId : ElementId,  exposure : drawingId });
      for(var colorIndex = 0; colorIndex < colorArray.length; colorIndex++)
      {
        var colorID = colorArray[colorIndex];
        usedColorIds[colorID] = colorID;
      }
    }
  }

  progressDlg.hide();
  this.colorItemList = [];
  this.executeDlg = false;
  for( var i in this.palettes )
  {

    var pal = this.palettes[i];
    var paletteColors = pal.Colors;
    for (var color in paletteColors)
    {// The color id was used in drawings, this means that this color is used or is a cloned color
      if (usedColorIds[color] == color)
      {
        delete paletteColors[color];
      }
    }

    if(noMoreColorsToDelete(pal))
    {
      delete this.palettes[pal.id];
      continue;
    }
    this.executeDlg = true;
    createTreeItem( pal , ui.treeWidget, this.colorItemList);
  }
  if(!this.executeDlg)
  {
    MessageBox.information("No Unused Colors");
    return;
  }
  
  var checkColors = function( item )
  {
    var state = item.checkState(0);
    if(state!=Qt.PartiallyChecked)
    {
      for ( var i = 0 ; i < item.childCount(); i++)
      {
        item.child(i).setCheckState(0,state);
      }
    }
  }
  var checkPalette = function(par)
  {
    var checked = false;
    var unchecked = false;
    for(var i = 0; i < par.childCount();i++)
    {
      var colorItem = par.child(i);
      if(colorItem.checkState(0)== Qt.Checked)
      {
        checked = true;
        if(unchecked == true)
        {
          par.setCheckState(0,Qt.PartiallyChecked);
          return;
        }
      }
      else
      {
        unchecked = true;
        if(checked == true)
        {
          par.setCheckState(0,Qt.PartiallyChecked);
          return;
        }
      }
      
      if(checked== true)
      {
        par.setCheckState(0,Qt.Checked);
      }
      else
      {
        par.setCheckState(0,Qt.Unchecked)
      }
    }
  }
  var onChange= function(item, column)
  {
    var par = item.parent();
    if (par!=null)
    {
      checkPalette(par);
    }
    else if(item.childCount()!=0)
    {
     checkColors(item); 
    }
  }
  this.ui.treeWidget.itemClicked.connect(this,onChange)
  
}



function TB_RemoveUnusedColors()
{
  var scriptFolder = specialFolders.resource+ "/scripts";
  var uiPath = scriptFolder + "/TB_RemoveUnusedColors.ui";
  var uiTemplate = UiLoader.load(uiPath, scriptFolder);
  var ui = new RemoveUnusedColorsDialog(uiTemplate);
  if(ui.executeDlg == false)
  {
    return;
  }
  if(ui.exec()==QDialog.Accepted)
  {
    var warning = false;
    scene.beginUndoRedoAccum("Remove Unused Colors");
    for(var i = 0; i < ui.colorItemList.length; i++)
    {
      var item = ui.colorItemList[i];
      if(item.ColorItem.checkState(0) == Qt.Checked)
      {
        if(item.Palette.getLock()==true)
        {
          item.Palette.removeColor(item.ColorID);
        }
        else
        {
          warning = true;
        }
      }
    }
    // Remove Empty palettes from each palette list
    for(var i =0 ; i < PaletteObjectManager.getNumPaletteLists(); i++)
    {
      var curPaletteList = PaletteObjectManager.getPaletteListByIndex(i);
      var toRemove = [];
      for(var p = 0 ; p < curPaletteList.numPalettes; p++)
      {
        var palette = curPaletteList.getPaletteByIndex(p);
        if(palette.nColors == 0 )
        {
          if(curPaletteList.getLock()==true)
          {
            toRemove.push(palette.id);
          }
          else
          {
            warning = true;
          }
        }
      }
      for(var p = 0 ;  p < toRemove.length;p++)
      {
        curPaletteList.removePaletteById(toRemove[p]);
      }
    }
    scene.endUndoRedoAccum();
    
    if(warning)
    {
      MessageBox.information("Could not obtain the access rights to some items. \n They were not deleted.");
    }
  }
}