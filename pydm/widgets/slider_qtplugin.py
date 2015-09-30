from PyQt4 import QtGui, QtDesigner
from slider import PyDMSlider

class PyDMSliderPlugin(QtDesigner.QPyDesignerCustomWidgetPlugin):
  def __init__(self, parent = None):
    QtDesigner.QPyDesignerCustomWidgetPlugin.__init__(self)
    self.initialized = False
  
  def initialize(self, core):
    if self.initialized:
      return
    self.initialized = True

  def isInitialized(self):
    return self.initialized

  def createWidget(self, parent):
    return PyDMSlider(None, parent)

  def name(self):
    return "PyDMSlider"

  def group(self):
    return "PyDM Widgets"

  def toolTip(self):
    return ""

  def whatsThis(self):
    return ""

  def isContainer(self):
    return False
    
  def icon(self):
    return QtGui.QIcon()

  def domXml(self):
    return (
               '<widget class="PyDMSlider" name=\"pydmSlider\">\n'
               " <property name=\"toolTip\" >\n"
               "  <string></string>\n"
               " </property>\n"
               " <property name=\"whatsThis\" >\n"
               "  <string>Displays the value from an EPICS PV.</string>\n"
               " </property>\n"
               "</widget>\n"
               )

  def includeFile(self):
    return "slider"
