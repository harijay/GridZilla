#!/usr/bin/python
# To change this template, choose Tools | Templates
# and open the template in the editor.


import wx
import wx.lib.scrolledpanel  as myscrolledpanel
import wx.lib.inspection
MYFRAMESIZE = (787,321)
import sys
sys.path.append("/home/hari/gridder")
class MaFrame(wx.Frame):

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
    from gridder.masterplate import Masterplate
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
    ID_DELETE_PLATE = 111

    plate_customizer_dict = {1:("A1","H12"),2:("A1","D6","E1","H12"),3:("A1","","","","","H12"),4:("A1","D6","A7","D12","D1","H6","D7","H12")}

    def __init__(self,*args,**kwds):
        kwds["size"] = MYFRAMESIZE
        wx.ScrolledWindow.__init__(self,*args,**kwds)
##        self.SetBackgroundColour(wx.Colour(0,153,77)) # GREEN
#        self.SetBackgroundColour(wx.Colour(204,255,255)) # BABY BLUE
        self.SetBackgroundColour(wx.Colour(194,194,194))
#        self.platelabel = wx.StaticText(parent=self,id=-1,label="Plate %s" % self.num_subplates,size=(-1,-1),style=wx.ALIGN_CENTER)
#        self.text_ctrl_1 = wx.TextCtrl(parent=self, id=-1,value= "A1",size=(50,-1),validator=Validate_Plate_Coordinate())
#        self.text_ctrl_2 = wx.TextCtrl(parent=self,id=-1,value="A12",size=(50,-1),validator=Validate_Plate_Coordinate())
        self.plate_add_button = wx.Button(self,label="Add Plate")
        self.plate_display_button = wx.Button(self,label="DISPLAY Config")
        self.refresh_button = wx.Button(self,label="Refresh")
        self.SetScrollRate(3, 3)
        self.do_connections()
        self.do_layout()
        self.bind_delete_events()

    def do_layout(self):
        self.master_sizer = wx.FlexGridSizer(rows=-1, cols=3, hgap=10, vgap=5)
        self.master_sizer.Add(self.refresh_button)
        self.master_sizer.Add(self.plate_display_button)
        self.master_sizer.Add(self.plate_add_button)
        self.SetSizer(self.master_sizer)
        self.master_sizer.Layout()
        self.master_sizer.FitInside(self)

    def do_new_layout(self):
        print "lets see"
        self.plate_add_button = wx.Button(self,label="Add Plate")
        self.plate_display_button = wx.Button(self,label="DISPLAY Config")
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
        self.Bind(wx.EVT_BUTTON,self.display_plateconfig,self.plate_display_button)
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


        
 
        
    def display_plateconfig(self,event):
        from gridder.masterplate import Masterplate
        myplate = Masterplate(2000)
        scanned_plate_def = None
        # Local variable to identify plate corner
        count = 0
        platecorner = {1:"left corner",0:"right corner"}
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
                elif text not in myplate.ordered_keys:
                    wx.MessageBox("Please enter a plate coordinate between A1 and H12 for %s,%s" % (platecorner[flag],scanned_plate_def))
                else:
                    print "Got value:%s" % child.GetValue()
                
        event.Skip()

class plate_layout(object):
#    from gridder.component import Component
    grid_operations = []
    plate_choices = []
    components = []
    buffer_choices = []

    def __init__(self):
        pass
    
    def register_component(self,*input):
        pass



class  ComponentPanel(wx.ScrolledWindow):
    import csv
    userinput = plate_layout()
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

    def set_components(self,event):
        event.Skip()




if __name__=="__main__":

    app = wx.PySimpleApp()
    maframe = MaFrame(parent=None,title="GZilla")
    plate_panel = PlatePanel(parent=maframe)
    maframe.GetSizer().Add(plate_panel,5,wx.EXPAND)
    component_panel = ComponentPanel(parent=maframe)
    maframe.GetSizer().Add(component_panel,4,wx.ALIGN_BOTTOM|wx.EXPAND)
    maframe.Layout()
    maframe.Show()
    # Debug using this tool
    wx.lib.inspection.InspectionTool().Show()
    app.MainLoop()
