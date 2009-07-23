#!/usr/bin/python
# To change this template, choose Tools | Templates
# and open the template in the editor.


import wx
import wx.lib.scrolledpanel  as myscrolledpanel
import wx.lib.inspection
MYFRAMESIZE = (800,500)

import sys
sys.path.append("/home/hari/gridder")
class MaFrame(wx.Frame):
    plates = []
    components = []

    PLATE_CONFIGURED = False
    IS_BEGUN = True

    def __init__(self,*args,**kwds):
        kwds["size"] = MYFRAMESIZE
        wx.Frame.__init__(self,*args, **kwds)
        self.CreateStatusBar(1,0)
        kwds["style"] = wx.THICK_FRAME
        frame_sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(frame_sizer)
        
    def do_layout(self):
        self.Layout()
#        self.Fit()

class Validate_Plate_Coordinate(wx.PyValidator):
    from gridder import masterplate
    from masterplate import Masterplate
    myplate = Masterplate(2000)

    def __init__(self):
        wx.PyValidator.__init__(self)

    def Clone(self):
        return self.__class__()

    def Validate(self,win):
        window =wxPyTypeCast(self.GetWindow(), "wxTextCtrl")
        text = window.GetValue()
        print "GOT VAL %s" % text
        if len(text) == 0 or text=="":
            wx.MessageBox("Please enter a plate coordinate between A1 and H12: Empty Box")
            print "FALSE EVAL reason empty "
            return False
        if text not in myplate.ordered_keys:
            wx.MessageBox("Please enter a plate coordinate between A1 and H12")
            print "FALSE EVAL reason no key match "
            return False
        else:
            textctrl.Refresh()
            return True

    def TransferToWindow(self):
        return True
    def TransferFromWindow(self):
        return True
    def OnChar(self,event):
        key = chr(event.GetKeyCode())
        if key in self.myplate.ordered_keys:
            return
        event.Skip()


class PlatePanel(wx.ScrolledWindow):
    num_subplates = 1
    subplate_array_sizers = []
    plate_customizer_dict = {1:("A1","H12"),2:("A1","D6","E1","H12"),3:("A1","","","","","H12"),4:("A1","D6","A7","D12","D1","H6","D7","H12")}

    def __init__(self,*args,**kwds):
        kwds["size"] = MYFRAMESIZE
        wx.ScrolledWindow.__init__(self,*args,**kwds)
##        self.SetBackgroundColour(wx.Colour(0,153,77)) # GREEN
#        self.SetBackgroundColour(wx.Colour(204,255,255)) # BABY BLUE
        self.SetBackgroundColour(wx.Colour(194,194,194))
        self.platelabel = wx.StaticText(parent=self,id=-1,label="Plate %s" % self.num_subplates,size=(-1,-1),style=wx.ALIGN_CENTER)
        self.text_ctrl_1 = wx.TextCtrl(parent=self, id=-1,value= "A1",size=(50,-1),validator=Validate_Plate_Coordinate())
        self.text_ctrl_2 = wx.TextCtrl(parent=self,id=-1,value="A12",size=(50,-1),validator=Validate_Plate_Coordinate())
        self.plate_add_button = wx.Button(self,label="Add Plate")
        self.plate_display_button = wx.Button(self,label="Set Plate Config")
        self.SetScrollRate(3, 3)
        self.do_connections()
        self.do_layout()
        self.bind_delete_events()
    
        
    def do_layout(self):
        self.sizer_top = wx.BoxSizer(wx.VERTICAL)
        sizer_widgets = wx.BoxSizer(wx.HORIZONTAL)
        sizer_widgets.Add(self.platelabel,1,wx.ALIGN_CENTER)
        sizer_widgets.Add(self.text_ctrl_1,1,wx.ALIGN_RIGHT)
        sizer_widgets.Add(self.text_ctrl_2,1,wx.ALIGN_RIGHT)
        self.sizer_top.Add(sizer_widgets,0,wx.EXPAND)
        self.subplate_array_sizers.append(sizer_widgets)
        self.sizer_top.Add(self.plate_add_button,0,wx.ALIGN_RIGHT|wx.ALL,10)
        self.sizer_top.Add(self.plate_display_button)
        self.SetSizer(self.sizer_top)
        self.sizer_top.Layout()
        self.sizer_top.FitInside(self)


    def do_connections(self):
        self.Bind(wx.EVT_BUTTON,self.add_plate_def,self.plate_add_button)
        self.Bind(wx.EVT_BUTTON,self.set_plateconfig,self.plate_display_button)
#        self.Bind(wx.EVT_MOUSEWHEEL, self.on_mousewheel)
        
    def on_mousewheel(self,event):
        self.Refresh()
        self.SetFocusIgnoringChildren()
        print "refreshed"
        event.Skip()

    def add_plate_def(self,event):
        self.GetParent().GetStatusBar().SetStatusText("Adding Plate %s" % self.num_subplates)
        self.num_subplates = self.num_subplates + 1
        # Get the add plate Button and hold on to it
        for sizers in self.subplate_array_sizers:
            self.sizer_top.Detach(sizers)

        self.sizer_top.Detach(self.plate_add_button)
        self.sizer_top.Detach(self.plate_display_button)
        platelabel = wx.StaticText(parent=self,id=-1,label="Plate %s" % self.num_subplates , size=(-1,-1),style=wx.ALIGN_CENTER )
        text_ctrl_1 = wx.TextCtrl(self, -1, "",(50,-1),validator=Validate_Plate_Coordinate())
        text_ctrl_2 = wx.TextCtrl(self,-1,"",(50,-1),validator=Validate_Plate_Coordinate())
        sizer_widgets = wx.BoxSizer(wx.HORIZONTAL)
        sizer_widgets.Add(platelabel,1,wx.ALIGN_RIGHT|wx.ALIGN_CENTER)
        sizer_widgets.Add(text_ctrl_1,1,wx.ALIGN_RIGHT|wx.ALIGN_CENTER)
        sizer_widgets.Add(text_ctrl_2,1,wx.ALIGN_RIGHT|wx.ALIGN_CENTER)
        self.subplate_array_sizers.append(sizer_widgets)
        for w in self.subplate_array_sizers:
            self.sizer_top.Add(w,0,wx.EXPAND)
        self.sizer_top.Add(self.plate_add_button,0,wx.ALIGN_RIGHT|wx.ALL,10)
        self.sizer_top.Add(self.plate_display_button)
        #self.sizer_top.Add(self.plate_add_button,1,wx.RIGHT|wx.ALIGN_BOTTOM,10)
        self.sizer_top.Layout()
        self.sizer_top.Fit(self)
        self.has_config()
        self.GetParent().do_layout()
        self.bind_delete_events()
        #self.GetParent().Fit()


    def bind_delete_events(self):
        import re
        plate_pattern = re.compile("Plate \d+")
        for child in self.GetChildren():
            if isinstance(child, wx.StaticText):
                if plate_pattern.search(child.GetLabel()):
#                    child.Bind(wx.EVT_RIGHT_DOWN ,lamda event, caller=child :self.delete_platedef(event,caller))
                    child.Bind(wx.EVT_RIGHT_DOWN,lambda event, caller= child: self.delete_platedef(event,caller))
    def has_config(self):
        # Local variable to run along plate config tuple using self.plate_customizer_dict[self.num_subplates][scanner]
        scanner = 0
        if self.plate_customizer_dict.has_key(self.num_subplates):
            for w in self.subplate_array_sizers:
                for possible_plate in w.GetChildren(): 
                    if isinstance(possible_plate.GetWindow(), wx.TextCtrl):
                        self.GetParent().GetStatusBar().SetStatusText("settingplate boundaries automatic done")
                        possible_plate.GetWindow().SetValue(self.plate_customizer_dict[self.num_subplates][scanner])
                        scanner = scanner + 1
#
#    def on_right_click(self,event):
#        self.PopupMenu(self.menu)

    def delete_platedef(self,event,caller):
        import re
        plate_pattern = re.compile("Plate \d")
        menu = wx.Menu()
        menu.Append(-1,"Delete Plate")
        self.PopupMenu(menu)
         # Implement Component Deletion"
        print "Delete PlateDef called on object", caller.GetLabel()
        self.sizer_top.Remove(caller)
        #self.sizer_top.Add(self.plate_add_button,1,wx.RIGHT|wx.ALIGN_BOTTOM,10)
        self.sizer_top.Layout()
        self.sizer_top.Fit(self)
        self.has_config()
        self.GetParent().do_layout()
        self.bind_delete_events()
        
    def set_plateconfig(self,event):
        from gridder.masterplate import Masterplate
        myplate = Masterplate(2000)
        scanned_plate_def = None
        # Local variable to identify plate corner
        count = 0
        childcount = 0
        platecorner = {1:"left corner",0:"right corner"}
        max = len(self.GetChildren())
        for child in self.GetChildren():
            if isinstance(child,wx.StaticText):
                scanned_plate_def = child.GetLabel()
            if isinstance(child,wx.TextCtrl):
                text = child.GetValue()
                count = count + 1
                # flag to determine if corner is left or right depending on platecorner = {1:"left corner",0:"right corner"}
                flag = count % 2
                if len(text) == 0 or text=="":
                    wx.MessageBox("Please enter a plate coordinate between A1 and H12 for %s,%s" % (platecorner[flag],scanned_plate_def))
                    self.GetParent().PLATE_CONFIGURED = False
                    break
                elif text not in myplate.ordered_keys:
                    wx.MessageBox("Please enter a plate coordinate between A1 and H12 for %s,%s" % (platecorner[flag],scanned_plate_def))
                    self.GetParent().PLATE_CONFIGURED = False
                    break
                else:
                    if scanned_plate_def not in self.GetParent().plates:
                        self.GetParent().plates.append(scanned_plate_def)
                        print "Got value:%s" % child.GetValue()
            childcount = childcount + 1
            if childcount == max :
                print self.GetParent().PLATE_CONFIGURED
                self.GetParent().PLATE_CONFIGURED = True
                self.GetParent().PLATE_CONFIGURED
                self.GetParent().FindWindowByName("plateop").make_plate_choicelist()
                self.GetParent().FindWindowByName("plateop").refresh_plate_choice_comboboxes()

        event.Skip()





class  ComponentPanel(wx.ScrolledWindow):
    import csv
    num_components = 1
    component_array_sizers = []
    is_VALID = False
    
    def __init__(self,*args, **kwds):
        kwds["size"] = MYFRAMESIZE
        wx.ScrolledWindow.__init__(self,*args,**kwds)
#        self.SetBackgroundColour(wx.Colour(252,244,222))
        self.SetBackgroundColour(wx.Colour(133,133,133))
        self.top_grid_sizer = wx.GridSizer(rows=-1, cols=6, hgap=5, vgap=5)
        self.fileselector_button = wx.Button(parent=self,id=-1,label="Component File")
        self.add_component_button = wx.Button(parent=self,id=-1,label="Add Component")
        self.add_buffer_button = wx.Button(parent=self,id=-1,label="Add Buffer")
        self.top_grid_sizer.Add(self.fileselector_button)
        self.top_grid_sizer.Add(self.add_component_button)
        self.top_grid_sizer.Add(self.add_buffer_button)
        self.top_grid_sizer.Add((1,1),1)
        self.top_grid_sizer.Add((1,1),1)
        self.top_grid_sizer.Add((1,1),1)
        self.component_number_slot = wx.StaticText(parent=self,id=-1,label="",size=(-1,-1))
        self.component_name_label = wx.StaticText(self, -1, "Component Name",(-1,-1))
        self.component_conc_label = wx.StaticText(self,-1,"Concentration",(-1,-1))
        self.component_volume_label = wx.StaticText(self,-1,"Volume",(-1,-1))
        self.component_ph_label = wx.StaticText(self,-1,"pH",(-1,-1))
        self.component_pka_label = wx.StaticText(self,-1,"pKa",(-1,-1))
        self.top_grid_sizer.Add(self.component_number_slot,1,wx.ALIGN_CENTER)
        self.top_grid_sizer.Add(self.component_name_label,wx.EXPAND|wx.ALIGN_CENTER)
        self.top_grid_sizer.Add(self.component_conc_label,1,wx.EXPAND|wx.ALIGN_CENTER)
        self.top_grid_sizer.Add(self.component_volume_label,wx.EXPAND|wx.ALIGN_CENTER)
        self.top_grid_sizer.Add(self.component_ph_label,1,wx.ALIGN_CENTER)
        self.top_grid_sizer.Add(self.component_pka_label,1,wx.ALIGN_CENTER)
        self.menu = wx.Menu()
        self.menu.Append(-1,"Delete Component")
        wx.EVT_MENU( self.menu, -1, self.delete_component )
        self.do_connections()
        self.bind_delete_events()
        self.SetScrollRate(3, 3)
        self.do_layout()
        


    def do_connections(self):
        self.Bind(wx.EVT_BUTTON , self.get_and_parse_file,self.fileselector_button)
        self.Bind(wx.EVT_BUTTON,self.manual_add_component,self.add_component_button)
        self.Bind(wx.EVT_BUTTON,self.manual_add_buffer,self.add_buffer_button)

    def bind_delete_events(self):
        import re
        component_pattern = re.compile("Component  \d")
        buffer_pattern = re.compile("Buffer  \d")
        for child in self.GetChildren():
            if isinstance(child, wx.StaticText):
                print child.GetLabel()
                if component_pattern.search(child.GetLabel()) or buffer_pattern.search(child.GetLabel()) :
                    child.Bind(wx.EVT_RIGHT_DOWN ,self.on_right_click)
   

    def on_right_click(self,event):
        self.PopupMenu(self.menu)

    def delete_component(self,event):
        # Implement Component Deletion" 
        print "Delete component called"

    def do_layout(self):
#        self.sizer_top = wx.BoxSizer(wx.VERTICAL)
#        self.sizer_top.Add(self.fileselector_button,0,wx.ALIGN_LEFT)
#        sizer_widgets = wx.BoxSizer(wx.HORIZONTAL)
#        self.top_grid_sizer.Add(self.componentlabel,1,wx.ALIGN_LEFT)
#        self.top_grid_sizer.Add(self.text_ctrl_1,1,wx.ALIGN_RIGHT)
#        self.top_grid_sizer.Add(self.text_ctrl_2,1,wx.ALIGN_RIGHT)
#        self.sizer_top.Add(sizer_widgets,0,wx.EXPAND)
#        self.component_array_sizers.append(sizer_widgets)
        self.SetSizer(self.top_grid_sizer)
#        self.top_grid_sizer.Fit(self)
#        self.top_grid_sizer.Layout()
#        self.GetParent().Fit(s)



    def create_component_gui_entry(self,component_array):
        if len(component_array) == 3:
            componentlabel = wx.StaticText(parent=self,id=-1,label="Component  %s" % self.num_components ,style=wx.ALIGN_CENTER)
            text_ctrl_1 = wx.TextCtrl(self, -1, component_array[0],(-1,-1))
            text_ctrl_2 = wx.TextCtrl(self,-1,component_array[1],(-1,-1))
            text_ctrl_3 = wx.TextCtrl(self,-1,component_array[2],(-1,-1))
            self.top_grid_sizer.Add(componentlabel,1,wx.ALIGN_CENTER)
            self.top_grid_sizer.Add(text_ctrl_1,1,wx.EXPAND|wx.ALIGN_CENTER)
            self.top_grid_sizer.Add(text_ctrl_2,1,wx.EXPAND|wx.ALIGN_CENTER)
            self.top_grid_sizer.Add(text_ctrl_3,1,wx.EXPAND|wx.ALIGN_CENTER)
            self.top_grid_sizer.Add((1,1),1)
            self.top_grid_sizer.Add((1,1),1)
            


        if len(component_array) == 5:
            componentlabel = wx.StaticText(parent=self,id=-1,label="Buffer  %s" % self.num_components ,style=wx.ALIGN_CENTER)
            text_ctrl_1 = wx.TextCtrl(self, -1, component_array[0],(-1,-1))
            text_ctrl_2 = wx.TextCtrl(self,-1,component_array[1],(-1,-1))
            text_ctrl_3 = wx.TextCtrl(self,-1,component_array[2],(-1,-1))
            text_ctrl_4 = wx.TextCtrl(self,-1,component_array[3],(-1,-1))
            text_ctrl_5 = wx.TextCtrl(self,-1,component_array[4],(-1,-1))
            self.top_grid_sizer.Add(componentlabel,1,wx.ALIGN_CENTER)
            self.top_grid_sizer.Add(text_ctrl_1,1,wx.EXPAND|wx.ALIGN_CENTER)
            self.top_grid_sizer.Add(text_ctrl_2,1,wx.EXPAND|wx.ALIGN_CENTER)
            self.top_grid_sizer.Add(text_ctrl_3,1,wx.EXPAND|wx.ALIGN_CENTER)
            self.top_grid_sizer.Add(text_ctrl_4,1,wx.EXPAND|wx.ALIGN_CENTER)
            self.top_grid_sizer.Add(text_ctrl_5,1,wx.EXPAND|wx.ALIGN_CENTER)
            
        self.bind_delete_events()
        self.top_grid_sizer.Fit(self)
        self.top_grid_sizer.Layout()
        self.GetParent().do_layout()
        self.num_components = self.num_components + 1
   
    def manual_add_component(self,event):
       self.create_component_gui_entry(["","",""])

    def manual_add_buffer(self,event):
        self.create_component_gui_entry(["","","","",""])
    
    def get_and_parse_file(self,event):
        import csv
        self.component_file = open(str(wx.FileSelector("Component File \"*.csv\" format","","","csv","*.csv")), "r")
        csvreader_object = csv.reader(self.component_file,dialect=csv)
        for component_array in csvreader_object:
            self.create_component_gui_entry(component_array)

    def set_components(self,event):
        for element in self.GetChildren:
            if isinstance(element,wx.StaticText):
                pass



class PromptingComboBox(wx.ComboBox) :
    def __init__(self, parent, value, choices=[], style=0, **par):
        wx.ComboBox.__init__(self, parent, wx.ID_ANY, value, style=style|wx.CB_DROPDOWN, choices=choices, **par)
        self.choices = choices
        self.Bind(wx.EVT_TEXT, self.EvtText)
        self.Bind(wx.EVT_CHAR, self.EvtChar)
        self.Bind(wx.EVT_COMBOBOX, self.EvtCombobox)
        self.ignoreEvtText = False

    def EvtCombobox(self, event):
        self.ignoreEvtText = True
        event.Skip()

    def EvtChar(self, event):
        if event.GetKeyCode() == 8:
            self.ignoreEvtText = True
        event.Skip()

    def EvtText(self, event):
        if self.ignoreEvtText:
            self.ignoreEvtText = False
            return
        currentText = event.GetString().upper()
        found = False
        for choice in self.choices :
            if choice.startswith(currentText):
                self.ignoreEvtText = True
                self.SetValue(choice)
                self.SetInsertionPoint(len(currentText))
                self.SetMark(len(currentText), len(choice))
                found = True
                break
        if not found:
            event.Skip()

class PlateOperations(wx.ScrolledWindow):
    #dict structure is an operations followed by a dict of arguments
    IS_COMPONENT = None
    IS_NUM = None
    IS_COORD = None
    operations_file_name = u"operations.csv"
    choices = []
    plate_choice_boxlist = []
    dispense_choice_boxlist = []

    def __init__(self,*args,**kwds):
        wx.ScrolledWindow.__init__(self,*args,**kwds)
        kwds["size"] = MYFRAMESIZE
        self.add_op_button = wx.Button(self,label="Add Operation")
        self.Bind(wx.EVT_BUTTON,self.add_operation,self.add_op_button)
        self.SetScrollRate(3,3)
        self.po_sizer = wx.GridSizer(-1,10,3,5)
        self.po_sizer.Add(self.add_op_button)
        for i in range(9):
            self.po_sizer.Add((1,1),1)
        
        self.make_choice_list()
        self.do_init_layout()
        self.SetScrollRate(3,3)
        self.SetSizer(self.po_sizer)
        self.po_sizer.Fit(self)
        
    def do_init_layout(self):
        self.Layout()
        self.GetParent().do_layout()

    def refresh_plate_choice_comboboxes(self):
#        print "hoobajabacks"
#        rows,cols =  self.po_sizer.CalcRowsCols()
#        for itemnum in range(11,rows*cols,cols):
#            print "Removing item no %d" % itemnum
#            self.po_sizer.Detach(self.po_sizer.GetItem(itemnum).GetWindow())
#            new_plate_choice = PromptingComboBox(self, "", self.platelist, style=wx.CB_SORT)
#            self.po_sizer.InsertItem(new_plate_choice.GetBestSize() ,itemnum)
#            print "REFRESH DONE at position %d" % itemnum
#        self.po_sizer.Layout()
#        print "refresh of exisiting combobox : Not yet Implemented"
        pass




    def add_operation(self,event):
        if self.GetParent().PLATE_CONFIGURED:
            print "Add Op"
            new_plate_choice = PromptingComboBox(self, "", self.platelist, style=wx.CB_SORT)
            new_dispense_combobox = PromptingComboBox(self, "", self.choices, style=wx.CB_SORT)
            self.plate_choice_boxlist.append(new_dispense_combobox)
            self.dispense_choice_boxlist.append(new_dispense_combobox)
            self.po_sizer.Add(new_plate_choice,wx.EXPAND|wx.ALIGN_CENTER)
            self.po_sizer.Add(new_dispense_combobox,wx.EXPAND|wx.ALIGN_CENTER)
            for i in range(8):
                self.po_sizer.Add((1,1),1)
            self.do_init_layout()
        else:
            wx.MessageBox("No Plates: Please Set Plate COnfig and then try")
  

    def make_plate_choicelist(self):
        # Called by Other Class to create list used to setup comboboxes here
        if self.GetParent().PLATE_CONFIGURED:
            self.platelist = self.GetParent().plates

#        print "SETTING BUTTON TO UNCLICKABLE " ,self.GetParent().FindWindowByName("platesetup").GetName()
#        self.GetParent().FindWindowByName("platesetup").plate_add_button.Enable(False)
        

    def make_choice_list(self):
        import csv
        self.dispense_choice_boxlist = []
        self.operations_file = open(self.operations_file_name, "r")
        csvreader_object = csv.reader(self.operations_file,dialect=csv)
        for operations_array_element in csvreader_object:
            print operations_array_element
            newchoice = operations_array_element[0]
            # Comments in file have # as first character and are ignored
            if newchoice[0] != "#":
                self.choices.append(newchoice)
        





if __name__=="__main__":

    app = wx.PySimpleApp()
    maframe = MaFrame(parent=None,title="GZilla")
    plate_panel = PlatePanel(parent=maframe,name="platesetup")
    maframe.GetSizer().Add(plate_panel,5,wx.EXPAND)
    component_panel = ComponentPanel(parent=maframe)
    maframe.GetSizer().Add(component_panel,4,wx.ALIGN_BOTTOM|wx.EXPAND)
    plateoperations = PlateOperations(parent=maframe,name="plateop")
    maframe.GetSizer().Add(plateoperations,4,wx.ALIGN_BOTTOM|wx.EXPAND)
    maframe.Layout()
    maframe.Show()
    print plateoperations.GetName()
    # Debug using this tool
    wx.lib.inspection.InspectionTool().Show()
    app.MainLoop()
