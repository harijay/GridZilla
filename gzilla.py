#!/usr/bin/python
# To change this template, choose Tools | Templates
# and open the template in the editor.

import gridder
import os.path
import wx
import wx.lib.scrolledpanel  as myscrolledpanel
#import wx.lib.inspection
MYFRAMESIZE = (1212,700)
import sys
import yaml
import subprocess
from gridder import *
from subprocess import CalledProcessError
# Imports to get py2exe and PyInstaller to work right
from reportlab.pdfbase import _fontdata_enc_winansi
from reportlab.pdfbase import _fontdata_enc_macroman
from reportlab.pdfbase import _fontdata_enc_standard
from reportlab.pdfbase import _fontdata_enc_symbol
from reportlab.pdfbase import _fontdata_enc_zapfdingbats
from reportlab.pdfbase import _fontdata_enc_pdfdoc
from reportlab.pdfbase import _fontdata_enc_macexpert
from reportlab.pdfbase import _fontdata_widths_courier
from reportlab.pdfbase import _fontdata_widths_courierbold
from reportlab.pdfbase import _fontdata_widths_courieroblique
from reportlab.pdfbase import _fontdata_widths_courierboldoblique
from reportlab.pdfbase import _fontdata_widths_helvetica
from reportlab.pdfbase import _fontdata_widths_helveticabold
from reportlab.pdfbase import _fontdata_widths_helveticaoblique
from reportlab.pdfbase import _fontdata_widths_helveticaboldoblique
from reportlab.pdfbase import _fontdata_widths_timesroman
from reportlab.pdfbase import _fontdata_widths_timesbold
from reportlab.pdfbase import _fontdata_widths_timesitalic
from reportlab.pdfbase import _fontdata_widths_timesbolditalic
from reportlab.pdfbase import _fontdata_widths_symbol
from reportlab.pdfbase import _fontdata_widths_zapfdingbats

class MaFrame(wx.Frame):
    plateobjects = []
    componentobjects = []
    
    PLATE_CONFIGURED = False
    IS_BEGUN = True
    dirtowriteto = None
    session_dict = {}
    def __init__(self,*args,**kwds):
        kwds["size"] = MYFRAMESIZE
        wx.Frame.__init__(self,*args, **kwds)
        self.CreateStatusBar(1,0)
        kwds["style"] = wx.THICK_FRAME
        self.frame_sizer = wx.BoxSizer(wx.VERTICAL)
        self.plate_panel = PlatePanel(parent=self,name="platesetup")
        self.frame_sizer.Add(self.plate_panel,4,wx.EXPAND)
        self.component_panel = ComponentPanel(parent=self,name="components")
        self.plateoperations = PlateOperations(parent=self,name="plateop")
        self.frame_sizer.Add(self.component_panel,5,wx.ALIGN_BOTTOM|wx.EXPAND)
        # The Operations panel
        self.holistic = MpPanel(self,name="mpanel")
        self.frame_sizer.Add(self.holistic,5,wx.EXPAND)
        self.frame_sizer.Add(self.plateoperations,5,wx.ALIGN_BOTTOM|wx.EXPAND)
        self.SetSizer(self.frame_sizer)
        self.filemenu = wx.Menu()
        rsf = self.filemenu.Append(-1,"&Read session file")
        readcomponent = self.filemenu.Append(-1,"Read &Component  from csv")
        savethesession = self.filemenu.Append(-1,"&Save session file")
        exit = self.filemenu.Append(-1,"E&xit")

        self.Bind(wx.EVT_MENU,self.read_session,rsf)
        self.Bind(wx.EVT_MENU,self.exit_gui,exit)
        self.Bind(wx.EVT_MENU,self.component_panel.get_and_parse_file,readcomponent)
        self.Bind(wx.EVT_MENU,self.save_session,savethesession)
        self.menubar = wx.MenuBar()
        self.menubar.Append(self.filemenu, "&File")
        self.SetMenuBar(self.menubar)
    
    def do_layout(self):
        self.Layout()
#        self.Fit()

    def exit_gui(self,event):
        # save timestamped session
        #print "Goycha"
        self.Close(1)
    # Event filed to save the session to file
    def save_session(self,event):
        try :
            if self.dirtowriteto == None :
                if os.environ.has_key("HOME"):
                    adialog = wx.DirDialog(self,message="Directory for dispense and session files",defaultPath=os.environ["HOME"])
                    adialog.ShowModal()
                    self.dirtowriteto = adialog.GetPath()
                    #print "ALL OUTPUT TO DIR %s" % self.dirtowriteto
                    session_file_name = os.path.join(self.dirtowriteto ,"%s.yaml" % str(self.holistic.file_name_text.GetValue()))
                    if os.path.exists(session_file_name):
                        wx.MessageBox("Overwriting session file %s" % session_file_name)
                    self.session_file = open(os.path.join(self.dirtowriteto ,"%s.yaml" % str(self.holistic.file_name_text.GetValue())),"w")
                else:
                    adialog = wx.DirDialog(self,message="Directory for dispense and session files",defaultPath=os.path.join(os.environ["HOMEDRIVE"],os.environ["HOMEPATH"]))
                    adialog.ShowModal()
                    #print "getting dialog"
                    self.dirtowriteto = adialog.GetPath()
                    session_file_name = os.path.join(self.dirtowriteto ,"%s.yaml" % str(self.holistic.file_name_text.GetValue()))
                    if os.path.exists(session_file_name):
                        wx.MessageBox("Overwriting session file %s" % session_file_name)
                    #print "ALL OUTPUT TO DIR %s" % self.dirtowriteto
                    self.session_file = open(os.path.join(self.dirtowriteto ,"%s.yaml" % str(self.holistic.file_name_text.GetValue())),"w")
            else :
                session_file_name = os.path.join(self.dirtowriteto ,"%s.yaml" % str(self.holistic.file_name_text.GetValue()))
                if os.path.exists(session_file_name) > 0:
                    wx.MessageBox("Overwriting session file %s" % session_file_name)
                self.session_file = open(os.path.join(self.dirtowriteto ,"%s.yaml" % str(self.holistic.file_name_text.GetValue())),"w")
            
        except KeyError , k :
            print "Not Linux/Mac/Windows I see"

        try:
            # TODO Track down which these operations are
            # Class PlatePanel
            self.FindWindowByName("platesetup").save_session(event,self.session_dict)
            # Class ComponentPanel
            self.FindWindowByName("components").save_session(event,self.session_dict)
            # Class PlateOperations
            self.FindWindowByName("plateop").save_session(event,self.session_dict)
            yaml.dump(self.session_dict,self.session_file)
            self.session_file.close()
        except Exception , e :
            sys.stderr.write(e.message)
            print "Error while saving session file:" , e
            wx.MessageBox("No Plates or Components or Operations Defined: Unable to write session File")
    

    def read_session(self,event):
        evt_delete = wx.CommandEvent(wx.wxEVT_COMMAND_BUTTON_CLICKED,self.plate_panel.refresh_button.GetId())
        self.plate_panel.delete_all_plates(evt_delete)
        try:
            self.session_dict = yaml.load(open(str(wx.FileSelector("Session YAML File \"*.yaml\" format","","","yaml","*.yaml")), "r"))
        except IOError, i:
            wx.MessageBox("No Such File")
            return None
        # Get Plate dict
        plates_dict = self.session_dict["plates"]
        masterplate_style = self.session_dict["style"]
        self.plate_panel.style = masterplate_style
        self.plate_panel.platestyle.SetSelection(self.plate_panel.styles.index(str(self.plate_panel.style)))
        if plates_dict is not None:
            sorted_plates = sorted(plates_dict.keys())
            for key in sorted_plates:
                #self.GetStatusBar().SetStatusText("Adding Plate %s" % key.split()[1])
                platelabel = wx.StaticText(self.plate_panel,id=-1,label=key, size=(-1,-1),style=wx.ALIGN_CENTER )
                text_ctrl_1 = wx.TextCtrl(self.plate_panel, -1,plates_dict[key][0],(50,-1))
                text_ctrl_2 = wx.TextCtrl(self.plate_panel,-1,plates_dict[key][1],(50,-1))
                self.plate_panel.master_sizer.Add(platelabel,1,wx.ALIGN_CENTER)
                self.plate_panel.master_sizer.Add(text_ctrl_1,1,wx.ALIGN_CENTER)
                self.plate_panel.master_sizer.Add(text_ctrl_2,1,wx.ALIGN_CENTER)
                #self.plate_panel.master_sizer.Layout()
                #self.sizer_top.Add(self.plate_add_button,1,wx.RIGHT|wx.ALIGN_BOTTOM,10)
                self.plate_panel.bind_delete_events()
                self.plate_panel.master_sizer.Layout()
    #            self.plate_panel.master_sizer.Fit(self)
                self.plate_panel.num_subplates = self.plate_panel.num_subplates + 1
                #self.do_layout()
                #self.GetParent().Fit()
                event = wx.CommandEvent(wx.wxEVT_COMMAND_BUTTON_CLICKED,self.plate_panel.plate_display_button.GetId())
                event.SetEventObject(self.plate_panel.plate_display_button)
                self.plate_panel.set_plate_config(event)
                event.Skip()
            self.do_layout()
        self.PLATE_CONFIGURED = self.session_dict["plate_config_state"]
        components_dict = self.session_dict["components"]
        sorted_components_dict_keys = sorted(components_dict.keys())
        # If there are components then cleanup
        if self.component_panel.IS_CONFIGURED  or ( len(self.component_panel.component_namedict.keys())  != 0) or (len(self.component_panel.buffer_namedict.keys())  != 0):
            delete_event = wx.CommandEvent(wx.wxEVT_COMMAND_BUTTON_CLICKED,self.component_panel.refresh_components_button.GetId())
            self.component_panel.delete_all_components(delete_event)

        if sorted_components_dict_keys is not None:
            for key in sorted_components_dict_keys:
                #print key
                componentlabel = wx.StaticText(parent=self.component_panel,id=-1,label=key ,style=wx.ALIGN_CENTER)
                text_ctrl_1 = wx.TextCtrl(self.component_panel, -1, components_dict[key][0],(-1,-1))
                text_ctrl_2 = wx.TextCtrl(self.component_panel,-1,components_dict[key][1],(-1,-1))
                text_ctrl_3 = wx.TextCtrl(self.component_panel,-1,components_dict[key][2],(-1,-1))
                self.component_panel.top_grid_sizer.Add(componentlabel,1,wx.ALIGN_LEFT|wx.ALIGN_CENTER)
                self.component_panel.top_grid_sizer.Add(text_ctrl_1,1,wx.ALIGN_CENTER)
                self.component_panel.top_grid_sizer.Add(text_ctrl_2,1,wx.ALIGN_CENTER)
                self.component_panel.top_grid_sizer.Add(text_ctrl_3,1,wx.ALIGN_CENTER)
                dummypanel1 = wx.Panel(self.component_panel,-1,(1,1))
                dummypanel1.SetBackgroundColour(wx.Colour(133,133,133))
                dummypanel2 = wx.Panel(self.component_panel,-1,(1,1))
                dummypanel2.SetBackgroundColour(wx.Colour(133,133,133))
                self.component_panel.top_grid_sizer.Add(dummypanel1)
                self.component_panel.top_grid_sizer.Add(dummypanel2)
                self.component_panel.num_components = self.component_panel.num_components + 1
#            self.Fit()
            self.do_layout()
        buffers_dict = self.session_dict["buffers"]
        sorted_buffers_dict_keys = sorted(buffers_dict.keys())
        if sorted_buffers_dict_keys is not None:
            for key in sorted_buffers_dict_keys:
                componentlabel = wx.StaticText(parent=self.component_panel,id=-1,label=key ,style=wx.ALIGN_CENTER)
                text_ctrl_1 = wx.TextCtrl(self.component_panel, -1,buffers_dict[key][0],(-1,-1))
                text_ctrl_2 = wx.TextCtrl(self.component_panel,-1,buffers_dict[key][1],(-1,-1))
                text_ctrl_3 = wx.TextCtrl(self.component_panel,-1,buffers_dict[key][2],(-1,-1))
                text_ctrl_4 = wx.TextCtrl(self.component_panel,-1,buffers_dict[key][3],(-1,-1))
                text_ctrl_5 = wx.TextCtrl(self.component_panel,-1,buffers_dict[key][4],(-1,-1))
                self.component_panel.top_grid_sizer.Add(componentlabel,1,wx.ALIGN_LEFT|wx.ALIGN_CENTER)
                self.component_panel.top_grid_sizer.Add(text_ctrl_1,1,wx.ALIGN_CENTER)
                self.component_panel.top_grid_sizer.Add(text_ctrl_2,1,wx.ALIGN_CENTER)
                self.component_panel.top_grid_sizer.Add(text_ctrl_3,1,wx.ALIGN_CENTER)
                self.component_panel.top_grid_sizer.Add(text_ctrl_4,1,wx.ALIGN_CENTER)
                self.component_panel.top_grid_sizer.Add(text_ctrl_5,1,wx.ALIGN_CENTER)
                self.component_panel.num_components = self.component_panel.num_components + 1
        event = wx.CommandEvent(wx.wxEVT_COMMAND_BUTTON_CLICKED,self.component_panel.set_component_button.GetId())
        event.SetEventObject(self.component_panel.set_component_button)
        self.component_panel.set_components(event)
        self.component_panel.bind_delete_events()
        self.component_panel.IS_CONFIGURED = self.session_dict["component_config_state"]
#        self.Fit()
        self.component_panel.top_grid_sizer.Layout()
        self.do_layout()
        operations_dict = self.session_dict["operations"]
        sorted_operations_dict_keys = sorted(operations_dict.keys())
        if len(self.plateoperations.plate_combobox_objects) != 0:
            self.plateoperations.delete_all_operations(event)
        if sorted_operations_dict_keys is not None:
            for key in sorted_operations_dict_keys:
                operation_row_dict = operations_dict[key]
                # If  plate then Create plate combobox: set selected to plate
                selected_plate = operation_row_dict["plate"]
                plate_choices = operation_row_dict["platelist"]
                currentrowpos,currentcolpos  = self.plateoperations.po_sizer.CalcRowsCols()
                new_platechoice_combobox = PromptingComboBox(self.plateoperations,"",choices=plate_choices, style=wx.CB_SORT,rowposition=currentrowpos)
                # Need to lambda the combobox so we can know which row the event came from
                new_platechoice_combobox.Bind(wx.EVT_COMBOBOX,lambda event,platecallercombobox=new_platechoice_combobox : self.plateoperations.on_plate_combobox_select(event,platecallercombobox))
                new_platechoice_combobox.Bind(wx.EVT_RIGHT_DOWN,lambda event,platecallercombobox=new_platechoice_combobox : self.plateoperations.delete_operation(event,platecallercombobox))
                try:
                    new_platechoice_combobox.GetChildren()[1].Bind(wx.EVT_RIGHT_DOWN,lambda event,platecallercombobox=new_platechoice_combobox : self.plateoperations.delete_operation(event,platecallercombobox))
                except:
                    pass
                new_dispense_combobox = PromptingComboBox(self.plateoperations,operation_row_dict["op"], choices=operation_row_dict["choices"], style=wx.CB_SORT,size=(280,-1),rowposition=currentrowpos)
                new_dispense_combobox.Bind(wx.EVT_COMBOBOX,lambda event,operationcombobox=new_dispense_combobox : self.plateoperations.on_operation_combobox_select(event,operationcombobox))
                self.plateoperations.plate_combobox_objects.append(new_platechoice_combobox)
                self.plateoperations.dispense_choice_boxlist.append(new_dispense_combobox)
                self.plateoperations.po_sizer.Add(new_platechoice_combobox,1,wx.EXPAND|wx.ALIGN_CENTER)
                self.plateoperations.po_sizer.Add(new_dispense_combobox,5,wx.EXPAND|wx.ALIGN_CENTER)
                new_platechoice_combobox.SetValue(selected_plate)
                for i in range(8):
                    dummypanel = wx.Panel(self,-1,size=(260,-1))
    #                dummypanel.SetBackgroundColour(wx.Colour(112,122,223))
                    self.plateoperations.po_sizer.Add(dummypanel,1,wx.EXPAND|wx.ALIGN_CENTER)
                self.plateoperations.do_init_layout()
                self.Layout()
                for item in self.plateoperations.plate_combobox_objects:
                    self.plateoperations.plate_id_mapper_dict[item.GetId()] = item.rowposition
                   # fire the events for plate selection and operation selection
                evt = wx.CommandEvent(wx.wxEVT_COMMAND_COMBOBOX_SELECTED, new_platechoice_combobox.GetId())
                evt.SetEventObject(new_platechoice_combobox)
                evt.SetInt(new_platechoice_combobox.choices.index(selected_plate))
                evt.SetString(selected_plate)
                self.plateoperations.on_plate_combobox_select(evt,new_platechoice_combobox)
                event_operation = wx.CommandEvent(wx.wxEVT_COMMAND_COMBOBOX_SELECTED,new_dispense_combobox.GetId())
                event_operation.SetString(operation_row_dict["op"])
                event_operation.SetEventObject(new_dispense_combobox)
                self.plateoperations.on_operation_combobox_select(event_operation,new_dispense_combobox)
                #print  "Plate Operations" , self.plateoperations.plate_operations
                
                # Create operation box regardless
                # for components in component_dict create a set of comboboxes with component choices , set the component_dict value
                # For arg dicts create textcontrols and set value to value in argdict array
                if operation_row_dict["component_dict"] == {} :
                    self.GetStatusBar().SetStatusText("Someething Wrong here: Check all operations in session file")
                    operation_row_dict["component_dict"][0] = ""   
                    
                sorted_compoennt_keys = sorted(operation_row_dict["component_dict"].keys())
                
                for component_stored_keys in sorted_compoennt_keys:
                    cbox = self.plateoperations.po_sizer.GetItem(currentrowpos*currentcolpos +  2 + component_stored_keys ).GetWindow()
                    cbox.SetValue(operation_row_dict["component_dict"][ component_stored_keys])
                    event = wx.CommandEvent(wx.wxEVT_COMMAND_COMBOBOX_SELECTED,cbox.GetId())
                    event.SetString(operation_row_dict["component_dict"][ component_stored_keys])
                    event.SetEventObject(cbox)
                    self.plateoperations.on_component_comobobox_select(event,cbox,currentrowpos,component_stored_keys)
                    
                sorted_arg_keys = sorted(operation_row_dict["argdict"].keys())[::-1]
                i = 0
                numcompoboxes = len( sorted_compoennt_keys)
            
                for key in sorted_arg_keys:
                    #print "Value",self.plateoperations.po_sizer.GetItem(currentrowpos*currentcolpos +  2 + numcompoboxes + i ).GetWindow().GetValue()
                    self.plateoperations.po_sizer.GetItem(currentrowpos*currentcolpos +  2 + numcompoboxes + i ).GetWindow().SetValue(r"%s" % operation_row_dict["argdict"][key])
                    #print r"Setting value to %s " % operation_row_dict["argdict"][key]
                    #print "Value",self.plateoperations.po_sizer.GetItem(currentrowpos*currentcolpos +  2 + numcompoboxes + i ).GetWindow().GetValue()
                    i = i + 1

class Validate_Plate_Coordinate(wx.PyValidator):


    def __init__(self,style):
        from gridder import masterplate
        from gridder.masterplate import Masterplate
        wx.PyValidator.__init__(self)
        self.myplate = Masterplate(2000,int(style))

    def Clone(self):
        return self.__class__(self)

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
    
    plate_customizer_dict = {96:{1:("A1","H12"),2:("A1","D12","E1","H12"),4:("A1","D6","A7","D12","E1","H6","E7","H12")},24:{1:("A1","D6"),2:("A1","B6","C1","D6")},384:{1:("A1","P24"),2:("A1","H24","I1","P24"),4:("A1","H12","A13","H24","I1","P12","I13","P24")}}
#    change_logger = []
    style = 96

    def __init__(self,*args,**kwds):
        kwds["size"] = MYFRAMESIZE
        wx.ScrolledWindow.__init__(self,*args,**kwds)
##        self.SetBackgroundColour(wx.Colour(0,153,77)) # GREEN
#        self.SetBackgroundColour(wx.Colour(204,255,255)) # BABY BLUE
        self.styles = ["24","96","384"]
        self.platestyle = wx.RadioBox(self,-1,choices=self.styles,style=wx.NO_BORDER|wx.RA_HORIZONTAL)
        self.platestyle.SetSelection(1)
        self.platestyle.Bind(wx.EVT_RADIOBOX,self.on_style_change)
        self.plate_add_button = wx.Button(self,label="Add Plate")
        self.plate_display_button = wx.Button(self,label="Configure Done")
        self.refresh_button = wx.Button(self,label="Refresh")
        self.SetBackgroundColour(wx.Colour(194,194,194))
        self.SetScrollRate(3, 3)
        self.do_connections()
        self.do_layout()
        self.bind_delete_events()
    
    def do_layout(self):
        self.master_sizer = wx.FlexGridSizer(rows=-1, cols=3, hgap=10, vgap=5)
        self.master_sizer.Add(self.platestyle)
        for i in range(2):
            dummypanel = wx.Panel(self,-1,(1,1))
            dummypanel.SetBackgroundColour(wx.Colour(194,194,194))
            self.master_sizer.Add(dummypanel)
        self.master_sizer.Add(self.refresh_button)
        self.master_sizer.Add(self.plate_add_button)
        self.master_sizer.Add(self.plate_display_button,wx.ALIGN_RIGHT)
        self.SetSizer(self.master_sizer)
        self.master_sizer.Layout()
        self.master_sizer.FitInside(self)

    def on_style_change(self,event):
        self.style = int(self.styles[self.platestyle.GetSelection()])
        #print "style changed to %s" % self.style
        if self.GetParent().PLATE_CONFIGURED:
            self.GetParent().PLATE_CONFIGURED = False
        
    def do_new_layout(self):
        self.platestyle = wx.RadioBox(self,-1,choices=self.styles,style=wx.NO_BORDER|wx.RA_HORIZONTAL)
        self.plate_add_button = wx.Button(self,label="Add Plate")
        self.platestyle.SetSelection(self.styles.index(str(self.style)))
        self.plate_display_button = wx.Button(self,label="Plate Configure Done")
        self.refresh_button = wx.Button(self,label="Refresh")
        self.do_connections()
        self.do_layout()
        self.bind_delete_events()
        
    
    def delete_all_plates(self,event):
        #print "Destroying all children"
        self.DestroyChildren()
        self.GetParent().plateobjects = []
        self.do_new_layout()
        self.num_subplates = 1
#        self.set_plateconfig_status_false(event)
        event.Skip()
        if self.GetParent().PLATE_CONFIGURED:
            self.GetParent().FindWindowByName("plateop").make_plate_choicetxtlist()
            self.GetParent().FindWindowByName("plateop").refresh_plate_choice_comboboxes()
            self.GetParent().PLATE_CONFIGURED = False

            
    def do_connections(self):
        self.platestyle.Bind(wx.EVT_RADIOBOX,self.on_style_change)
        self.Bind(wx.EVT_BUTTON,self.add_plate_def,self.plate_add_button)
        self.Bind(wx.EVT_BUTTON,self.set_plate_config,self.plate_display_button)
	self.Bind(wx.EVT_BUTTON,self.delete_all_plates,self.refresh_button)
#        self.Bind(wx.EVT_MOUSEWHEEL, self.on_mousewheel)
    
    def on_mousewheel(self,event):
        self.Refresh()
        self.SetFocusIgnoringChildren()
        #print "refreshed"
        event.Skip()

    def add_plate_def(self,event):
        self.GetParent().GetStatusBar().SetStatusText("Adding Plate %s" % self.num_subplates)
        platelabel = wx.StaticText(parent=self,id=-1,label="Plate %s" % self.num_subplates , size=(-1,-1),style=wx.ALIGN_CENTER )
        text_ctrl_1 = wx.TextCtrl(self, -1, "",(50,-1))
        text_ctrl_2 = wx.TextCtrl(self,-1,"",(50,-1))
        self.master_sizer.Add(platelabel,1,wx.ALIGN_CENTER)
        self.master_sizer.Add(text_ctrl_1,1,wx.ALIGN_CENTER)
        self.master_sizer.Add(text_ctrl_2,1,wx.ALIGN_CENTER)
        self.master_sizer.Layout()
        #self.sizer_top.Add(self.plate_add_button,1,wx.RIGHT|wx.ALIGN_BOTTOM,10)
        
        self.has_config()
        self.bind_delete_events()
        
        self.master_sizer.Layout()
        self.master_sizer.Fit(self)
        
        self.num_subplates = self.num_subplates + 1
        self.GetParent().do_layout()
        #self.GetParent().Fit()
        # We dont want add plate to mess with configuration
        # self.set_plateconfig_status_false(event)
        event.Skip()

    
    def bind_delete_events(self):
        import re
        plate_pattern = re.compile("Plate \d+")
        for child in self.GetChildren():
            if isinstance(child, wx.StaticText):
                if plate_pattern.search(child.GetLabel()):
                    child.Bind(wx.EVT_RIGHT_DOWN, self.show_plate_delete_choice)

    def has_config(self):
        # Local variable to run along plate config tuple using self.plate_customizer_dict[self.num_subplates][scanner]
        scanner = 0
        # We  dont want to auto_fill if some configuration has already been established
        if not self.GetParent().PLATE_CONFIGURED:
            for child in self.GetChildren():
                if isinstance(child, wx.TextCtrl):
                    try:
                        child.SetValue(self.plate_customizer_dict[self.style][self.num_subplates][scanner])
                        self.GetParent().GetStatusBar().SetStatusText("settingplate boundaries automatic done")
                    except KeyError , e:
                        pass
                    scanner = scanner + 1
        else:
            # We  dont want to auto_fill if some configuration has already been established
            pass

#
#    def on_right_click(self,event):
#        self.PopupMenu(self.menu)

    def get_index(self,pos):
        count = 0
        for i in self.master_sizer.GetChildren():
            ipos = i.GetPosition()
            if ipos == pos:
                return count
            count = count + 1

    def delete_called_plate(self,event,caller):
        # Get row number of firing event
#        delpos = self.master_sizer.GetItem(caller).GetPosition()
        delpos = caller.GetPosition()
        index = self.get_index(delpos)
        w1 = self.master_sizer.GetItem(index).GetWindow()
        w2 = self.master_sizer.GetItem(index + 1 ).GetWindow()
        w3 = self.master_sizer.GetItem(index + 2).GetWindow()
        w1.Destroy()
        w2.Destroy()
        w3.Destroy()
        self.master_sizer.Layout()
#        row,col = self.master_sizer.CalcRowsCols()
#        for elem in range(index,row*col,1):
#            w = self.master_sizer.GetItem(elem).GetWindow()
#            if isinstance(w,wx.StaticText):
#                pval = w.GetLabel().split()
#                w.SetLabel(" ".join([pval[0] , "%s" % (int(pval[1])- 1)]))
#        self.num_subplates = self.num_subplates - 1
#        self.set_plateconfig_status_false(event)
        if self.GetParent().PLATE_CONFIGURED:
#            self.change_logger.append(event.GetId())
            self.set_plate_config(event)
            self.GetParent().FindWindowByName("plateop").make_plate_choicetxtlist()
            self.GetParent().FindWindowByName("plateop").refresh_plate_choice_comboboxes()
        


        
    def show_plate_delete_choice(self,event):
        mycaller = event.GetEventObject()
        menu = wx.Menu()
        delete_entry = menu.Append(-1,"&Delete Plate")
        self.Bind(wx.EVT_MENU,lambda event,caller=mycaller:self.delete_called_plate(event,caller=mycaller),delete_entry)
        self.PopupMenu(menu)
        


        
#    def display_change_warning(self,event):
#        if event.GetId() not in self.change_logger:
#            msg = wx.MessageBox("Please Configure Plates and then check configure to propagate changes")
#            self.change_logger.append(event.GetId())
#            event.Skip()
#        else:
#            event.Skip()

    def set_plateconfig_status_false(self,event):
        if self.GetParent().PLATE_CONFIGURED:
            self.GetParent().PLATE_CONFIGURED = False
            event.Skip()
    
    def set_plate_config(self,event):
        self.GetParent().plateobjects = []
        from gridder.masterplate import Masterplate
        # Servant plate object to check user input
        myplate = Masterplate(2000,self.style)
        # Local variable to identify plate corner
        scanned_plate_def = None
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
                    wx.MessageBox("Please enter a plate coordinate between %s%s and %s%s for %s,%s" % (myplate.alphas[0],myplate.nums[0],myplate.alphas[-1],myplate.nums[-1],platecorner[flag],scanned_plate_def))
                    self.GetParent().PLATE_CONFIGURED = False
                    break
                elif text not in myplate.ordered_keys:
                    wx.MessageBox("Please enter a plate coordinate between %s%s and %s%s for %s,%s" % (myplate.alphas[0],myplate.nums[0],myplate.alphas[-1],myplate.nums[-1],platecorner[flag],scanned_plate_def))
                    self.GetParent().PLATE_CONFIGURED = False
                    break
                else:
                    if scanned_plate_def not in self.GetParent().plateobjects:
                        self.GetParent().plateobjects.append(scanned_plate_def)

            childcount = childcount + 1
            # If it has scanned through all the children in plateop panel without breaking out of this set_plate_config
            if childcount == max :
                self.GetParent().PLATE_CONFIGURED = True
                self.GetParent().FindWindowByName("plateop").make_plate_choicetxtlist()
                self.GetParent().FindWindowByName("plateop").refresh_plate_choice_comboboxes()
        self.plate_setup_dict = {}
        rows,cols = self.master_sizer.CalcRowsCols()
        for row in range(2,rows,1):
#                print "p%s = plate.Plate(\"%s\",\"%s\")" % ( row,self.master_sizer.GetItem(cols*row + 1).GetWindow().GetValue() , self.master_sizer.GetItem(cols*row + 2).GetWindow().GetValue())
            win0 = self.master_sizer.GetItem(cols*row).GetWindow()
            win1 = self.master_sizer.GetItem(cols*row + 1).GetWindow()
            win2 = self.master_sizer.GetItem(cols*row + 2).GetWindow()
            self.plate_setup_dict[win0.GetLabel().split()[1]] = [win1.GetValue(),win2.GetValue()]
            # If user changes anything from now on this invalidates plate_config status
            win1.Bind(wx.EVT_TEXT,self.set_plateconfig_status_false)
            win2.Bind(wx.EVT_TEXT,self.set_plateconfig_status_false)
        event.Skip()
    
    def save_session(self,event,session_dict):
        tmp_dict = {}
        for platespec in self.plate_setup_dict.keys():
            tmp_dict["Plate %s" % platespec]=self.plate_setup_dict[platespec]
            
        session_dict["plates"] = tmp_dict
        session_dict["style"] = self.style
        #print  yaml.dump(self.plate_setup_dict)
        #print self.plate_setup_dict
    
#
#            platelabel = wx.StaticText(parent=self,id=-1,label="Plate %s" % self.num_subplates , size=(-1,-1),style=wx.ALIGN_CENTER )
#
#            text_ctrl_1 = wx.TextCtrl(self, -1, "A1",(50,-1))
#            text_ctrl_2 = wx.TextCtrl(self,-1,"B5",(50,-1))
#            self.master_sizer.Add(platelabel,1,wx.ALIGN_CENTER)
#            self.master_sizer.Add(text_ctrl_1,1,wx.ALIGN_CENTER)
#            self.master_sizer.Add(text_ctrl_2,1,wx.ALIGN_CENTER)
#            self.master_sizer.Layout()
#        self.bind_delete_events()


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
        self.top_grid_sizer = wx.FlexGridSizer(rows=-1, cols=6, hgap=20, vgap=10)
        self.fileselector_button = wx.Button(parent=self,id=-1,label="Component File")
        self.add_component_button = wx.Button(parent=self,id=-1,label="Add Component")
        self.add_buffer_button = wx.Button(parent=self,id=-1,label="Add Buffer")
        self.set_component_button = wx.Button(parent=self,id=-1,label="Configure done")
        self.refresh_components_button = wx.Button(parent=self,id=-1,label="Delete All Components")
        self.top_grid_sizer.Add(self.fileselector_button)
        self.top_grid_sizer.Add(self.add_component_button)
        self.top_grid_sizer.Add(self.add_buffer_button)
        dummy_panel = wx.Panel(self,-1,(1,1))
        dummy_panel.SetBackgroundColour(wx.Colour(133,133,133))
        self.top_grid_sizer.Add(dummy_panel)
        self.top_grid_sizer.Add(self.refresh_components_button)
        self.top_grid_sizer.Add(self.set_component_button)
        self.component_number_slot = wx.StaticText(parent=self,id=-1,label="",size=(-1,-1))
        self.component_name_label = wx.StaticText(self, -1, "Component Name",style=wx.ALIGN_CENTER)
        self.component_conc_label = wx.StaticText(self,-1,"Concentration",style=wx.ALIGN_CENTER)
        self.component_volume_label = wx.StaticText(self,-1,u"Volume in \xb5l",style=wx.ALIGN_CENTER)
        self.component_ph_label = wx.StaticText(self,-1,"pH",style=wx.ALIGN_CENTER)
        self.component_pka_label = wx.StaticText(self,-1,"pKa",style=wx.ALIGN_CENTER)
        self.top_grid_sizer.Add(self.component_number_slot,1,wx.ALIGN_CENTER)
        self.top_grid_sizer.Add(self.component_name_label,1,wx.ALIGN_CENTER)
        self.top_grid_sizer.Add(self.component_conc_label,1,wx.ALIGN_CENTER)
        self.top_grid_sizer.Add(self.component_volume_label,1,wx.ALIGN_CENTER)
        self.top_grid_sizer.Add(self.component_ph_label,1,wx.ALIGN_CENTER)
        self.top_grid_sizer.Add(self.component_pka_label,1,wx.ALIGN_CENTER)
        self.do_connections()
        self.bind_delete_events()
        self.SetScrollRate(3, 3)
        self.do_layout()


    
    def do_connections(self):
        self.Bind(wx.EVT_BUTTON , self.get_and_parse_file,self.fileselector_button)
        self.Bind(wx.EVT_BUTTON,self.manual_add_component,self.add_component_button)
        self.Bind(wx.EVT_BUTTON,self.manual_add_buffer,self.add_buffer_button)
        self.Bind(wx.EVT_BUTTON,self.set_components,self.set_component_button)
        self.Bind(wx.EVT_BUTTON,self.delete_all_components,self.refresh_components_button)

    def bind_delete_events(self):
        import re
        component_pattern = re.compile("Component\s+\d")
        buffer_pattern = re.compile("Buffer\s+\d")
        for child in self.GetChildren():
            if isinstance(child, wx.StaticText):
#                print child.GetLabel()
                if component_pattern.search(child.GetLabel()) or buffer_pattern.search(child.GetLabel()) :
                    child.Bind(wx.EVT_RIGHT_DOWN ,self.on_right_click)

    
    def on_right_click(self,event):
        mycaller = event.GetEventObject()
        menu = wx.Menu()
        delete_menu_item=menu.Append(-1,"Delete Component")
        self.Bind(wx.EVT_MENU,lambda caller: self.delete_component(event,caller=mycaller) )
        self.PopupMenu(menu)
    
    def get_index(self,pos):
        count = 0
        for i in self.top_grid_sizer.GetChildren():
            ipos = i.GetPosition()
            if ipos == pos:
                return count
            count = count + 1

    def delete_component(self,event,caller):
        # Implement Component Deletion"
                # Get row number of firing event
        # TODO remove this component from the gridder well component dictionary since we are now using execfile
        print "Before Deletion of compound gridder.well.Well.wellcomponentlist.componentfactory.keys()", len(gridder.well.Well.wellcomponentlist.componentfactory.keys())
        delpos = self.top_grid_sizer.GetItem(caller).GetPosition()
        index = self.get_index(delpos)
        #print index
        widget_bin = []
        rows,cols = self.top_grid_sizer.CalcRowsCols()

        for i in range(index,index+cols,1):
            w = self.top_grid_sizer.GetItem(i).GetWindow()
            widget_bin.append(w)
        
        #print len(widget_bin)
        for item in widget_bin:
            item.Destroy()

        newrows,newcols = self.top_grid_sizer.CalcRowsCols()
        for elem in range(index,newrows*newcols,1):
            w = self.top_grid_sizer.GetItem(elem).GetWindow()
            if isinstance(w,wx.StaticText):
                pval = w.GetLabel().split()
                w.SetLabel(" ".join([pval[0] , "%s" % (int(pval[1])- 1)]))
        self.num_components = self.num_components - 1
        self.top_grid_sizer.Layout()
        self.GetParent().Layout()
        # Re initialize the component factory
        #TODO remove only the specific object. But wiping dict empty also works
        gridder.well.Well.wellcomponentlist.componentfactory = {}
        print "After Deletion of all components from gridder library",  len(gridder.well.Well.wellcomponentlist.componentfactory.keys())
        if self.IS_CONFIGURED:
            #print self.all_solutionsdict.pop(index/6)
            if self.buffer_namedict.has_key(index/6):
                self.buffer_namedict.pop(index/6)
            self.set_components(event)
    
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
            componentlabel = wx.StaticText(parent=self,id=-1,label="Component %s" % self.num_components ,style=wx.ALIGN_CENTER)
            text_ctrl_1 = wx.TextCtrl(self, -1, component_array[0],(-1,-1))
            text_ctrl_2 = wx.TextCtrl(self,-1,component_array[1],(-1,-1))
            text_ctrl_3 = wx.TextCtrl(self,-1,component_array[2],(-1,-1))
            self.top_grid_sizer.Add(componentlabel,1,wx.ALIGN_LEFT|wx.ALIGN_CENTER)
            self.top_grid_sizer.Add(text_ctrl_1,1,wx.ALIGN_CENTER)
            self.top_grid_sizer.Add(text_ctrl_2,1,wx.ALIGN_CENTER)
            self.top_grid_sizer.Add(text_ctrl_3,1,wx.ALIGN_CENTER)
            dummypanel1 = wx.Panel(self,-1,(1,1))
            dummypanel1.SetBackgroundColour(wx.Colour(133,133,133))
            dummypanel2 = wx.Panel(self,-1,(1,1))
            dummypanel2.SetBackgroundColour(wx.Colour(133,133,133))
            self.top_grid_sizer.Add(dummypanel1)
            self.top_grid_sizer.Add(dummypanel2)


        
        if len(component_array) == 5:
            componentlabel = wx.StaticText(parent=self,id=-1,label="Buffer %s" % self.num_components ,style=wx.ALIGN_CENTER)
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

    def delete_all_components(self,event):
#        print "Destroying all components"
        self.DestroyChildren()
        rows,cols = self.top_grid_sizer.CalcRowsCols()
#        print "ROWOOOW",rows,cols
        self.fileselector_button = wx.Button(parent=self,id=-1,label="Component File")
        self.add_component_button = wx.Button(parent=self,id=-1,label="Add Component")
        self.add_buffer_button = wx.Button(parent=self,id=-1,label="Add Buffer")
        self.set_component_button = wx.Button(parent=self,id=-1,label="Configure done")
        self.refresh_components_button = wx.Button(parent=self,id=-1,label="Delete All Components")
        self.top_grid_sizer.Add(self.fileselector_button)
        self.top_grid_sizer.Add(self.add_component_button)
        self.top_grid_sizer.Add(self.add_buffer_button)
        dummy_panel = wx.Panel(self,-1,(1,1))
        dummy_panel.SetBackgroundColour(wx.Colour(133,133,133))
        self.top_grid_sizer.Add(dummy_panel)
        self.top_grid_sizer.Add(self.refresh_components_button)
        self.top_grid_sizer.Add(self.set_component_button)
        self.component_number_slot = wx.StaticText(parent=self,id=-1,label="",size=(-1,-1))
        self.component_name_label = wx.StaticText(self, -1, "Component Name",style=wx.ALIGN_CENTER)
        self.component_conc_label = wx.StaticText(self,-1,"Concentration",style=wx.ALIGN_CENTER)
        self.component_volume_label = wx.StaticText(self,-1,u"Volume in \xb5l",style=wx.ALIGN_CENTER)
        self.component_ph_label = wx.StaticText(self,-1,"pH",style=wx.ALIGN_CENTER)
        self.component_pka_label = wx.StaticText(self,-1,"pKa",style=wx.ALIGN_CENTER)
        self.top_grid_sizer.Add(self.component_number_slot,1,wx.ALIGN_CENTER)
        self.top_grid_sizer.Add(self.component_name_label,1,wx.ALIGN_CENTER)
        self.top_grid_sizer.Add(self.component_conc_label,1,wx.ALIGN_CENTER)
        self.top_grid_sizer.Add(self.component_volume_label,1,wx.ALIGN_CENTER)
        self.top_grid_sizer.Add(self.component_ph_label,1,wx.ALIGN_CENTER)
        self.top_grid_sizer.Add(self.component_pka_label,1,wx.ALIGN_CENTER)
        self.do_connections()
        self.bind_delete_events()
        self.top_grid_sizer.Layout()
        self.num_components = 1
        # Old status since we are using set_components to clean stuff up elsewhere
        status = self.IS_CONFIGURED
        self.set_components(event)
        # reset status to old status
        self.IS_CONFIGURED = status
        

      
            
    def set_components(self,event):
        import re
        spaces = re.compile("\s+")
        rows,cols = self.top_grid_sizer.CalcRowsCols()
        self.all_solutionsdict.clear()
        self.component_namedict.clear()
        self.buffer_namedict.clear()
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
#                    print "Added component num :  %d , Name : %s , Concentration : %s Volume : %s " % tuple([rownum] + itemvals)

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
        
    def save_session(self,event,session_dict):
        #print self.component_namedict.keys()
        tmp_comp_dict = {}
        tmp_buffer_dict = {}
        for key in self.component_namedict.keys():
            displaykey = int(key) -1
            tmp_comp_dict["Component %s" % displaykey] = self.component_namedict[key]
        session_dict["component_config_state"] = self.IS_CONFIGURED
        session_dict["components"] = tmp_comp_dict
        for key in self.buffer_namedict.keys():
            tmp_buffer_dict["Buffer %s" % str(key)] = self.buffer_namedict[key]
        session_dict["buffers"] = tmp_buffer_dict
        #print yaml.dump(self.component_namedict)
        #print yaml.dump(self.buffer_namedict)
        event.Skip()


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
        event.Skip()
        return
        ## if self.ignoreEvtText:
        ##     self.ignoreEvtText = False
        ##     # Added to Fix PromptingCombobox bug
        ##     event.Skip()
        ## currentText = event.GetString().upper()
        ## found = False
        ## for choice in self.choices :
        ##     if choice.startswith(currentText):
        ##         self.ignoreEvtText = True
        ##         self.SetValue(choice)
        ##         self.SetInsertionPoint(len(currentText))
        ##         self.SetMark(len(currentText), len(choice))
        ##         found = True
        ##         # Added to fix PromptingCombobox bug
        ##         # http://trac.wxwidgets.org/ticket/11122
        ##         event.Skip()
        ## if not found:
        ##     event.Skip()

class PlateOperations(wx.ScrolledWindow):
    #dict structure is an operations followed by a dict of arguments
    function_dict = {"Component To Single Row":"push_component_to_row_on_masterplate",\
    "Component To Single Column":"push_component_to_column_on_masterplate","Add To Entire Plate":"push_component_uniform_to_masterplate",\
    "Gradient Along X":"gradient_along_x","Gradient Along Y":"gradient_along_y","Gradient List Along X":"gradientlist_along_x",\
    "Gradient List Along Y":"gradientlist_along_y","Component To Multiple Rows":"push_component_rowlist",\
    "Component To Multiple Columns":"push_component_columnlist","Buffer pH Gradient Along X":"ph_gradient_alongx","Buffer pH Gradient Along Y":"ph_gradient_alongy",\
    "Buffer pH List Along X":"ph_list_alongx","Buffer pH List Along Y":"ph_list_alongy","Make To 100 Along X":"maketo100_alongx",\
    "Make To 100 Along Y":"maketo100_alongy","Make To 100 List X":"maketo100_listx","Make To 100 List Y":"maketo100_listy","Gradient List to Single Row":"gradient_list_to_row","Gradient List to Single Column":"gradient_list_to_column",\
    "Gradient List to Multiple Rows":"gradient_list_to_multiple_rows","Gradient List to Multiple Columns":"gradient_list_to_multiple_columns",\
    "Buffer single pH to row or rows":"buffer_single_ph_to_row_or_rows","Buffer single pH to column or columns":"buffer_single_ph_to_column_or_columns",
    "Buffer pH list to single row":"buffer_multiple_phs_to_single_row","Buffer pH list to single column":"buffer_multiple_phs_to_single_column"}
    masterdict = {'Gradient List Along X': ['Component', 'LISTVALS'], 'Gradient List Along Y': ['Component', 'LISTVALS'], 'Make To 100 Along X': ['Component', 'Component', 'FinalConc', 'FinalConcStartComponent1', 'FinalConcStopComponent1'], 'Make To 100 Along Y': ['Component', 'Component', 'FinalConc', 'FinalConcStartComponent1', 'FinalConcStopComponent1'], 'Add To Entire Plate': ['Component', 'FinalConc'], \
                  'Make To 100 List X': ['Component', 'Component', 'FinalConc', 'LISTVALS'], 'Component To Single Column': ['Component', 'FinalConc', 'NUM'], 'Buffer pH List Along Y': ['Buffer', 'Buffer', 'FinalConc', 'LISTVALS'],\
                  'Buffer pH List Along X': ['Buffer', 'Buffer', 'FinalConc', 'LISTVALS'], 'Component To Single Row': ['Component', 'FinalConc', 'ALPHA'], 'Buffer pH Gradient Along Y': ['Buffer', 'Buffer', 'FinalConc', 'pHSTART', 'pHSTOP'], \
                  'Buffer pH Gradient Along X': ['Buffer', 'Buffer', 'FinalConc', 'pHSTART', 'pHSTOP'], 'Component To Multiple Rows': ['Component', 'FinalConc', 'LISTROWS'], 'Component To Multiple Columns': ['Component', 'FinalConc', 'LISTCOLS'], \
                  'Make To 100 List Y': ['Component', 'Component', 'FinalConc', 'LISTVALS'], 'Gradient Along Y': ['Component', 'FinalConcStart', 'FinalConcStop'], 'Gradient Along X': ['Component', 'FinalConcStart', 'FinalConcStop'],\
                  "Gradient List to Single Row" :['Component','Concentration_List','row alphabet'],"Gradient List to Single Column" : ['Component','Concentration_List','column_number'],\
                  "Gradient List to Multiple Rows":['Component','Concentration_List',"Row Alpha List"],"Gradient List to Multiple Columns":["Component","Concentration_List","Column Number List"],\
                  "Buffer single pH to row or rows":['Buffer',"Buffer","FinalConc","pH desired","""["A"] or ["A","D"]"""],\
                  "Buffer single pH to column or columns":['Buffer',"Buffer","FinalConc","pH desired","""[1] or [1,4]"""],\
                  "Buffer pHList to single row":["Buffer","Buffer","FinalConc","pHList","A"], "Buffer pHlist to single column":["Buffer","Buffer","FinalConc","pHList","3"]}


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
#        self.add_op_button = wx.Button(self,label="Add Operation")
#        self.make_plate_button = wx.Button(self,label="Make Plate")
#        self.Bind(wx.EVT_BUTTON,self.add_operation,self.add_op_button)
#        self.Bind(wx.EVT_BUTTON,self.make_plate,self.make_plate_button)

        self.SetScrollRate(3,3)
        self.po_sizer = wx.FlexGridSizer(-1,10,20,20)
        self.po_sizer.Add(wx.Panel(self,-1,size=(260,-1)))
        self.po_sizer.Add(wx.Panel(self,-1,size=(260,-1)))
#        self.po_sizer.Add(self.add_op_button)
#        self.po_sizer.Add(self.make_plate_button)

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
#        i = 0
#        for item in self.plate_combobox_objects:
#            # Simply setting the combobox_object.choice to new choices did not do it
#            # One has to clear the present plate choices and repopulate the list
#            item.SetItems(self.platelist)
#
        rows,cols = self.po_sizer.CalcRowsCols()

        for row in range(1,rows,1):
            for col in range(0,cols,1):
                try:
                    w = self.po_sizer.GetItem(row*cols + col).GetWindow()
                    if w in self.plate_combobox_objects:
                        selected = None
                        try :
                            selected = w.GetValue()
                        except :
                            selected = ""
                            pass
                        w.Clear()
                        w.SetItems(self.platelist)
                        if selected in self.platelist:
                            w.SetValue(selected)
                        else:
                            w.SetValue("")
                except Exception , e:
                    pass
                    #print "Nothing to Refresh"

           

    def on_plate_combobox_select(self,event,platecallercombobox):
#        print "selected plate combobox event %s %s from grid row %d" % (event.GetString(),event.GetId(),platecallercombobox.rowposition)
        if platecallercombobox.rowposition in self.plate_operations.keys():
            myopobject = self.plate_operations[platecallercombobox.rowposition]
        else:
            myopobject = OperationObject()
            self.plate_operations[platecallercombobox.rowposition] = myopobject 
        myopobject.plate = event.GetString()


    def on_operation_combobox_select(self,event,operationcombobox):

        if not self.GetParent().FindWindowByName("components").IS_CONFIGURED:
            self.make_component_choice_list()

#        print "selected Operation combobox event %s %s from rid row %d " % (event.GetString(),event.GetId(),operationcombobox.rowposition)
        rows,cols = self.po_sizer.CalcRowsCols()
#        print "#######################"
#        for i in range(rows*cols):
#            print self.po_sizer.GetItem(i).GetWindow()
        for counter in range(operationcombobox.rowposition*cols + 2,operationcombobox.rowposition*cols + cols,1):
            oldwindow = self.po_sizer.GetItem(counter).GetWindow()
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
               # print "gettingsadadfadasd"
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
#                print self.buffer_frame_choices
                newcombo2 = PromptingComboBox(self,"",choices=self.buffer_frame_choices,rowposition=operationcombobox.rowposition)
                self.Bind(wx.EVT_COMBOBOX,lambda event, caller=newcombo2,row=operationcombobox.rowposition,column=argcount :self.on_component_comobobox_select(event,caller,row,column),newcombo2 )
                if self.po_sizer.GetItem(int(operationcombobox.rowposition)*10  + 2 + argcount ):
                    #print "replace called on posn %d column %d " % (int(operationcombobox.rowposition)*int(10) + int(2) + argcount,argcount )
                    oldwindow = self.po_sizer.GetItem(int(operationcombobox.rowposition)*int(10) + int(2) + argcount).GetWindow()
                    self.po_sizer.Replace(oldwindow , newcombo2)
                    oldwindow.Destroy()
                    self.Layout()


                else:
                    #print " Fresh item insertion attempt"
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
        # This event is not bound properly. Does not get called everytime
#        print "aefrgaergfertqert",event.GetString(),caller,row
        myobj = self.plate_operations[row]
        myobj.component_dict[column] = event.GetString()
        event.Skip()

    def add_operation(self,event):
        if self.GetParent().PLATE_CONFIGURED :
            if self.GetParent().FindWindowByName("components").IS_CONFIGURED:
                mynewchoice = self.platelist
                # Hardcode row position into object for script generation purposes
                currentrowpos,currentcolpos  = self.po_sizer.CalcRowsCols()
#                print "MBCJMDBCJDCB" ,  currentrowpos,currentcolpos
                new_platechoice_combobox = PromptingComboBox(self,"",choices=mynewchoice, style=wx.CB_SORT,rowposition=currentrowpos)
                # Need to lambda the combobox so we can know which row the event came from
                new_platechoice_combobox.Bind(wx.EVT_COMBOBOX,lambda event,platecallercombobox=new_platechoice_combobox : self.on_plate_combobox_select(event,platecallercombobox))
                new_platechoice_combobox.Bind(wx.EVT_RIGHT_DOWN,lambda event,platecallercombobox=new_platechoice_combobox : self.delete_operation(event,platecallercombobox))
                try:
                    new_platechoice_combobox.GetChildren()[1].Bind(wx.EVT_RIGHT_DOWN,lambda event,platecallercombobox=new_platechoice_combobox : self.delete_operation(event,platecallercombobox))
                except:
                    pass
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
#                print self.plate_combobox_objects
                for item in self.plate_combobox_objects:
                    self.plate_id_mapper_dict[item.GetId()] = item.rowposition
            else:
                wx.MessageBox("No Components: Please Configure components and then add operations")
        else:
            wx.MessageBox("No Plates: Please Set Plate COnfig and then Add operation")
    
    def  perform_delete(self,event,platecallercombobox):
        rows,cols = self.po_sizer.CalcRowsCols()
        dustbin = []
        for i in range(platecallercombobox.rowposition*cols,platecallercombobox.rowposition*cols + cols,1):
            widget = self.po_sizer.GetItem(i).GetWindow()
            dustbin.append(widget)
#            print self.plate_id_mapper_dict
#            print self.plate_operations
            if self.plate_operations.has_key(platecallercombobox.rowposition):
                self.plate_operations.pop(platecallercombobox.rowposition)
            if widget in self.plate_combobox_objects:
                self.plate_combobox_objects.remove(widget)
                self.plate_id_mapper_dict.pop(widget.GetId())
            if widget in self.dispense_choice_boxlist:
                self.dispense_choice_boxlist.remove(widget)
        #print dustbin,len(dustbin)
        for w in dustbin:
            dummypanel = wx.Panel(self,-1,(1,1))
            self.po_sizer.Replace(w , dummypanel)
            self.po_sizer.Detach(w)
            w.Destroy()
        #print self.po_sizer.CalcRowsCols()
        self.po_sizer.Layout()

    def delete_operation(self,event,platecallercombobox):
        menu = wx.Menu()
        delete_item = menu.Append(-1,"Delete Operation")
        self.Bind(wx.EVT_MENU,lambda event,caller=platecallercombobox:self.perform_delete(event,platecallercombobox),delete_item)
        self.PopupMenu(menu)
        
        
#        event.Skip()
    
    def make_plate_choicetxtlist(self):
        # Called by Other Class to create list used to setup comboboxes here
        if self.GetParent().PLATE_CONFIGURED:
            self.platelist = self.GetParent().plateobjects
        else:
            wx.MessageBox("Setting Choices regardless")
            self.platelist = self.GetParent().plateobjects
#        print "SETTING BUTTON TO UNCLICKABLE " ,self.GetParent().FindWindowByName("platesetup").GetName()
#        self.GetParent().FindWindowByName("platesetup").plate_add_button.Enable(False)

    def make_component_choice_list(self):
        self.component_frame_choices = []
        self.buffer_frame_choices = []
#        print "IYSYSY",self.GetParent().FindWindowByName("components").all_solutionsdict,self.GetParent().FindWindowByName("components").buffer_namedict
        try:
            for key in self.GetParent().FindWindowByName("components").all_solutionsdict:
                self.component_frame_choices.append(self.GetParent().FindWindowByName("components").all_solutionsdict[key][0])
            for key in self.GetParent().FindWindowByName("components").buffer_namedict:
                self.buffer_frame_choices.append(self.GetParent().FindWindowByName("components").buffer_namedict[key][0])
        except KeyError , e:
            #print "Something wrong , no generation of Component list or plate list possible at this time"
            if not self.GetParent().FindWindowByName("components").IS_CONFIGURED:
                wx.MessageBox("Please configure components and retry")
        # Refresh existing choice boxes
        rows,cols = self.po_sizer.CalcRowsCols()

        for row in range(1,rows,1):
            for col in range(2,cols,1):
                try:
                    w = self.po_sizer.GetItem(row*cols + col).GetWindow()
                    if isinstance(w,PromptingComboBox):
                        selected = None
                        try :
                            selected = w.GetValue()
                        except :
                            selected = ""
                            pass
                        # Deermine if we expeted a component or a buffer here
                        if "Buffer" in self.po_sizer.GetItem(row*cols + 1).GetWindow().GetValue():
                            w.Clear()
                            #print "BUFFER REPLACING" , w.choices,self.buffer_frame_choices
                            w.SetItems(self.buffer_frame_choices)
                            if selected in self.component_frame_choices:
                                w.SetValue(selected)
                            else:
                                w.SetValue("")

                        else:
                            #print "COMponent REPLACING" , w.choices,self.component_frame_choices
                            w.Clear()
                            w.SetItems(self.component_frame_choices)
                            if selected in self.component_frame_choices:
                                w.SetValue(selected)
                            else:
                                w.SetValue("")
                except Exception , e:
                    pass
                    #print "Nothing to Refresh"




    def make_choice_list(self):
        self.dispense_choice_boxlist = []
        sorted_keys = self.masterdict.keys()
        sorted_keys.sort()
        for key in sorted_keys:
            self.choices.append(key)


    def make_plate(self,event):
        import os
        from gridder import plateliberror
        scrfile = None
        if not self.GetParent().PLATE_CONFIGURED:
            wx.MessageBox("Plate configuration changed: Continuing regardless : Please check Dispense data")
        
        try :
            if self.GetParent().dirtowriteto == None :
                if os.environ.has_key("HOME"):
                    adialog = wx.DirDialog(self,message="Directory for dispense files",defaultPath=os.environ["HOME"])
                    adialog.ShowModal()
                    print "getting dialog"
                    self.GetParent().dirtowriteto = adialog.GetPath()
                    print "ALL OUTPUT TO DIR %s" % self.GetParent().dirtowriteto
                    scrfile = open(os.path.join(self.GetParent().dirtowriteto ,"%s_scr.py" % str(self.GetParent().FindWindowByName("mpanel").file_name_text.GetValue())),"w")
                else:
                    adialog = wx.DirDialog(self,message="Directory for dispense files",defaultPath=os.path.join(os.environ["HOMEDRIVE"],os.environ["HOMEPATH"]))
                    adialog.ShowModal()
                    print "getting dialog"
                    self.GetParent().dirtowriteto = adialog.GetPath()
                    print "ALL OUTPUT TO DIR %s" % self.GetParent().dirtowriteto
                    scrfile = open(os.path.join(self.GetParent().dirtowriteto ,"%s_scr.py" % str(self.GetParent().FindWindowByName("mpanel").file_name_text.GetValue())),"w")
            else :
                scrfile = open(os.path.join(self.GetParent().dirtowriteto ,"%s_scr.py" % str(self.GetParent().FindWindowByName("mpanel").file_name_text.GetValue())),"w")
            
        except KeyError , k :
            print "Not Linux/Mac/Windows I see"
            pass
        try:
            EXE_PATH_TO_ADD = os.path.dirname(sys.executable)
            #scrfile.write("#!/usr/bin/python\n")
            scrfile.write("import sys\n")
            scrfile.write("import os\n")
            scrfile.write("""sys.path.append(r"%s")""" % EXE_PATH_TO_ADD + "\n")
            library_zip = os.path.join(EXE_PATH_TO_ADD,"library.zip")
            scrfile.write("""sys.path.append(r"%s")""" % library_zip + "\n")
            scrfile.write("import pprint\n")
            scrfile.write("pprint.pprint(sys.path)\n")
            scrfile.write("import gridder\n")
            scrfile.write("from gridder import masterplate,plate,component,buffercomponent\n")
            scrfile.write("mp = masterplate.Masterplate(%s,%d)\n" % (self.GetParent().FindWindowByName("mpanel").volttc.GetValue(),self.GetParent().FindWindowByName("platesetup").style))

            myplate_setup = self.GetParent().FindWindowByName("platesetup").plate_setup_dict
            for key in myplate_setup.keys():
                    com =  "p%s = plate.Plate(\"%s\",\"%s\",mp)\n" % ( key,myplate_setup[key][0],myplate_setup[key][1])
                    #print com
                    scrfile.write(com)

            comppanel = self.GetParent().FindWindowByName("components").all_solutionsdict
            objdict = {}

            for key in sorted(comppanel.keys()):
                if key in self.GetParent().FindWindowByName("components").buffer_namedict.keys():
                    cargs = ""
                    cargs = ",".join(comppanel[key][1:])
                    com = "c%s = buffercomponent.SimpleBuffer(\"%s\" , %s)\n" % (key,comppanel[key][0],cargs)
                    #print com
                    scrfile.write(com)
                    objdict[comppanel[key][0]] = "c%s " %  key
                else:
                    cargs = ""
                    cargs = ",".join(comppanel[key][1:])
                    com = "c%s = component.Component(\"%s\" , %s)\n" % (key,comppanel[key][0],cargs)
                    #print com
                    scrfile.write(com)
                    objdict[comppanel[key][0]] = "c%s " %  key


    # These are integer keys
            for i in self.plate_operations.keys():
                # Bug in unicode cases in this code block
                # TODO FIX bug
                myobj = self.plate_operations[i]
                # We got the plateoperations object
                #print myobj.argdict
                argstring = "" 
                args = ""
                textentries = sorted(myobj.argdict.keys())
                # Since event keys are negative numbers , to preserve argument order for functions we reverse the keys
                textentries.reverse()
                allargs = []
                for sorted_key in textentries:
                    allargs.append(myobj.argdict[sorted_key])
                print "ARGSTRING ARRAY IS ", allargs
                #TODO understand implications of this change
                # This line synthesizes tyhe raw string of args from the argdict
                args = ",".join(allargs)
                #print "Arguments for self.plate_operations.keys()",args
                #args = r"%s" % argstring
                component_keys = sorted(myobj.component_dict.keys())
                cstring = ""
                for sorted_component in component_keys:
                    cstring = cstring +  objdict[myobj.component_dict[sorted_component]] + " "
                component_args = ",".join(cstring.split())
                #print myobj.plate
                com = "p%s.%s(%s,%s)\n" % (myobj.plate.split()[1],self.function_dict[myobj.op],component_args,args)
                print "Synthesized argstring is " , com
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
                #        scrfile.write("water = component.Component(\"100.00 % Water\",100,100000)\n")
                #        scrfile.write("pwhole = plate.Plate(\"A1\",\"H12\",mp)\n")
                #        scrfile.write("pwhole.fill_water(water)\n")

            scrfile.write("mp.printwellinfo()\n")
            scrfile.write("mp.makefileforformulatrix(r\"%s\")\n" % str(os.path.join(self.GetParent().dirtowriteto,"%s.dl.txt" % self.GetParent().FindWindowByName("mpanel").file_name_text.GetValue())))
            scrfile.write("mp.writepdf(r\"%s\")\n" % str(os.path.join(self.GetParent().dirtowriteto,"%s" % self.GetParent().FindWindowByName("mpanel").file_name_text.GetValue())))
    #        scrfile.write("mp.printpdf(r\"%s\")\n" % str((os.path.join(self.GetParent().dirtowriteto,"%s_volumes" % self.GetParent().FindWindowByName("mpanel").file_name_text.GetValue()))))
            scrfile.write("mp.makefileforhamilton(r\"%s\",1)\n" % str(os.path.join(self.GetParent().dirtowriteto,"%s-hamilton.csv" % self.GetParent().FindWindowByName("mpanel").file_name_text.GetValue())))
            scrfile.close()
        except Exception as ec:
            sys.stderr.write(ec.message)
            self.GetParent().GetStatusBar().SetBackgroundColour(wx.Colour(255,204,153))
            self.GetParent().GetStatusBar().SetStatusText("Something wrong in session file : Check all components and operations " + str(type(ec)))
            return
            
        try:
            os.chmod((os.path.join(self.GetParent().dirtowriteto,"%s_scr.py" % str(self.GetParent().FindWindowByName("mpanel").file_name_text.GetValue()))),0755)
            self.GetParent().GetStatusBar().SetStatusText("Making Dispense Lists")
            execfile(os.path.join(self.GetParent().dirtowriteto,"%s_scr.py" % str(self.GetParent().FindWindowByName("mpanel").file_name_text.GetValue())))
            self.GetParent().GetStatusBar().SetBackgroundColour(wx.Colour(0,204,153))
            self.GetParent().GetStatusBar().SetStatusText(r"Files Written to Directory : %s" % self.GetParent().dirtowriteto )
#            subp_status = subprocess.Popen(["python.exe",os.path.join(self.GetParent().dirtowriteto,"%s_scr.py" % str(self.GetParent().FindWindowByName("mpanel").file_name_text.GetValue()))],shell=False,stderr=None,stdout=None)
#            mystdout,mystderr = subp_status.communicate()
#            if subp_status.returncode != 0 :
#                self.GetParent().GetStatusBar().SetBackgroundColour(wx.Colour(255,204,153))
#                #print mystderr
#                sys.stderr.write(mystderr)
#                self.GetParent().GetStatusBar().SetStatusText("\n".join(mystderr.splitlines()[-1:]))
#                return
#
#
#
#            self.GetParent().GetStatusBar().SetStatusText("DISPENSE LIST %s OUTPUT  " % str(os.path.join(self.GetParent().dirtowriteto,"%s.dl.txt" % self.GetParent().FindWindowByName("mpanel").file_name_text.GetValue())))
#            self.GetParent().GetStatusBar().SetStatusText("FILES OUTPUT with prefix %s" % str(os.path.join(self.GetParent().dirtowriteto,"%s" % self.GetParent().FindWindowByName("mpanel").file_name_text.GetValue())))
#            self.GetParent().GetStatusBar().SetBackgroundColour(wx.Colour(204,255,204))
#
#        except plateliberror.PlatelibException , p :
#            self.GetParent().GetStatusBar().SetBackgroundColour(wx.Colour(255,204,153))
#            self.GetParent().GetStatusBar().SetStatusText(p.message)

        except Exception , e:
            sys.stderr.write(e.message)
            self.GetParent().GetStatusBar().SetBackgroundColour(wx.Colour(255,204,153))
            self.GetParent().GetStatusBar().SetStatusText(str(e))

    def delete_all_operations(self,event):
        rows,cols = self.po_sizer.CalcRowsCols()
        self.DestroyChildren()
        self.plate_combobox_objects = []
        self.po_sizer.Clear()
#        for rownum in range(rows):
#            w = self.po_sizer.GetItem(rownum*cols).GetWindow()
#            print w
#            if isinstance(w,PromptingComboBox):
#                self.perform_delete(event,w)

#        self.dispense_choice_boxlist= []
#
#        self.plate_operations = {}
#        # Combobox choices populated by events that propagate from above
#        self.component_frame_choices = []
#        self.buffer_frame_choices = []


    # plate_id_mapper_dict maps plate components to their row positions
    plate_id_mapper_dict = {}

    def save_session(self,event,session_dict):
        tmp_dict = {}
        if self.plate_operations.keys():
            for key in self.plate_operations.keys():
                myobj = self.plate_operations[key]
                myobj.platelist =  self.platelist
                myobj.choices = self.choices
                myobj.components = self.component_frame_choices
                tmp_dict["Operation %s" % key] = myobj.__dict__
        session_dict["operations"] = tmp_dict
        session_dict["plate_config_state"] = self.GetParent().PLATE_CONFIGURED




        
class MpPanel(wx.ScrolledWindow):

    def __init__(self,*args,**kwds):
        wx.ScrolledWindow.__init__(self,*args,**kwds)
        kwds["size"] = MYFRAMESIZE
        self.platevol_label = wx.StaticText(self,-1,"Plate Volume")
        self.volttc = wx.TextCtrl(self,-1,"2000")
        self.filenamelabel = wx.StaticText(self,-1,"Dispense file prefix")
        self.file_name_text = wx.TextCtrl(self,-1,"test")
        self.add_op_button = wx.Button(self,label="Add Operation")
        self.make_plate_button = wx.Button(self,label="Make Plate")
        self.save_session_button = wx.Button(self,label="Save Session")
        self.refresh_operations_button = wx.Button(self,label="Delete all operations")
        self.Bind(wx.EVT_BUTTON,self.GetParent().FindWindowByName("plateop").add_operation,self.add_op_button)
        self.Bind(wx.EVT_BUTTON,self.GetParent().FindWindowByName("plateop").make_plate,self.make_plate_button)
        self.Bind(wx.EVT_BUTTON, self.GetParent().save_session,self.save_session_button)
        self.Bind(wx.EVT_BUTTON,self.GetParent().FindWindowByName("plateop").delete_all_operations,self.refresh_operations_button)
        self.szr = wx.FlexGridSizer(3,2,10,10)
        self.szr.Add(self.add_op_button)
        self.szr.Add(self.make_plate_button)
        self.szr.Add(self.platevol_label)
        self.szr.Add(self.volttc)
        self.szr.Add(self.filenamelabel)
        self.szr.Add(self.file_name_text)
        self.szr.Add(self.save_session_button)
        self.szr.Add(self.refresh_operations_button)
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
    maframe.Layout()
    maframe.Show()
    # Debug using this tool
#    wx.lib.inspection.InspectionTool().Show()
    app.MainLoop()
