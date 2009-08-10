#!/usr/bin/python
# To change this template, choose Tools | Templates
# and open the template in the editor.



from wx._core import FindWindowByName
import wx
import wx.lib.scrolledpanel  as myscrolledpanel
import wx.lib.inspection
MYFRAMESIZE = (1212,700)

import sys


class MaFrame(wx.Frame):
    plateobjects = []
    componentobjects = []
    
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
    from gridder.masterplate import Masterplate
    myplate = Masterplate(2000)
    
    def __init__(self):
        wx.PyValidator.__init__(self)
    
    def Clone(self):
        return self.__class__()
    
    def Validate(self,win):
        window =wxPyTypeCast(self.GetWindow(), "wxTextCtrl")
        text = window.GetValue()
        if len(text) == 0 or text=="":
            wx.MessageBox("Please enter a plate coordinate between A1 and H12: Empty Box")
            return False
        if text not in myplate.ordered_keys:
            wx.MessageBox("Please enter a plate coordinate between A1 and H12")
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
    ID_DELETE_PLATE = 111
    plate_customizer_dict = {1:("A1","H12"),2:("A1","D6","E1","H12"),3:("A1","","","","","H12"),4:("A1","D6","A7","D12","E1","H6","E7","H12")}
    change_logger = []
    def __init__(self,*args,**kwds):
        kwds["size"] = MYFRAMESIZE
        wx.ScrolledWindow.__init__(self,*args,**kwds)
##        self.SetBackgroundColour(wx.Colour(0,153,77)) # GREEN
#        self.SetBackgroundColour(wx.Colour(204,255,255)) # BABY BLUE
        self.SetBackgroundColour(wx.Colour(194,194,194))
        self.plate_add_button = wx.Button(self,label="Add Plate")
        self.plate_display_button = wx.Button(self,label="Configure Done")
        self.refresh_button = wx.Button(self,label="Refresh")
        self.SetScrollRate(3, 3)
        self.do_connections()
        self.do_layout()
        self.bind_delete_events()
    
    def do_layout(self):
        self.master_sizer = wx.FlexGridSizer(rows=-1, cols=3, hgap=10, vgap=5)
        self.master_sizer.Add(self.refresh_button)
        self.master_sizer.Add(self.plate_add_button)
        self.master_sizer.Add(self.plate_display_button,wx.ALIGN_RIGHT)
        self.SetSizer(self.master_sizer)
        self.master_sizer.Layout()
        self.master_sizer.FitInside(self)
    
    def do_new_layout(self):
        self.plate_add_button = wx.Button(self,label="Add Plate")
        self.plate_display_button = wx.Button(self,label="Plate Configure Done")
        self.refresh_button = wx.Button(self,label="Refresh")
        self.do_connections()
        self.do_layout()
        self.bind_delete_events()
        self.num_subplates = 1
    
    def delete_all_plates(self,event):
        print "Destroying all children"
        self.DestroyChildren()
        
        self.do_new_layout()

    def do_connections(self):
        self.Bind(wx.EVT_BUTTON,self.add_plate_def,self.plate_add_button)
        self.Bind(wx.EVT_BUTTON,self.set_plate_config,self.plate_display_button)
	self.Bind(wx.EVT_BUTTON,self.delete_all_plates,self.refresh_button)
#        self.Bind(wx.EVT_MOUSEWHEEL, self.on_mousewheel)
    
    def on_mousewheel(self,event):
        self.Refresh()
        self.SetFocusIgnoringChildren()
        print "refreshed"
        event.Skip()
    
    def add_plate_def(self,event):
        self.GetParent().GetStatusBar().SetStatusText("Adding Plate %s" % self.num_subplates)
        platelabel = wx.StaticText(parent=self,id=-1,label="Plate %s" % self.num_subplates , size=(-1,-1),style=wx.ALIGN_CENTER )
        text_ctrl_1 = wx.TextCtrl(self, -1, "",(50,-1),validator=Validate_Plate_Coordinate())
        text_ctrl_2 = wx.TextCtrl(self,-1,"",(50,-1),validator=Validate_Plate_Coordinate())
        self.master_sizer.Add(platelabel,1,wx.ALIGN_CENTER)
        self.master_sizer.Add(text_ctrl_1,1,wx.ALIGN_CENTER)
        self.master_sizer.Add(text_ctrl_2,1,wx.ALIGN_CENTER)
        #self.sizer_top.Add(self.plate_add_button,1,wx.RIGHT|wx.ALIGN_BOTTOM,10)
        
        self.has_config()
        self.bind_delete_events()
        
        self.master_sizer.Layout()
        self.master_sizer.Fit(self)
        
        self.num_subplates = self.num_subplates + 1
        self.GetParent().do_layout()
        #self.GetParent().Fit()

    
    def bind_delete_events(self):
        import re
        plate_pattern = re.compile("Plate \d+")
        for child in self.GetChildren():
            if isinstance(child, wx.StaticText):
                if plate_pattern.search(child.GetLabel()):
#                    child.Bind(wx.EVT_RIGHT_DOWN ,lamda event, caller=child :self.delete_platedef(event,caller))
                    child.Bind(wx.EVT_RIGHT_DOWN,lambda event, caller= child: self.show_plate_delete_choice(event,caller))

    def has_config(self):
        # Local variable to run along plate config tuple using self.plate_customizer_dict[self.num_subplates][scanner]
        scanner = 0
        for child in self.GetChildren():
            if isinstance(child, wx.TextCtrl):
                self.GetParent().GetStatusBar().SetStatusText("settingplate boundaries automatic done")
                try:
                    child.SetValue(self.plate_customizer_dict[self.num_subplates][scanner])
                except KeyError , e:
                    pass
                scanner = scanner + 1
#
#    def on_right_click(self,event):
#        self.PopupMenu(self.menu)

    
    def show_plate_delete_choice(self,event,caller):
        def delete_component(mycaller):
            print "Deleting plate %s NOT YET IMPLEMENTED " % mycaller.GetLabel()
            wx.MessageBox("Deleting plate %s NOT YET IMPLEMENTED " % mycaller.GetLabel())
            # first find the element:
#            all_children = self.master_sizer.GetChildren()
#            print all_children
#            i = 1
#            for child in all_children:
#                if isinstance(child.GetWindow(),wx.StaticText):
#                    i = i + 3
#                    if child.GetWindow().GetLabel() == mycaller.GetLabel():
#                        print "removing three" , i , i + 1 , i + 2
#                        self.master_sizer.Remove(all_children[i].GetWindow())
#                        self.master_sizer.Remove(all_children[i + 1].GetWindow())
#                        self.master_sizer.Remove(all_children[i + 2].GetWindow())
#                        self.num_subplates = self.num_subplates - 1
        
        menu = wx.Menu()
        menu.Append(-1,"")
        menu.Append(self.ID_DELETE_PLATE,"Delete Plate")
        menu.Append(-1,"")
        self.PopupMenu(menu)
        wx.EVT_MENU(self,self.ID_DELETE_PLATE,delete_component(caller))

        
    def display_change_warning(self,event):
        if event.GetId() not in self.change_logger:
            msg = wx.MessageBox("Please Configure Plates and then check configure to propagate changes")
            self.change_logger.append(event.GetId())
            event.Skip()
        else:
            event.Skip()
        
    
    def set_plate_config(self,event):
        from gridder.masterplate import Masterplate
        # Servant plate object to check user input
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
                    if scanned_plate_def not in self.GetParent().plateobjects:
                        self.GetParent().plateobjects.append(scanned_plate_def)

            childcount = childcount + 1
            if childcount == max :
                self.GetParent().PLATE_CONFIGURED = True
                self.GetParent().PLATE_CONFIGURED
                self.GetParent().FindWindowByName("plateop").make_plate_choicetxtlist()
                self.GetParent().FindWindowByName("plateop").refresh_plate_choice_comboboxes()
        self.plate_setup_dict = {}
        rows,cols = self.master_sizer.CalcRowsCols()
        for row in range(1,rows,1):
#                print "p%s = plate.Plate(\"%s\",\"%s\")" % ( row,self.master_sizer.GetItem(cols*row + 1).GetWindow().GetValue() , self.master_sizer.GetItem(cols*row + 2).GetWindow().GetValue())
            win1 = self.master_sizer.GetItem(cols*row + 1).GetWindow()
            win2 = self.master_sizer.GetItem(cols*row + 2).GetWindow()
            self.plate_setup_dict[row] = [win1.GetValue(),win2.GetValue()]
            win1.Bind(wx.EVT_TEXT,self.display_change_warning)
            win2.Bind(wx.EVT_TEXT,self.display_change_warning)

        event.Skip()





class  ComponentPanel(wx.ScrolledWindow):
    import csv
    num_components = 1
    component_array_sizers = []
    is_VALID = False
    component_namedict = {}
    buffer_namedict = {}
    all_solutionsdict = {}
    IS_CONFIGURED = False
    change_logger = []

    def __init__(self,*args, **kwds):
        kwds["size"] = MYFRAMESIZE
        wx.ScrolledWindow.__init__(self,*args,**kwds)
#        self.SetBackgroundColour(wx.Colour(252,244,222))
        self.SetBackgroundColour(wx.Colour(133,133,133))
        self.top_grid_sizer = wx.GridSizer(rows=-1, cols=6, hgap=5, vgap=5)
        self.fileselector_button = wx.Button(parent=self,id=-1,label="Component File")
        self.add_component_button = wx.Button(parent=self,id=-1,label="Add Component")
        self.add_buffer_button = wx.Button(parent=self,id=-1,label="Add Buffer")
        self.set_component_button = wx.Button(parent=self,id=-1,label="Configure done")
        self.top_grid_sizer.Add(self.fileselector_button)
        self.top_grid_sizer.Add(self.add_component_button)
        self.top_grid_sizer.Add(self.add_buffer_button)
        self.top_grid_sizer.Add((1,1),1)
        self.top_grid_sizer.Add((1,1),1)
        self.top_grid_sizer.Add(self.set_component_button)
        self.component_number_slot = wx.StaticText(parent=self,id=-1,label="",size=(-1,-1))
        self.component_name_label = wx.StaticText(self, -1, "Component Name",style=wx.ALIGN_CENTER)
        self.component_conc_label = wx.StaticText(self,-1,"Concentration",style=wx.ALIGN_CENTER)
        self.component_volume_label = wx.StaticText(self,-1,"Volume",style=wx.ALIGN_CENTER)
        self.component_ph_label = wx.StaticText(self,-1,"pH",style=wx.ALIGN_CENTER)
        self.component_pka_label = wx.StaticText(self,-1,"pKa",style=wx.ALIGN_CENTER)
        self.top_grid_sizer.Add(self.component_number_slot,1,wx.ALIGN_CENTER)
        self.top_grid_sizer.Add(self.component_name_label,1,wx.EXPAND|wx.ALIGN_CENTER)
        self.top_grid_sizer.Add(self.component_conc_label,1,wx.EXPAND|wx.ALIGN_CENTER)
        self.top_grid_sizer.Add(self.component_volume_label,wx.EXPAND|wx.ALIGN_CENTER)
        self.top_grid_sizer.Add(self.component_ph_label,1,wx.EXPAND|wx.ALIGN_CENTER)
        self.top_grid_sizer.Add(self.component_pka_label,1,wx.EXPAND|wx.ALIGN_CENTER)
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
        self.Bind(wx.EVT_BUTTON,self.set_components,self.set_component_button)

    def bind_delete_events(self):
        import re
        component_pattern = re.compile("Component  \d")
        buffer_pattern = re.compile("Buffer  \d")
        for child in self.GetChildren():
            if isinstance(child, wx.StaticText):
#                print child.GetLabel()
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
            self.top_grid_sizer.Add(componentlabel,1,wx.ALIGN_LEFT|wx.ALIGN_CENTER)
            self.top_grid_sizer.Add(text_ctrl_1,1,wx.ALIGN_CENTER)
            self.top_grid_sizer.Add(text_ctrl_2,1,wx.ALIGN_CENTER)
            self.top_grid_sizer.Add(text_ctrl_3,1,wx.ALIGN_CENTER)
            self.top_grid_sizer.Add((1,1),1)
            self.top_grid_sizer.Add((1,1),1)


        
        if len(component_array) == 5:
            componentlabel = wx.StaticText(parent=self,id=-1,label="Buffer  %s" % self.num_components ,style=wx.ALIGN_CENTER)
            text_ctrl_1 = wx.TextCtrl(self, -1, component_array[0],(-1,-1))
            text_ctrl_2 = wx.TextCtrl(self,-1,component_array[1],(-1,-1))
            text_ctrl_3 = wx.TextCtrl(self,-1,component_array[2],(-1,-1))
            text_ctrl_4 = wx.TextCtrl(self,-1,component_array[3],(-1,-1))
            text_ctrl_5 = wx.TextCtrl(self,-1,component_array[4],(-1,-1))
            self.top_grid_sizer.Add(componentlabel,1,wx.ALIGN_LEFT|wx.ALIGN_CENTER)
            self.top_grid_sizer.Add(text_ctrl_1,1,wx.ALIGN_CENTER)
            self.top_grid_sizer.Add(text_ctrl_2,1,wx.ALIGN_CENTER)
            self.top_grid_sizer.Add(text_ctrl_3,1,wx.ALIGN_CENTER)
            self.top_grid_sizer.Add(text_ctrl_4,1,wx.ALIGN_CENTER)
            self.top_grid_sizer.Add(text_ctrl_5,1,wx.ALIGN_CENTER)
        
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

    def is_valid_component(self,array_of_vals):
        pass

    def display_change_warning(self,event):
        if event.GetId() not in self.change_logger:
            msg = wx.MessageBox("Please Configure Components and then check all operations to synchronize changes")
            self.change_logger.append(event.GetId())
            event.Skip()
        else:
            event.Skip()

    def set_components(self,event):
        import re
        spaces = re.compile("\s+")
        rows,cols = self.top_grid_sizer.CalcRowsCols()
        for rownum in range(2,rows,1):
            if "Component" in self.top_grid_sizer.GetItem(rownum*cols + 0 ).GetWindow().GetLabel():
                if (self.top_grid_sizer.GetItem(rownum*cols + 1 ).GetWindow().GetValue() or \
                self.top_grid_sizer.GetItem(rownum*cols + 2 ).GetWindow().GetValue() or \
                self.top_grid_sizer.GetItem(rownum*cols + 3 ).GetWindow().GetValue() ) == "":
                    wx.MessageBox("Please Fill in all Component parameters")
                else:
                    itemvals = []
                    for t in range(3):
                        win = self.top_grid_sizer.GetItem(rownum*cols + t + 1).GetWindow()
                        itemvals.append(win.GetValue())
                        win.Bind(wx.EVT_TEXT,self.display_change_warning)

                    # component_namedict is keyed by component number(int) and has index 0 : Name, index 1: Conc, index 2: Volume
                    print "Added component num :  %d , Name : %s , Concentration : %s Volume : %s " % tuple([rownum] + itemvals)

                    self.component_namedict[rownum] = itemvals
                    self.all_solutionsdict[rownum] = itemvals

            if "Buffer" in self.top_grid_sizer.GetItem(rownum*cols + 0 ).GetWindow().GetLabel():
                if self.top_grid_sizer.GetItem(rownum*cols + 1 ).GetWindow().GetValue() == "" or \
                self.top_grid_sizer.GetItem(rownum*cols + 2 ).GetWindow().GetValue() == "" or \
                self.top_grid_sizer.GetItem(rownum*cols + 3 ).GetWindow().GetValue() == "" or \
                self.top_grid_sizer.GetItem(rownum*cols + 4 ).GetWindow().GetValue() == "" or \
                self.top_grid_sizer.GetItem(rownum*cols + 5 ).GetWindow().GetValue() == "":
                    wx.MessageBox("Please Fill in all Buffer Parameters")
                else:
                    itemvals = []
                    for t in  range(5):
                        itemvals.append(self.top_grid_sizer.GetItem(rownum*cols + t + 1).GetWindow().GetValue())
                        # component_namedict is keyed by component number(int) and has index 0 : Name, index 1: Conc, index 2: Volume , index 3 :pH , index 4 : pka
                        # NOTE ROWNUMS are part of sequence and not separate i.e. keys here dont start at 0 and may not be sequential
                    self.buffer_namedict[rownum] = itemvals
                    self.all_solutionsdict[rownum] = itemvals

#                        print "Added buffer component num :  %d , Name : %s , Concentration : %s Volume : %s pH: %s  pKa : %s" % tuple([rownum] + itemvals)
        self.GetParent().FindWindowByName("plateop").make_component_choice_list()
        self.IS_CONFIGURED = True




class PromptingComboBox(wx.ComboBox) :
    def __init__(self, parent, value, choices=[], style=0, rowposition=0,**par):
        wx.ComboBox.__init__(self, parent, wx.ID_ANY, value, style=style|wx.CB_DROPDOWN, choices=choices,**par)
        self.choices = choices
        self.Bind(wx.EVT_TEXT, self.EvtText)
        self.Bind(wx.EVT_CHAR, self.EvtChar)
        self.Bind(wx.EVT_COMBOBOX, self.EvtCombobox)
        self.ignoreEvtText = False
        self.rowposition = rowposition
    
    def EvtCombobox(self, event):
        self.ignoreEvtText = True
        event.Skip()

    def SetChoices(self,newchoices):
        self.choices = newchoices

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
    function_dict = {"Add To Row":"push_component_to_row_on_masterplate",\
    "Add To Column":"push_component_to_column_on_masterplate","Add To Entire Plate":"push_component_uniform_to_masterplate",\
    "Gradient Along X":"gradient_along_x","Gradient Along Y":"gradient_along_y","Gradient List Along X":"gradientlist_along_x",\
    "Gradient List Along Y":"gradientlist_along_y","Component To Multiple Rows":"push_component_rowlist",\
    "Component To Multiple Columns":"push_component_columnlist","Buffer pH Gradient Along X":"ph_gradient_alongx","Buffer pH Gradient Along Y":"ph_gradient_alongy",\
    "Buffer pH List Along X":"ph_list_alongx","Buffer pH List Along Y":"ph_list_alongy","Make To 100 Along X":"maketo100_alongx",\
    "Make To 100 Along Y":"maketo100_alongy","Make To 100 List X":"maketo100_listx","Make To 100 List Y":"maketo100_listy"}
    masterdict = {'Gradient List Along X': ['Component', 'LISTVALS'], 'Gradient List Along Y': ['Component', 'LISTVALS'], 'Make To 100 Along X': ['Component', 'Component', 'FinalConc', 'FinalConcStartComponent1', 'FinalConcStopComponent1'], 'Make To 100 Along Y': ['Component', 'Component', 'FinalConc', 'FinalConcStartComponent1', 'FinalConcStopComponent1'], 'Add To Entire Plate': ['Component', 'FinalConc'], 'Make To 100 List X': ['Component', 'Component', 'FinalConc', 'LISTVALS'], 'Add To Column': ['Component', 'FinalConc', 'NUM'], 'Buffer pH List Along Y': ['Buffer', 'Buffer', 'FinalConc', 'LISTVALS'], 'Buffer pH List Along X': ['Buffer', 'Buffer', 'FinalConc', 'LISTVALS'], 'Add To Row': ['Component', 'FinalConc', 'ALPHA'], 'Buffer pH Gradient Along Y': ['Buffer', 'Buffer', 'FinalConc', 'pHSTART', 'pHSTOP'], 'Buffer pH Gradient Along X': ['Buffer', 'Buffer', 'FinalConc', 'pHSTART', 'pHSTOP'], 'Component To Multiple Rows': ['Component', 'FinalConc', 'LISTROWS'], 'Component To Multiple Columns': ['Component', 'FinalConc', 'LISTCOLS'], 'Make To 100 List Y': ['Component', 'Component', 'FinalConc', 'LISTVALS'], 'Gradient Along Y': ['Component', 'FinalConcStart', 'FinalConcStop'], 'Gradient Along X': ['Component', 'FinalConcStart', 'FinalConcStop']}


    IS_COMPONENT = None
    IS_NUM = None
    IS_COORD = None
   
    choices = []
    plate_combobox_objects = []
    dispense_choice_boxlist = []
    platelist = []
    plate_operations = {}
    # Combobox choices populated by events that propagate from above
    component_frame_choices = []
    buffer_frame_choices = []

    # plate_id_mapper_dict maps plate components to their row positions
    plate_id_mapper_dict = {}
    def __init__(self,*args,**kwds):
        import os
        wx.ScrolledWindow.__init__(self,*args,**kwds)
        kwds["size"] = MYFRAMESIZE
        self.add_op_button = wx.Button(self,label="Add Operation")
        self.make_plate_button = wx.Button(self,label="Make Plate")
        self.Bind(wx.EVT_BUTTON,self.add_operation,self.add_op_button)
        self.Bind(wx.EVT_BUTTON,self.make_plate,self.make_plate_button)

        self.SetScrollRate(3,3)
        self.po_sizer = wx.FlexGridSizer(-1,10,20,20)
        self.po_sizer.Add(self.add_op_button)
        self.po_sizer.Add(self.make_plate_button)

        for i in range(8):
            self.po_sizer.Add((1,1),1)
        
        self.make_choice_list()
        self.do_init_layout()
        self.SetScrollRate(3,3)
        self.SetSizer(self.po_sizer)
        self.po_sizer.Fit(self)
    
    def do_init_layout(self):
        self.Layout()
        self.GetParent().do_layout()
        self.SetScrollRate(3,3)
        self.po_sizer.FitInside(self)
    
    def refresh_plate_choice_comboboxes(self):
        i = 0
        for item in self.plate_combobox_objects:
            # Simply setting the combobox_object.choice to new choices did not do it
            # One has to clear the present plate choices and repopulate the list
            item.Clear()
            # Repopulate the combobox object with the new items

            for c in self.platelist:
                item.Append(c)
           

    def on_plate_combobox_select(self,event,platecallercombobox):
#        print "selected plate combobox event %s %s from grid row %d" % (event.GetString(),event.GetId(),platecallercombobox.rowposition)
        if platecallercombobox.rowposition in self.plate_operations.keys():
            myopobject = self.plate_operations[platecallercombobox.rowposition]
        else:
            myopobject = OperationObject()
            self.plate_operations[platecallercombobox.rowposition] = myopobject 
        myopobject.plate = event.GetString()

    def getRowFiringEvent(self,event):
        pass



    def on_operation_combobox_select(self,event,operationcombobox):

        if not self.GetParent().FindWindowByName("components").IS_CONFIGURED:
            self.make_component_choice_list()

#        print "selected Operation combobox event %s %s from rid row %d " % (event.GetString(),event.GetId(),operationcombobox.rowposition)
        for delcounter in range(2,10,1):
            oldwindow = self.po_sizer.GetItem(int(operationcombobox.rowposition)*int(10) + delcounter).GetWindow()
            dummypanel = wx.Panel(self,-1,size=(140,-1))
            self.po_sizer.Replace(oldwindow ,dummypanel )
            oldwindow.Destroy()

        mystring = event.GetString()
        if operationcombobox.rowposition not in  self.plate_operations:
            myobj = OperationObject()
            self.plate_operations[operationcombobox.rowposition] = myobj
        else:
            myobj = self.plate_operations[operationcombobox.rowposition]
        # Replace values of operations object 
        myobj.op = event.GetString()
        myobj.argdict = {}
        myobj.component_dict = {}
        argcount = 0
        for arg in self.masterdict[event.GetString()]:

            if arg  == "Component":
                newcombo1 = PromptingComboBox(self,"",choices=self.component_frame_choices,rowposition=operationcombobox.rowposition)
                self.Bind(wx.EVT_COMBOBOX,lambda event, caller=newcombo1,row=operationcombobox.rowposition,column=argcount :self.on_component_comobobox_select(event,caller,row,column),newcombo1 )
                if self.po_sizer.GetItem(int(operationcombobox.rowposition)*10  + 2 + argcount ):
                    oldwindow = self.po_sizer.GetItem(int(operationcombobox.rowposition)*int(10) + int(2) + argcount).GetWindow()
                    self.po_sizer.Replace(oldwindow , newcombo1)
                    oldwindow.Destroy()
                    self.Layout()


                else:
                    self.po_sizer.Replace(int(operationcombobox.rowposition)*10 + int(2) + argcount, newcombo)
                    self.po_sizer.Layout()

            elif arg == "Buffer":
                print self.buffer_frame_choices
                newcombo2 = PromptingComboBox(self,"",choices=self.buffer_frame_choices,rowposition=operationcombobox.rowposition)
                self.Bind(wx.EVT_COMBOBOX,lambda event, caller=newcombo2,row=operationcombobox.rowposition,column=argcount :self.on_component_comobobox_select(event,caller,row,column),newcombo2 )
                if self.po_sizer.GetItem(int(operationcombobox.rowposition)*10  + 2 + argcount ):
                    print "replace called on posn %d column %d " % (int(operationcombobox.rowposition)*int(10) + int(2) + argcount,argcount )
                    oldwindow = self.po_sizer.GetItem(int(operationcombobox.rowposition)*int(10) + int(2) + argcount).GetWindow()
                    self.po_sizer.Replace(oldwindow , newcombo2)
                    oldwindow.Destroy()
                    self.Layout()


                else:
                    print " Fresh item insertion attempt"
                    self.po_sizer.Replace(int(operationcombobox.rowposition)*10 + int(2) + argcount, newcombo)
                    self.po_sizer.Layout()

            else:
                newtextctrl = wx.TextCtrl(self,-1,"%s" % arg,size=(200,-1))
                newtextctrl.Bind(wx.EVT_TEXT,lambda event, caller=newtextctrl,row=operationcombobox.rowposition :self.process_argument(event,caller,row) )
                oldwindow = self.po_sizer.GetItem(int(operationcombobox.rowposition)*int(10) + int(2) + argcount).GetWindow()
                self.po_sizer.Replace(oldwindow , newtextctrl)
                oldwindow.Destroy()
                self.po_sizer.Layout()
                
            argcount = argcount + 1
        event.Skip()
            
    def process_argument(self,event,caller,row):
        myobj = self.plate_operations[row]
        myobj.argdict[event.GetId()]= caller.GetValue()

    def on_component_comobobox_select(self,event,caller,row,column):
        print "aefrgaergfertqert",event.GetString(),caller,row
        myobj = self.plate_operations[row]
        myobj.component_dict[column] = event.GetString()
        event.Skip()

    def add_operation(self,event):
        if self.GetParent().PLATE_CONFIGURED :
            if self.GetParent().FindWindowByName("components").IS_CONFIGURED:
                mynewchoice = self.platelist
                # Hardcode row position into object for script generation purposes
                currentrowpos,currentcolpos  = self.po_sizer.CalcRowsCols()
                new_platechoice_combobox = PromptingComboBox(self,"",choices=mynewchoice, style=wx.CB_SORT,rowposition=currentrowpos)
                # Need to lambda the combobox so we can know which row the event came from
                new_platechoice_combobox.Bind(wx.EVT_COMBOBOX,lambda event,platecallercombobox=new_platechoice_combobox : self.on_plate_combobox_select(event,platecallercombobox))
                new_dispense_combobox = PromptingComboBox(self,"", choices=self.choices, style=wx.CB_SORT,size=(280,-1),rowposition=currentrowpos)
                new_dispense_combobox.Bind(wx.EVT_COMBOBOX,lambda event,operationcombobox=new_dispense_combobox : self.on_operation_combobox_select(event,operationcombobox))
                self.plate_combobox_objects.append(new_platechoice_combobox)
                self.dispense_choice_boxlist.append(new_dispense_combobox)
                self.po_sizer.Add(new_platechoice_combobox,1,wx.EXPAND|wx.ALIGN_CENTER)
                self.po_sizer.Add(new_dispense_combobox,5,wx.EXPAND|wx.ALIGN_CENTER)
                for i in range(8):
                    dummypanel = wx.Panel(self,-1,size=(260,-1))
    #                dummypanel.SetBackgroundColour(wx.Colour(112,122,223))
                    self.po_sizer.Add(dummypanel,1,wx.EXPAND|wx.ALIGN_CENTER)
                self.do_init_layout()
                self.GetParent().Layout()
                for item in self.plate_combobox_objects:
                    self.plate_id_mapper_dict[item.GetId()] = item.rowposition
            else:
                wx.MessageBox("No Components: Please Configure components and then add operations")
        else:
            wx.MessageBox("No Plates: Please Set Plate COnfig and then try")

    def delete_operation(self,event):
        wx.MessageBox("Delete operation not implemented")
        event.Skip()
    
    def make_plate_choicetxtlist(self):
        # Called by Other Class to create list used to setup comboboxes here
        if self.GetParent().PLATE_CONFIGURED:
            self.platelist = self.GetParent().plateobjects

#        print "SETTING BUTTON TO UNCLICKABLE " ,self.GetParent().FindWindowByName("platesetup").GetName()
#        self.GetParent().FindWindowByName("platesetup").plate_add_button.Enable(False)

    def make_component_choice_list(self):
        self.component_frame_choices = []
        self.buffer_frame_choices = []
        try:
            for key in self.GetParent().FindWindowByName("components").all_solutionsdict:
                self.component_frame_choices.append(self.GetParent().FindWindowByName("components").all_solutionsdict[key][0])
            for key in self.GetParent().FindWindowByName("components").buffer_namedict:
                self.buffer_frame_choices.append(self.GetParent().FindWindowByName("components").buffer_namedict[key][0])
        except KeyError , e:
            print "Something wrong , no generation of Component list or plate list possible at this time"
            if not self.GetParent().FindWindowByName("components").IS_CONFIGURED:
                wx.MessageBox("Please configure components and retry")
        # Refresh existing choice boxes
        rows,cols = self.po_sizer.CalcRowsCols()

        for row in range(1,rows,1):
            for col in range(2,cols,1):
                try:
                    w = self.po_sizer.GetItem(row*cols + col).GetWindow()
                    if isinstance(w,PromptingComboBox):
                        w.Clear()
                        w.SetItems(self.component_frame_choices)
                except Exception , e:
                    print "Nothing to Refresh"




    def make_choice_list(self):
        self.dispense_choice_boxlist = []
        sorted_keys = self.masterdict.keys()
        sorted_keys.sort()
        for key in sorted_keys:
            self.choices.append(key)


    def make_plate(self,event):
        import os
        scrfile = None
        try :
            scrfile = open(os.path.join(os.environ["HOME"],"%s.scr" % str(self.GetParent().FindWindowByName("mpanel").file_name_text.GetValue())),"w")
            print "ALL OUTPUT TO DIR %s" % os.environ["HOME"]
        except KeyError , k :
            print "Not Linux/Mac I see"
            os.environ["HOME"] = os.path.join(os.environ["HOMEDRIVE"],os.environ["HOMEPATH"])
            scrfile = open(os.path.join(os.environ["HOME"],"%s.scr" % str(self.GetParent().FindWindowByName("mpanel").file_name_text.GetValue())),"w")
            print "ALL OUTPUT TO DIR %s" % os.environ["HOME"]

        scrfile.write("#!/usr/bin/python\n")
        scrfile.write("from gridder import masterplate,plate,component,buffercomponent\n")
        scrfile.write("mp = masterplate.Masterplate(%s)\n" % self.GetParent().FindWindowByName("mpanel").volttc.GetValue())

        myplate_setup = self.GetParent().FindWindowByName("platesetup").plate_setup_dict
        for key in myplate_setup.keys():
                com =  "p%s = plate.Plate(\"%s\",\"%s\",mp)\n" % ( key,myplate_setup[key][0],myplate_setup[key][1])
                print com
                scrfile.write(com)

        comppanel = self.GetParent().FindWindowByName("components").all_solutionsdict
        objdict = {}

        for key in sorted(comppanel.keys()):
            if key in self.GetParent().FindWindowByName("components").buffer_namedict.keys():
                cargs = ""
                cargs = ",".join(comppanel[key][1:])
                com = "c%s = buffercomponent.SimpleBuffer(\"%s\" , %s)\n" % (key,comppanel[key][0],cargs)
                print com
                scrfile.write(com)
                objdict[comppanel[key][0]] = "c%s " %  key
            else:
                cargs = ""
                cargs = ",".join(comppanel[key][1:])
                com = "c%s = component.Component(\"%s\" , %s)\n" % (key,comppanel[key][0],cargs)
                print com
                scrfile.write(com)
                objdict[comppanel[key][0]] = "c%s " %  key

        print self.plate_operations.keys()
        
        for i in self.plate_operations.keys():

            myobj = self.plate_operations[i]
            print myobj.argdict
            argstring = "" 
            args = ""
            textentries = sorted(myobj.argdict.keys())
            # Since event keys are negative numbers , to preserve argument order for functions we reverse the keys
            textentries.reverse()
            for sorted_key in textentries:
                argstring = argstring + myobj.argdict[sorted_key] + " "
            args = ",".join(argstring.split())
            component_keys = sorted(myobj.component_dict.keys())
            cstring = ""
            for sorted_component in component_keys:
                cstring = cstring +  objdict[myobj.component_dict[sorted_component]] + " "
            component_args = ",".join(cstring.split())
            print "$$$$$$$$$$", component_args
            com = "p%s.%s(%s,%s)\n" % (myobj.plate.split()[1],self.function_dict[myobj.op],component_args,args)
            print com
            scrfile.write(com)

        # Add the water Component to each script
        scrfile.write("water = component.Component(\"100.00 % Water\",100,100000)\n")
        added_water = []
        for i in self.plate_operations.keys():
            myobj = self.plate_operations[i]
            if myobj.plate not in added_water:
                scrfile.write("p%s.fill_water(water)\n" % myobj.plate.split()[1])
                added_water.append(myobj.plate)
            else:
                pass
#                print "filled water into" , added_water



##        scrfile.write("water = component.Component(\"100.00 % Water\",100,100000)\n")
#        scrfile.write("pwhole = plate.Plate(\"A1\",\"H12\",mp)\n")
#        scrfile.write("pwhole.fill_water(water)\n")
        scrfile.write("mp.printwellinfo()\n")
        scrfile.write("mp.makefileforformulatrix(\"%s\")\n" % str(os.path.join(os.environ["HOME"],"%s.dl.txt" % self.GetParent().FindWindowByName("mpanel").file_name_text.GetValue())))
        print "DISPENSE LIST OUTPUT to %s" % str(os.path.join(os.environ["HOME"],"%s.dl.txt" % self.GetParent().FindWindowByName("mpanel").file_name_text.GetValue()))
        scrfile.write("mp.printpdfhuman(\"%s\")\n" % str(os.path.join(os.environ["HOME"],"%s" % self.GetParent().FindWindowByName("mpanel").file_name_text.GetValue())))
        print "PDF FILE OUTPUT TO %s" % str(os.path.join(os.environ["HOME"],"%s" % self.GetParent().FindWindowByName("mpanel").file_name_text.GetValue()))

        scrfile.write("mp.printpdf(\"%s\")\n" % str((os.path.join(os.environ["HOME"],"%s_volumes" % self.GetParent().FindWindowByName("mpanel").file_name_text.GetValue()))))

        scrfile.close()
        execfile(os.path.join(os.environ["HOME"],"%s.scr" % str(self.GetParent().FindWindowByName("mpanel").file_name_text.GetValue())))


    


        
class MpPanel(wx.ScrolledWindow):

    def __init__(self,*args,**kwds):
        wx.ScrolledWindow.__init__(self,*args,**kwds)
        kwds["size"] = MYFRAMESIZE
        self.platevol_label = wx.StaticText(self,-1,"Plate Volume")
        self.volttc = wx.TextCtrl(self,-1,"2000")
        self.filenamelabel = wx.StaticText(self,-1,"Dispense file prefix")
        self.file_name_text = wx.TextCtrl(self,-1,"test")
        self.szr = wx.FlexGridSizer(2,2,10,10)
        self.szr.Add(self.platevol_label)
        self.szr.Add(self.volttc)
        self.szr.Add(self.filenamelabel)
        self.szr.Add(self.file_name_text)
        self.SetSizer(self.szr)
        self.szr.FitInside(self)
        self.Layout()


class OperationObject():

    def __init__(self,op=None,plate=None,args={},component_dict = {}):
        self.op = op
        self.plate = plate
        self.argdict =  args
        self.component_dict = component_dict
        
if __name__=="__main__":
    
    app = wx.PySimpleApp()
    maframe = MaFrame(parent=None,title="GZilla")
    plate_panel = PlatePanel(parent=maframe,name="platesetup")
    maframe.GetSizer().Add(plate_panel,5,wx.EXPAND)
    component_panel = ComponentPanel(parent=maframe,name="components")
    maframe.GetSizer().Add(component_panel,4,wx.ALIGN_BOTTOM|wx.EXPAND)
    plateoperations = PlateOperations(parent=maframe,name="plateop")
    maframe.GetSizer().Add(plateoperations,4,wx.ALIGN_BOTTOM|wx.EXPAND)
    holistic = MpPanel(maframe,name="mpanel")
    maframe.GetSizer().Add(holistic,1,wx.EXPAND)
    maframe.Layout()
    maframe.Show()
    # Debug using this tool
#    wx.lib.inspection.InspectionTool().Show()
    app.MainLoop()
