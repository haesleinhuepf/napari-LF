import os, sys, glob, ntpath, subprocess, traceback, json, time
from pathlib import Path
from qtpy import QtCore, QtGui
from qtpy.QtCore import Qt, QTimer
from qtpy.QtWidgets import *
from magicgui.widgets import *

try:
	from napari_lf import _widgetLF_vals as LFvals
except:
	import _widgetLF_vals as LFvals

try:	
	import pyopencl as cl
except Exception as e:
	print(e)
	print(traceback.format_exc())

class LFQWidgetGui():
		
	def __init__(self):
		super().__init__()
		self.currentdir = os.path.dirname(os.path.realpath(__file__))
		self.lf_vals = LFvals.PLUGIN_ARGS
		self.settings = {}
		self.gui_elms = {}
		
		# == MAIN ==
		self.gui_elms["main"] = {}
		_widget_main = []
		self.logo_label = Label(value=LFvals.PLUGIN_ARGS['main']['logo_label']['label'], tooltip=LFvals.PLUGIN_ARGS['main']['logo_label']['help'])
		self.logo_label.native.setAlignment(Qt.AlignCenter|Qt.AlignVCenter)
		self.logo_label.native.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		
		self.info_label = Label(label=f'<h2><center>LF Analyze</a></center></h2>')
		dict = LFvals.PLUGIN_ARGS["main"]["img_folder"]
		self.gui_elms["main"]["img_folder"] = create_widget(dict)
		
		dict = LFvals.PLUGIN_ARGS["main"]["img_list"]
		self.gui_elms["main"]["img_list"] = create_widget(dict)
		
		self.btn_open_img = PushButton(label='Open Image')
		self.btn_open_img.max_width = 80
		_cont_img_list_btn = Container(name='Image List Open', widgets=[self.gui_elms["main"]["img_list"], self.btn_open_img], layout='horizontal', labels=False)

		dict = LFvals.PLUGIN_ARGS["main"]["metadata_file"]
		self.gui_elms["main"]["metadata_file"] = create_widget(dict)
		
		dict = LFvals.PLUGIN_ARGS["main"]["comments"]
		self.gui_elms["main"]["comments"] = create_widget(dict)
		self.gui_elms["main"]["comments"].native.setMaximumHeight(50)
		
		dict = LFvals.PLUGIN_ARGS["main"]["presets"]
		self.gui_elms["main"]["presets"] = create_widget(dict)
		self.btn_preset_load = PushButton(label='Load')
		self.btn_preset_save = PushButton(label='Save As..')
		self.btn_preset_delete = PushButton(label='Delete')
		_cont_preset_list_btn = Container(name='Presets', widgets=[self.gui_elms["main"]["presets"], self.btn_preset_load, self.btn_preset_save, self.btn_preset_delete], layout='horizontal', labels=False)
		_cont_preset_list_btn.native.layout().setContentsMargins(1,1,1,1)
		_cont_preset_list_btn.native.layout().setSpacing(1)
		
		_cont_btn_QFormLayout = QFormLayout()
		_cont_btn_widget = QWidget()
		_cont_btn_widget.setLayout(_cont_btn_QFormLayout)
		_cont_btn_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		_cont_btn_QFormLayout.setSpacing(2)
		_cont_btn_QFormLayout.setContentsMargins(1,1,1,1)
		
		self.btn_cal = PushButton(label='Calibrate')
		self.btn_cal.native.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		self.btn_cal_prog = Label()
		self.btn_cal_prog.native.setFixedSize(20,20)
		self.btn_cal_prog.native.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
		
		_cont_btn_QFormLayout.addRow(self.btn_cal_prog.native, self.btn_cal.native)

		self.btn_rec = PushButton(label='Rectify')
		self.btn_rec.native.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		self.btn_rec_prog = Label()
		self.btn_rec_prog.native.setFixedSize(20,20)
		self.btn_rec_prog.native.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
		
		_cont_btn_QFormLayout.addRow(self.btn_rec_prog.native, self.btn_rec.native)
		
		self.btn_dec = PushButton(label='Deconvolve')
		self.btn_dec.native.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		self.btn_dec_prog = Label()
		self.btn_dec_prog.native.setFixedSize(20,20)
		self.btn_dec_prog.native.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
		
		_cont_btn_QFormLayout.addRow(self.btn_dec_prog.native, self.btn_dec.native)
		
		_cont_btn_left = Container(name='btn Left', widgets=(), labels=False)
		_cont_btn_left.native.layout().addWidget(_cont_btn_widget)
		
		self.btn_stop = PushButton(label='Stop')
		self.btn_stop.min_height = 65
		self.btn_stop.min_width = 65
		
		_cont_btn_right = Container(name='btn Right', widgets=[self.btn_stop], labels=False)
		_cont_btn_processing = Container(widgets=[_cont_btn_left, _cont_btn_right], labels=False, layout='horizontal')
		_cont_btn_processing.native.layout().setContentsMargins(1,1,1,1)
		
		_QFormLayout = QFormLayout()
		self.cont_btn_status = QWidget()
		self.cont_btn_status.setLayout(_QFormLayout)
		_QFormLayout.setContentsMargins(1,1,1,1)
		
		self.cont_btn_status_label = Label()
		self.cont_btn_status_label.native.setStyleSheet("border:1px solid rgb(0, 255, 0);")
		self.cont_btn_status_label.value = ':STATUS: ' + LFvals.PLUGIN_ARGS['main']['status']['value_idle']
		
		_QFormLayout.addRow(self.logo_label.native)
		_QFormLayout.addRow(self.gui_elms["main"]["img_folder"].label, self.gui_elms["main"]["img_folder"].native)
		_QFormLayout.addRow(_cont_img_list_btn.native)
		_QFormLayout.addRow(self.gui_elms["main"]["metadata_file"].label, self.gui_elms["main"]["metadata_file"].native)
		_QFormLayout.addRow(self.gui_elms["main"]["presets"].label, _cont_preset_list_btn.native)
		_QFormLayout.addRow(self.gui_elms["main"]["comments"].label, self.gui_elms["main"]["comments"].native)
		
		_QFormLayout.addRow(_cont_btn_processing.native)
		_QFormLayout.addRow(self.cont_btn_status_label.native)
		
		self.cont_btn_status.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
		self.cont_btn_status_label.native.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		self.cont_btn_status_label.native.setAlignment(Qt.AlignCenter|Qt.AlignVCenter)
		
		self.groupbox = {"calibrate":{"required":{},"optional":{},"inspect":{}},"rectify":{"required":{},"optional":{}},"deconvolve":{"required":{},"optional":{}}}
		
		# == CALIBATE ==
		_widget_calibrate_req = []
		_widget_calibrate_opt = []
		_widget_calibrate_ins = []
		self.gui_elms["calibrate"] = {}
		
		for key in self.lf_vals["calibrate"]:
			dict = self.lf_vals["calibrate"][key]
			if "label" not in dict:
				dict["label"] = dict["dest"]
			wid_elm = create_widget(dict)
			if wid_elm != None:
				self.gui_elms["calibrate"][key] = wid_elm
				
				if "cat" in dict and dict["cat"] == "required":
					if self.lf_vals["misc"]["group_params"]["value"] == False:
						_widget_calibrate_req.append(wid_elm)
					else:
						if "group" in dict and dict["group"] not in self.groupbox["calibrate"]["required"]:
							self.groupbox["calibrate"]["required"][dict["group"]] = QGroupBox(dict["group"])
							vbox = QFormLayout()
							_widget_calibrate_req.append(self.groupbox["calibrate"]["required"][dict["group"]])
							self.groupbox["calibrate"]["required"][dict["group"]].setLayout(vbox)
							if dict["type"] == "bool":
								self.groupbox["calibrate"]["required"][dict["group"]].layout().addRow(wid_elm.native)
							else:
								self.groupbox["calibrate"]["required"][dict["group"]].layout().addRow(wid_elm.label, wid_elm.native)
						elif ("group" in dict and dict["group"] in self.groupbox["calibrate"]["required"]) or "misc" in self.groupbox["calibrate"]["required"]:
							if dict["type"] == "bool":
								self.groupbox["calibrate"]["required"][dict["group"]].layout().addRow(wid_elm.native)
							else:
								self.groupbox["calibrate"]["required"][dict["group"]].layout().addRow(wid_elm.label, wid_elm.native)
						else:
							self.groupbox["calibrate"]["required"]["misc"] = QGroupBox("Misc")
							vbox = QFormLayout()
							_widget_calibrate_req.append(self.groupbox["calibrate"]["required"]["misc"])
							self.groupbox["calibrate"]["required"]["misc"].setLayout(vbox)
							if dict["type"] == "bool":
								self.groupbox["calibrate"]["required"]["misc"].layout().addRow(wid_elm.native)
							else:
								self.groupbox["calibrate"]["required"]["misc"].layout().addRow(wid_elm.label, wid_elm.native)
				elif "cat" in dict and dict["cat"] == "inspect":
					if self.lf_vals["misc"]["group_params"]["value"] == False:
						_widget_calibrate_ins.append(wid_elm)
					else:
						if "group" in dict and dict["group"] not in self.groupbox["calibrate"]["inspect"]:
							self.groupbox["calibrate"]["inspect"][dict["group"]] = QGroupBox(dict["group"])
							vbox = QFormLayout()
							_widget_calibrate_ins.append(self.groupbox["calibrate"]["inspect"][dict["group"]])
							self.groupbox["calibrate"]["inspect"][dict["group"]].setLayout(vbox)
							if dict["type"] == "bool":
								self.groupbox["calibrate"]["inspect"][dict["group"]].layout().addRow(wid_elm.native)
							else:
								self.groupbox["calibrate"]["inspect"][dict["group"]].layout().addRow(wid_elm.label, wid_elm.native)
						elif ("group" in dict and dict["group"] in self.groupbox["calibrate"]["inspect"]) or "misc" in self.groupbox["calibrate"]["inspect"]:
							if dict["type"] == "bool":
								self.groupbox["calibrate"]["inspect"][dict["group"]].layout().addRow(wid_elm.native)
							elif "no_label_layout_style" in dict and dict["no_label_layout_style"] == True:
								self.groupbox["calibrate"]["inspect"][dict["group"]].layout().addRow(wid_elm.native)
							else:
								self.groupbox["calibrate"]["inspect"][dict["group"]].layout().addRow(wid_elm.label, wid_elm.native)
						else:
							self.groupbox["calibrate"]["inspect"]["misc"] = QGroupBox("Misc")
							vbox = QFormLayout()
							_widget_calibrate_ins.append(self.groupbox["calibrate"]["inspect"]["misc"])
							self.groupbox["calibrate"]["inspect"]["misc"].setLayout(vbox)
							if dict["type"] == "bool":
								self.groupbox["calibrate"]["inspect"]["misc"].layout().addRow(wid_elm.native)
							else:
								self.groupbox["calibrate"]["inspect"]["misc"].layout().addRow(wid_elm.label, wid_elm.native)
				else:
					if self.lf_vals["misc"]["group_params"]["value"] == False:
						_widget_calibrate_opt.append(wid_elm)
					else:
						if "group" in dict and dict["group"] not in self.groupbox["calibrate"]["optional"]:
							self.groupbox["calibrate"]["optional"][dict["group"]] = QGroupBox(dict["group"])
							vbox = QFormLayout()
							_widget_calibrate_opt.append(self.groupbox["calibrate"]["optional"][dict["group"]])
							self.groupbox["calibrate"]["optional"][dict["group"]].setLayout(vbox)
							if dict["type"] == "bool":
								self.groupbox["calibrate"]["optional"][dict["group"]].layout().addRow(wid_elm.native)
							else:
								self.groupbox["calibrate"]["optional"][dict["group"]].layout().addRow(wid_elm.label, wid_elm.native)
						elif ("group" in dict and dict["group"] in self.groupbox["calibrate"]["optional"]) or "misc" in self.groupbox["calibrate"]["optional"]:
							if dict["type"] == "bool":
								self.groupbox["calibrate"]["optional"][dict["group"]].layout().addRow(wid_elm.native)
							else:
								self.groupbox["calibrate"]["optional"][dict["group"]].layout().addRow(wid_elm.label, wid_elm.native)
						else:
							self.groupbox["calibrate"]["optional"]["misc"] = QGroupBox("Misc")
							vbox = QFormLayout()
							_widget_calibrate_opt.append(self.groupbox["calibrate"]["optional"]["misc"])
							self.groupbox["calibrate"]["optional"]["misc"].setLayout(vbox)
							if dict["type"] == "bool":
								self.groupbox["calibrate"]["optional"]["misc"].layout().addRow(wid_elm.native)
							else:
								self.groupbox["calibrate"]["optional"]["misc"].layout().addRow(wid_elm.label, wid_elm.native)
					
		self.btn_cal_req_def = PushButton(name='RTD', label='Reset to Defaults')
		@self.btn_cal_req_def.changed.connect
		def btn_cal_req_defaults():
			qm = QMessageBox
			ret = qm.question(QWidget(),'', "Reset Values to Default ?", qm.Yes | qm.No)
			if ret == qm.Yes:
				for key in self.lf_vals["calibrate"]:
					dict = self.lf_vals["calibrate"][key]
					if "cat" in dict and dict["cat"] == "required":
						wid_elm = self.gui_elms["calibrate"][key]
						try:
							if wid_elm.widget_type == 'ComboBox':
								if dict["default"] in wid_elm.choices:
									wid_elm.value = dict["default"]
								elif len(wid_elm.choices) == 0:
									pass
								else:
									wid_elm.value = wid_elm.choices[0]
							else:
								wid_elm.value = dict["default"]
						except Exception as e:
							print(e)
							print(traceback.format_exc())
				self.verify_preset_vals()
		
		self.btn_cal_opt_def = PushButton(name='RTD', label='Reset to Defaults')
		@self.btn_cal_opt_def.changed.connect
		def btn_cal_opt_defaults():
			qm = QMessageBox
			ret = qm.question(QWidget(),'', "Reset Values to Default ?", qm.Yes | qm.No)
			if ret == qm.Yes:
				for key in self.lf_vals["calibrate"]:
					dict = self.lf_vals["calibrate"][key]
					if "cat" in dict and dict["cat"] == "required":
						pass
					else:
						wid_elm = self.gui_elms["calibrate"][key]
						try:
							if wid_elm.widget_type == 'ComboBox':
								if dict["default"] in wid_elm.choices:
									wid_elm.value = dict["default"]
								elif len(wid_elm.choices) == 0:
									pass
								else:
									wid_elm.value = wid_elm.choices[0]
							else:
								wid_elm.value = dict["default"]
						except Exception as e:
							print(e)
							print(traceback.format_exc())
				self.verify_preset_vals()
		
		if self.lf_vals["misc"]["group_params"]["value"] == False:
			_widget_calibrate_req.append(self.btn_cal_req_def)			
			_widget_calibrate_opt.append(self.btn_cal_opt_def)
			self.widget_calibrate_req = Container(name='Calibrate Req', widgets=_widget_calibrate_req)
			self.widget_calibrate_opt = Container(name='Calibrate Opt', widgets=_widget_calibrate_opt)
			self.widget_calibrate_ins = Container(name='Calibrate Opt', widgets=_widget_calibrate_ins)
		else:
			_widget_calibrate_req.append(self.btn_cal_req_def.native)			
			_widget_calibrate_opt.append(self.btn_cal_opt_def.native)
			
			self.widget_calibrate_req = Container(name='Calibrate Req', widgets=())
			for wid_elm in _widget_calibrate_req:
				self.widget_calibrate_req.native.layout().addWidget(wid_elm)
			self.widget_calibrate_opt = Container(name='Calibrate Opt', widgets=())
			for wid_elm in _widget_calibrate_opt:
				self.widget_calibrate_opt.native.layout().addWidget(wid_elm)
			self.widget_calibrate_ins = Container(name='Calibrate Ins', widgets=())
			for wid_elm in _widget_calibrate_ins:
				self.widget_calibrate_ins.native.layout().addWidget(wid_elm)
		
		# == RECTIFY ==
		_widget_rectify_req = []
		_widget_rectify_opt = []
		self.gui_elms["rectify"] = {}
		for key in self.lf_vals["rectify"]:
			dict = self.lf_vals["rectify"][key]
			if "label" not in dict:
				dict["label"] = dict["dest"]
			wid_elm = create_widget(dict)
			if wid_elm != None:
				self.gui_elms["rectify"][key] = wid_elm
				
				if "cat" in dict and dict["cat"] == "required":
					if self.lf_vals["misc"]["group_params"]["value"] == False:
						_widget_rectify_req.append(wid_elm)
					else:
						if "group" in dict and dict["group"] not in self.groupbox["rectify"]["required"]:
							self.groupbox["rectify"]["required"][dict["group"]] = QGroupBox(dict["group"])
							vbox = QFormLayout()
							_widget_rectify_req.append(self.groupbox["rectify"]["required"][dict["group"]])
							self.groupbox["rectify"]["required"][dict["group"]].setLayout(vbox)
							if dict["type"] == "bool":
								self.groupbox["rectify"]["required"][dict["group"]].layout().addRow(wid_elm.native)
							else:
								self.groupbox["rectify"]["required"][dict["group"]].layout().addRow(wid_elm.label, wid_elm.native)
						elif ("group" in dict and dict["group"] in self.groupbox["rectify"]["required"]) or "misc" in self.groupbox["rectify"]["required"]:
							group = "misc"
							if "group" in dict:
								group = dict["group"]
							if dict["type"] == "bool":
								self.groupbox["rectify"]["required"][group].layout().addRow(wid_elm.native)
							else:
								self.groupbox["rectify"]["required"][group].layout().addRow(wid_elm.label, wid_elm.native)
						else:
							self.groupbox["rectify"]["required"]["misc"] = QGroupBox("Misc")
							vbox = QFormLayout()
							_widget_rectify_req.append(self.groupbox["rectify"]["required"]["misc"])
							self.groupbox["rectify"]["required"]["misc"].setLayout(vbox)
							if dict["type"] == "bool":
								self.groupbox["rectify"]["required"]["misc"].layout().addRow(wid_elm.native)
							else:
								self.groupbox["rectify"]["required"]["misc"].layout().addRow(wid_elm.label, wid_elm.native)
				else:
					if self.lf_vals["misc"]["group_params"]["value"] == False:
						_widget_rectify_opt.append(wid_elm)
					else:
						if "group" in dict and dict["group"] not in self.groupbox["rectify"]["optional"]:
							self.groupbox["rectify"]["optional"][dict["group"]] = QGroupBox(dict["group"])
							vbox = QFormLayout()
							_widget_rectify_opt.append(self.groupbox["rectify"]["optional"][dict["group"]])
							self.groupbox["rectify"]["optional"][dict["group"]].setLayout(vbox)
							if dict["type"] == "bool":
								self.groupbox["rectify"]["optional"][dict["group"]].layout().addRow(wid_elm.native)
							else:
								self.groupbox["rectify"]["optional"][dict["group"]].layout().addRow(wid_elm.label, wid_elm.native)
						elif ("group" in dict and dict["group"] in self.groupbox["rectify"]["optional"]) or "misc" in self.groupbox["rectify"]["optional"]:
							group = "misc"
							if "group" in dict:
								group = dict["group"]
							if dict["type"] == "bool":
								self.groupbox["rectify"]["optional"][group].layout().addRow(wid_elm.native)
							else:
								self.groupbox["rectify"]["optional"][group].layout().addRow(wid_elm.label, wid_elm.native)
						else:
							self.groupbox["rectify"]["optional"]["misc"] = QGroupBox("Misc")
							vbox = QFormLayout()
							_widget_rectify_opt.append(self.groupbox["rectify"]["optional"]["misc"])
							self.groupbox["rectify"]["optional"]["misc"].setLayout(vbox)
							if dict["type"] == "bool":
								self.groupbox["rectify"]["optional"]["misc"].layout().addRow(wid_elm.native)
							else:
								self.groupbox["rectify"]["optional"]["misc"].layout().addRow(wid_elm.label, wid_elm.native)
					
		self.btn_rec_req_def = PushButton(name='RTD', label='Reset to Defaults')
		@self.btn_rec_req_def.changed.connect
		def btn_rec_req_defaults():
			qm = QMessageBox
			ret = qm.question(QWidget(),'', "Reset Values to Default ?", qm.Yes | qm.No)
			if ret == qm.Yes:
				for key in self.lf_vals["rectify"]:
					dict = self.lf_vals["rectify"][key]
					if "cat" in dict and dict["cat"] == "required":
						wid_elm = self.gui_elms["rectify"][key]
						try:
							if wid_elm.widget_type == 'ComboBox':
								if dict["default"] in wid_elm.choices:
									wid_elm.value = dict["default"]
								elif len(wid_elm.choices) == 0:
									pass
								else:
									wid_elm.value = wid_elm.choices[0]
							else:
								wid_elm.value = dict["default"]
						except Exception as e:
							print(e)
							print(traceback.format_exc())
				self.verify_preset_vals()
		
		self.btn_rec_opt_def = PushButton(name='RTD', label='Reset to Defaults')
		@self.btn_rec_opt_def.changed.connect
		def btn_rec_opt_defaults():
			qm = QMessageBox
			ret = qm.question(QWidget(),'', "Reset Values to Default ?", qm.Yes | qm.No)
			if ret == qm.Yes:
				for key in self.lf_vals["rectify"]:
					dict = self.lf_vals["rectify"][key]
					if "cat" in dict and dict["cat"] == "required":
						pass
					else:
						wid_elm = self.gui_elms["rectify"][key]
						try:
							if wid_elm.widget_type == 'ComboBox':
								if dict["default"] in wid_elm.choices:
									wid_elm.value = dict["default"]
								elif len(wid_elm.choices) == 0:
									pass
								else:
									wid_elm.value = wid_elm.choices[0]
							else:
								wid_elm.value = dict["default"]
						except Exception as e:
							print(e)
							print(traceback.format_exc())
				self.verify_preset_vals()
						
		if self.lf_vals["misc"]["group_params"]["value"] == False:
			_widget_rectify_req.append(self.btn_rec_req_def)			
			_widget_rectify_opt.append(self.btn_rec_opt_def)
			self.widget_rectify_req = Container(name='Rectify Req', widgets=_widget_rectify_req)
			self.widget_rectify_opt = Container(name='Rectify Opt', widgets=_widget_rectify_opt)
		else:
			_widget_rectify_req.append(self.btn_rec_req_def.native)			
			_widget_rectify_opt.append(self.btn_rec_opt_def.native)
			
			self.widget_rectify_req = Container(name='Rectify Req', widgets=())
			for wid_elm in _widget_rectify_req:
				self.widget_rectify_req.native.layout().addWidget(wid_elm)
			self.widget_rectify_opt = Container(name='Rectify Opt', widgets=())
			for wid_elm in _widget_rectify_opt:
				self.widget_rectify_opt.native.layout().addWidget(wid_elm)
		
		# == DECONVOLVE ==
		_widget_deconvolve_req = []
		_widget_deconvolve_opt = []
		self.gui_elms["deconvolve"] = {}
		for key in self.lf_vals["deconvolve"]:
			dict = self.lf_vals["deconvolve"][key]
			if "label" not in dict:
				dict["label"] = dict["dest"]
			wid_elm = create_widget(dict)
			if wid_elm != None:
				self.gui_elms["deconvolve"][key] = wid_elm
				
				if "cat" in dict and dict["cat"] == "required":
					if self.lf_vals["misc"]["group_params"]["value"] == False:
						_widget_deconvolve_req.append(wid_elm)
					else:
						if "group" in dict and dict["group"] not in self.groupbox["deconvolve"]["required"]:
							self.groupbox["deconvolve"]["required"][dict["group"]] = QGroupBox(dict["group"])
							vbox = QFormLayout()
							_widget_deconvolve_req.append(self.groupbox["deconvolve"]["required"][dict["group"]])
							self.groupbox["deconvolve"]["required"][dict["group"]].setLayout(vbox)
							if dict["type"] == "bool":
								self.groupbox["deconvolve"]["required"][dict["group"]].layout().addRow(wid_elm.native)
							else:
								self.groupbox["deconvolve"]["required"][dict["group"]].layout().addRow(wid_elm.label, wid_elm.native)
						elif ("group" in dict and dict["group"] in self.groupbox["deconvolve"]["required"]) or "misc" in self.groupbox["deconvolve"]["required"]:
							group = "misc"
							if "group" in dict:
								group = dict["group"]
							if dict["type"] == "bool":
								self.groupbox["deconvolve"]["required"][group].layout().addRow(wid_elm.native)
							else:
								self.groupbox["deconvolve"]["required"][group].layout().addRow(wid_elm.label, wid_elm.native)
						else:
							self.groupbox["deconvolve"]["required"]["misc"] = QGroupBox("Misc")
							vbox = QFormLayout()
							_widget_deconvolve_req.append(self.groupbox["deconvolve"]["required"]["misc"])
							self.groupbox["deconvolve"]["required"]["misc"].setLayout(vbox)
							if dict["type"] == "bool":
								self.groupbox["deconvolve"]["required"]["misc"].layout().addRow(wid_elm.native)
							else:
								self.groupbox["deconvolve"]["required"]["misc"].layout().addRow(wid_elm.label, wid_elm.native)
				else:
					if self.lf_vals["misc"]["group_params"]["value"] == False:
						_widget_deconvolve_opt.append(wid_elm)
					else:
						if "group" in dict and dict["group"] not in self.groupbox["deconvolve"]["optional"]:
							self.groupbox["deconvolve"]["optional"][dict["group"]] = QGroupBox(dict["group"])
							vbox = QFormLayout()
							_widget_deconvolve_opt.append(self.groupbox["deconvolve"]["optional"][dict["group"]])
							self.groupbox["deconvolve"]["optional"][dict["group"]].setLayout(vbox)
							if dict["type"] == "bool":
								self.groupbox["deconvolve"]["optional"][dict["group"]].layout().addRow(wid_elm.native)
							else:
								self.groupbox["deconvolve"]["optional"][dict["group"]].layout().addRow(wid_elm.label, wid_elm.native)
						elif ("group" in dict and dict["group"] in self.groupbox["deconvolve"]["optional"]) or "misc" in self.groupbox["deconvolve"]["optional"]:
							group = "misc"
							if "group" in dict:
								group = dict["group"]
							if dict["type"] == "bool":
								self.groupbox["deconvolve"]["optional"][group].layout().addRow(wid_elm.native)
							else:
								self.groupbox["deconvolve"]["optional"][group].layout().addRow(wid_elm.label, wid_elm.native)
						else:
							self.groupbox["deconvolve"]["optional"]["misc"] = QGroupBox("Misc")
							vbox = QFormLayout()
							_widget_deconvolve_opt.append(self.groupbox["deconvolve"]["optional"]["misc"])
							self.groupbox["deconvolve"]["optional"]["misc"].setLayout(vbox)
							if dict["type"] == "bool":
								self.groupbox["deconvolve"]["optional"]["misc"].layout().addRow(wid_elm.native)
							else:
								self.groupbox["deconvolve"]["optional"]["misc"].layout().addRow(wid_elm.label, wid_elm.native)
					
		self.btn_dec_req_def = PushButton(name='RTD', label='Reset to Defaults')
		@self.btn_dec_req_def.changed.connect
		def btn_dec_req_defaults():
			qm = QMessageBox
			ret = qm.question(QWidget(),'', "Reset Values to Default ?", qm.Yes | qm.No)
			if ret == qm.Yes:
				for key in self.lf_vals["deconvolve"]:
					dict = self.lf_vals["deconvolve"][key]
					if "cat" in dict and dict["cat"] == "required":
						wid_elm = self.gui_elms["deconvolve"][key]
						try:
							if wid_elm.widget_type == 'ComboBox':
								if dict["default"] in wid_elm.choices:
									wid_elm.value = dict["default"]
								elif len(wid_elm.choices) == 0:
									pass
								else:
									wid_elm.value = wid_elm.choices[0]
							else:
								wid_elm.value = dict["default"]
						except Exception as e:
							print(e)
							print(traceback.format_exc())
				self.verify_preset_vals()
			
		self.btn_dec_opt_def = PushButton(name='RTD', label='Reset to Defaults')
		@self.btn_dec_opt_def.changed.connect
		def btn_dec_opt_defaults():
			qm = QMessageBox
			ret = qm.question(QWidget(),'', "Reset Values to Default ?", qm.Yes | qm.No)
			if ret == qm.Yes:
				for key in self.lf_vals["deconvolve"]:
					dict = self.lf_vals["deconvolve"][key]
					if "cat" in dict and dict["cat"] == "required":
						pass
					else:
						wid_elm = self.gui_elms["deconvolve"][key]
						try:
							if wid_elm.widget_type == 'ComboBox':
								if dict["default"] in wid_elm.choices:
									wid_elm.value = dict["default"]
								elif len(wid_elm.choices) == 0:
									pass
								else:
									wid_elm.value = wid_elm.choices[0]
							else:
								wid_elm.value = dict["default"]
						except Exception as e:
							print(e)
							print(traceback.format_exc())
				self.verify_preset_vals()
					
		if self.lf_vals["misc"]["group_params"]["value"] == False:
			_widget_deconvolve_req.append(self.btn_dec_req_def)			
			_widget_deconvolve_opt.append(self.btn_dec_opt_def)
			self.widget_deconvolve_req = Container(name='Deconvolve Req', widgets=_widget_deconvolve_req)
			self.widget_deconvolve_opt = Container(name='Deconvolve Opt', widgets=_widget_deconvolve_opt)
		else:
			_widget_deconvolve_req.append(self.btn_dec_req_def.native)			
			_widget_deconvolve_opt.append(self.btn_dec_opt_def.native)
			
			self.widget_deconvolve_req = Container(name='Deconvolve Req', widgets=())
			for wid_elm in _widget_deconvolve_req:
				self.widget_deconvolve_req.native.layout().addWidget(wid_elm)
			self.widget_deconvolve_opt = Container(name='Deconvolve Opt', widgets=())
			for wid_elm in _widget_deconvolve_opt:
				self.widget_deconvolve_opt.native.layout().addWidget(wid_elm)
		
		# == HARDWARE ==
		self.gui_elms["hw"] = {}
		_widget_hw = []
		self.gpu_choices = self.get_GPU()
		self.gui_elms["hw"]["gpu_id"] = ComboBox(name='Select Device', label='Select Device', tooltip=LFvals.PLUGIN_ARGS['hw']['gpu_id']['help'], choices=(self.gpu_choices))
		self.platforms_choices = self.get_PlatForms()
		self.gui_elms["hw"]["platform_id"] = ComboBox(name='Select Platform', label='Select Platform', tooltip=LFvals.PLUGIN_ARGS['hw']['platform_id']['help'], choices=(self.platforms_choices))
		# self.cpu_threads_combobox = ComboBox(label=LFvals.PLUGIN_ARGS['calibrate']['num_threads']['label'], tooltip=LFvals.PLUGIN_ARGS['calibrate']['num_threads']['help'], choices=(list(range(1,129))))
		self.gui_elms["hw"]["disable_gpu"] = CheckBox(label=LFvals.PLUGIN_ARGS['hw']['disable_gpu']['label'], value=LFvals.PLUGIN_ARGS['hw']['disable_gpu']['default'], tooltip=LFvals.PLUGIN_ARGS['hw']['disable_gpu']['help'])
		self.gui_elms["hw"]["use_single_prec"] = CheckBox(label=LFvals.PLUGIN_ARGS['hw']['use_single_prec']['label'], value=LFvals.PLUGIN_ARGS['hw']['use_single_prec']['default'], tooltip=LFvals.PLUGIN_ARGS['hw']['use_single_prec']['help'])
		
		for key in LFvals.PLUGIN_ARGS['hw']:
			wid_elm = self.gui_elms["hw"][key]
			_widget_hw.append(wid_elm)
			
		self.btn_hw_def = PushButton(name='RTD', label='Reset to Defaults')
		@self.btn_hw_def.changed.connect
		def btn_hw_defaults():
			qm = QMessageBox
			ret = qm.question(QWidget(),'', "Reset Values to Default ?", qm.Yes | qm.No)
			if ret == qm.Yes:
				for key in self.lf_vals["hw"]:
					dict = self.lf_vals["hw"][key]
					wid_elm = self.gui_elms["hw"][key]
					if dict["type"] == "int" and type(wid_elm.value).__name__ == "str":
						try:
							wid_elm.value = wid_elm.choices[dict["default"]]
						except Exception as e:
							print(e)
							print(traceback.format_exc())
					else:
						try:
							if wid_elm.widget_type == 'ComboBox':
								if dict["default"] in wid_elm.choices:
									wid_elm.value = dict["default"]
								elif len(wid_elm.choices) == 0:
									pass
								else:
									wid_elm.value = wid_elm.choices[0]
							else:
								wid_elm.value = dict["default"]
						except Exception as e:
							print(e)
							print(traceback.format_exc())
				self.verify_preset_vals()

		_widget_hw.append(self.btn_hw_def)
			
		self.container_hw = Container(name='HW', widgets=_widget_hw)
			
		# == MISC ==
		self.gui_elms["misc"] = {}
		_widget_misc = []

		_misc_widget = QWidget()
		_layout_misc = QFormLayout(_misc_widget)
		_layout_misc.setLabelAlignment(Qt.AlignLeft)
		_layout_misc.setFormAlignment(Qt.AlignRight)
		
		for key in self.lf_vals["misc"]:
			dict = self.lf_vals["misc"][key]
			wid_elm = create_widget(dict)
			self.gui_elms["misc"][key] = wid_elm
			_widget_misc.append(wid_elm)
			if dict["type"] == "bool":
				_layout_misc.addRow(wid_elm.native)
			else:
				_layout_misc.addRow(wid_elm.label, wid_elm.native)
				
		self.btn_misc_def = PushButton(name='RTD', label='Reset to Defaults')
		@self.btn_misc_def.changed.connect
		def btn_misc_defaults():
			qm = QMessageBox
			ret = qm.question(QWidget(),'', "Reset Values to Default ?", qm.Yes | qm.No)
			if ret == qm.Yes:
				for key in self.lf_vals["misc"]:
					dict = self.lf_vals["misc"][key]
					wid_elm = self.gui_elms["misc"][key]
					if key != "lib_ver_label" or (key == "lib_ver_label" and str(self.gui_elms["misc"]["lib_folder"].value) != str(self.lf_vals["misc"]["lib_folder"]["default"])):
						if dict["type"] == "int" and type(wid_elm.value).__name__ == "str":
							try:
								wid_elm.value = wid_elm.choices[dict["default"]]
							except Exception as e:
								print(e)
								print(traceback.format_exc())
						else:
							try:
								if wid_elm.widget_type == 'ComboBox':
									if dict["default"] in wid_elm.choices:
										wid_elm.value = dict["default"]
									elif len(wid_elm.choices) == 0:
										pass
									else:
										wid_elm.value = wid_elm.choices[0]
								else:
									wid_elm.value = dict["default"]
							except Exception as e:
								print(e)
								print(traceback.format_exc())
				self.verify_preset_vals()
				
		_layout_misc.addRow(self.btn_misc_def.native)
		
		self.btn_all_def = PushButton(name='RTD', label='Reset ALL Settings to Defaults')
		@self.btn_all_def.changed.connect
		def btn_all_defaults():
			qm = QMessageBox
			ret = qm.question(QWidget(),'', "Reset ALL Values to Default ?", qm.Yes | qm.No)
			if ret == qm.Yes:
				btn_cal_req_defaults()
				btn_cal_opt_defaults()
				btn_rec_req_defaults()
				btn_rec_opt_defaults()
				btn_dec_req_defaults()
				btn_dec_opt_defaults()
				btn_hw_defaults()
				btn_misc_defaults()
				self.gui_elms["main"]["comments"].value = self.lf_vals["main"]["comments"]["default"]
				self.verify_preset_vals()
			
		_line = QFrame()
		_line.setMinimumWidth(1)
		_line.setFixedHeight(2)
		_line.setFrameShape(QFrame.HLine)
		_line.setFrameShadow(QFrame.Sunken)
		_line.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
		_line.setStyleSheet("margin:1px; padding:1px; border:1px solid rgb(128,128,128); border-width: 1px;")
		
		_layout_misc.addRow(_line)
		_layout_misc.addRow(self.btn_all_def.native)
		
		self.container_lfa = _misc_widget
		
		# bind values between props
		@self.gui_elms["calibrate"]["ulens_focal_length"].changed.connect
		def copy_vals():
			self.gui_elms["calibrate"]["ulens_focal_distance"].value = self.gui_elms["calibrate"]["ulens_focal_length"].value
		
		@self.btn_preset_load.changed.connect
		def load_presets():
			preset_sel = self.gui_elms["main"]["presets"].value
			if preset_sel is not None and preset_sel != "":
				if "preset_choices" in self.settings:
					if preset_sel in self.settings["preset_choices"]:
						loaded_preset_vals = self.settings["preset_choices"][preset_sel]
						for section in loaded_preset_vals:
							for prop in loaded_preset_vals[section]:
								try:
									if self.gui_elms[section][prop].widget_type == 'ComboBox':
										if loaded_preset_vals[section][prop] in self.gui_elms[section][prop].choices:
											self.gui_elms[section][prop].value = loaded_preset_vals[section][prop]
										elif len(self.gui_elms[section][prop].choices) == 0:
											pass
										else:
											self.gui_elms[section][prop].value = self.gui_elms[section][prop].choices[0]
									else:
										self.gui_elms[section][prop].value = loaded_preset_vals[section][prop]
								except Exception as e:
									print(e)
									print(traceback.format_exc())
			
		@self.btn_preset_save.changed.connect
		def save_presets():
			name = self.get_preset_name()
			if name == None:
				return
			if "preset_choices" not in self.settings:
				self.settings["preset_choices"] = {}
			
			preset_vals = {}
			for section in ["calibrate", "rectify", "deconvolve"]:
				preset_vals[section] = {}
				for prop in LFvals.PLUGIN_ARGS[section]:
					if "exclude_from_settings" in LFvals.PLUGIN_ARGS[section][prop] and LFvals.PLUGIN_ARGS[section][prop]["exclude_from_settings"] == True:
						pass
					else:
						if LFvals.PLUGIN_ARGS[section][prop]["type"] in ["file","folder","str"]:
							preset_vals[section][prop] = str(self.gui_elms[section][prop].value)
						else:
							preset_vals[section][prop] = self.gui_elms[section][prop].value
			
			self.settings["preset_choices"][name] = preset_vals
			self.save_plugin_prefs()
			self.refresh_preset_choices()
			self.gui_elms["main"]["presets"].value = name
			
		@self.btn_preset_delete.changed.connect
		def delete_presets():
			preset_sel = self.gui_elms["main"]["presets"].value
			if preset_sel is not None and preset_sel != "":
				if "preset_choices" in self.settings:
					if preset_sel in self.settings["preset_choices"]:
						del(self.settings["preset_choices"][preset_sel])
						self.save_plugin_prefs()
						self.refresh_preset_choices()
		
		@self.gui_elms["calibrate"]["calibration_files"].changed.connect
		def cal_img_list_inspect():
			img_selected = str(self.gui_elms["calibrate"]["calibration_files"].value)
			img_folder = str(self.gui_elms["main"]["img_folder"].value)
			img_file_path = os.path.join(img_folder, img_selected)
			
			import h5py
			
			str_data = []
			with h5py.File(img_file_path, "r") as f:
				# List all groups
				groups = f.keys()
				str_data.append("=== Groups: %s ===" % list(groups))
				str_data.append("\n")
				for group in groups:
					str_data.append("--- Group: %s ---" % group)
					str_data.append("\n")
					# Get the data
					data_grp = f[group]
					str_data.append("-- %s --" % data_grp)
					str_data.append("\n")
					for data_key in data_grp:
						data = data_grp[data_key]
						str_data.append(str(data))
						str_data.append("\n")
				str_data.append("====================")
				
			self.gui_elms["calibrate"]["calibration_files_viewer"].value = ' '.join(str_data)
		
		# ==================================
		
		self.qtab_widget = QTabWidget()
		
		self.cal_tab = QWidget()
		_cal_tab_layout = QVBoxLayout()
		_cal_tab_layout.setAlignment(Qt.AlignTop)
		self.cal_tab.setLayout(_cal_tab_layout)
		_cal_tab_layout.addWidget(self.widget_calibrate_req.native)
		
		self.cal_tab2 = QWidget()
		_cal_tab_layout2 = QVBoxLayout()
		_cal_tab_layout2.setAlignment(Qt.AlignTop)
		self.cal_tab2.setLayout(_cal_tab_layout2)
		
		self.cal_tab3 = QWidget()
		_cal_tab_layout3 = QVBoxLayout()
		_cal_tab_layout3.setAlignment(Qt.AlignTop)
		self.cal_tab3.setLayout(_cal_tab_layout3)
		
		_scroll_cal_req = QScrollArea()
		_scroll_cal_req.setWidgetResizable(True)
		_scroll_cal_req.setWidget(self.widget_calibrate_req.native)
		_cal_tab_layout.addWidget(_scroll_cal_req)
		
		_scroll_cal_opt = QScrollArea()
		_scroll_cal_opt.setWidgetResizable(True)
		_scroll_cal_opt.setWidget(self.widget_calibrate_opt.native)
		_cal_tab_layout2.addWidget(_scroll_cal_opt)
		
		_scroll_cal_ins = QScrollArea()
		_scroll_cal_ins.setWidgetResizable(True)
		_scroll_cal_ins.setWidget(self.widget_calibrate_ins.native)
		_cal_tab_layout3.addWidget(_scroll_cal_ins)
		
		self.qtab_cal_tabWidget = QTabWidget()
		self.qtab_cal_tabWidget.setTabPosition(QTabWidget.South)
		self.qtab_cal_tabWidget.addTab(self.cal_tab, 'Required')
		self.qtab_cal_tabWidget.addTab(self.cal_tab2, 'Optional')
		self.qtab_cal_tabWidget.addTab(self.cal_tab3, 'Inspect')
		self.qtab_widget.addTab(self.qtab_cal_tabWidget, 'Calibrate')
		
		self.rec_tab = QWidget()
		_rec_tab_layout = QVBoxLayout()
		_rec_tab_layout.setAlignment(Qt.AlignTop)
		self.rec_tab.setLayout(_rec_tab_layout)
		_rec_tab_layout.addWidget(self.widget_rectify_req.native)
		
		self.rec_tab2 = QWidget()
		_rec_tab_layout2 = QVBoxLayout()
		_rec_tab_layout2.setAlignment(Qt.AlignTop)
		self.rec_tab2.setLayout(_rec_tab_layout2)
		_rec_tab_layout2.addWidget(self.widget_rectify_opt.native)
		
		self.qtab_rec_tabWidget = QTabWidget()
		self.qtab_rec_tabWidget.setTabPosition(QTabWidget.South)
		self.qtab_rec_tabWidget.addTab(self.rec_tab, 'Required')
		self.qtab_rec_tabWidget.addTab(self.rec_tab2, 'Optional')
		self.qtab_widget.addTab(self.qtab_rec_tabWidget, 'Rectify')
		
		self.dec_tab = QWidget()
		_dec_tab_layout = QVBoxLayout()
		_dec_tab_layout.setAlignment(Qt.AlignTop)
		self.dec_tab.setLayout(_dec_tab_layout)
		_dec_tab_layout.addWidget(self.widget_deconvolve_req.native)
		
		self.dec_tab2 = QWidget()
		_dec_tab_layout2 = QVBoxLayout()
		_dec_tab_layout2.setAlignment(Qt.AlignTop)
		self.dec_tab2.setLayout(_dec_tab_layout2)
		
		_scroll_dec_opt = QScrollArea()
		_scroll_dec_opt.setWidgetResizable(True)
		_scroll_dec_opt.setWidget(self.widget_deconvolve_opt.native)
		_dec_tab_layout2.addWidget(_scroll_dec_opt)
		
		self.qtab_dec_tabWidget = QTabWidget()
		self.qtab_dec_tabWidget.setTabPosition(QTabWidget.South)
		self.qtab_dec_tabWidget.addTab(self.dec_tab, 'Required')
		self.qtab_dec_tabWidget.addTab(self.dec_tab2, 'Optional')
		self.qtab_widget.addTab(self.qtab_dec_tabWidget, 'Deconvolve')
		
		self.hardware_tab = QWidget()
		_hardware_tab_layout = QVBoxLayout()
		_hardware_tab_layout.setAlignment(Qt.AlignTop)
		self.hardware_tab.setLayout(_hardware_tab_layout)
		self.hardware_tab.layout().addWidget(self.container_hw.native)
		self.qtab_widget.addTab(self.hardware_tab, 'Hardware')
		
		self.lfa_lib_tab = QWidget()
		_lfa_lib_tab_layout = QVBoxLayout()
		_lfa_lib_tab_layout.setAlignment(Qt.AlignTop)
		self.lfa_lib_tab.setLayout(_lfa_lib_tab_layout)
		self.lfa_lib_tab.layout().addWidget(self.container_lfa)
		self.qtab_widget.addTab(self.lfa_lib_tab, 'Misc')
		
		# self.calib_tab = QWidget()
		# _calib_tab_layout = QVBoxLayout()
		# _calib_tab_layout.setAlignment(Qt.AlignTop)
		# self.calib_tab.setLayout(_calib_tab_layout)
		# self.qtab_widget.addTab(self.calib_tab, 'Calibrate Grid')
		# self.LFD_frame = QMainWindow()
		# self.LFD_frame.setStyleSheet("margin:1px; padding:1px; border:1px solid rgb(0, 0, 255); border-width: 1px;")
		# _calib_tab_layout.addWidget(self.LFD_frame)
		
		#APP
		self.widget_main_top_comps = Container(widgets=(), labels=True)
		self.widget_main_top_comps.native.layout().addWidget(self.cont_btn_status)
		
		self.gui_elms["main"]["comments"].parent.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
		
		self.widget_main_bottom_comps = Container(widgets=(), labels=True)
		self.widget_main_bottom_comps.native.layout().addWidget(self.qtab_widget)
		
		self.timer = QTimer()
		self.timer.timeout.connect(self.verify_existing_files)
		self.timer.start(500)
		
	def verify_existing_files(self):
		
		try:
			_img_folder = str(self.gui_elms["main"]["img_folder"].value)
			path = Path(_img_folder)
			if path.is_dir():
			
				_cal_out = self.gui_elms["calibrate"]["output_filename"].value
				_rec_out = self.gui_elms["rectify"]["output_filename"].value
				_dec_out = self.gui_elms["deconvolve"]["output_filename"].value
				
				_alert_symbol = ' ⚠️'

				_file_path = os.path.join(_img_folder, _cal_out)		
				path = Path(_file_path)
				if path.is_file():
					self.gui_elms["calibrate"]["output_filename"].native.setStyleSheet("margin:1px; padding:1px; border:1px solid rgb(255, 255, 0); border-width: 1px;")
					if self.lf_vals["misc"]["group_params"]["value"] == True:
						i, j = self.groupbox["calibrate"]["required"]["Files"].layout().getWidgetPosition(self.gui_elms["calibrate"]["output_filename"].native)
						widget_item = self.groupbox["calibrate"]["required"]["Files"].layout().itemAt(i, j-1)
						widget = widget_item.widget()
						widget.setText(self.gui_elms["calibrate"]["output_filename"].label + _alert_symbol)
						widget.setToolTip("A filed named '{out_file}' already exists in this folder!\nYou can continue but it will overwrite the existing file.".format(out_file = self.gui_elms["calibrate"]["output_filename"].value))			
				else:
					self.gui_elms["calibrate"]["output_filename"].native.setStyleSheet("margin:1px; padding:1px; border:1px solid rgb(0, 0, 0); border-width: 1px;")
					if self.lf_vals["misc"]["group_params"]["value"] == True:
						i, j = self.groupbox["calibrate"]["required"]["Files"].layout().getWidgetPosition(self.gui_elms["calibrate"]["output_filename"].native)
						widget_item = self.groupbox["calibrate"]["required"]["Files"].layout().itemAt(i, j-1)
						widget = widget_item.widget()
						widget.setText(self.gui_elms["calibrate"]["output_filename"].label)
						widget.setToolTip("")
					
				
				_file_path = os.path.join(_img_folder, _rec_out)		
				path = Path(_file_path)
				if path.is_file():
					self.gui_elms["rectify"]["output_filename"].native.setStyleSheet("margin:1px; padding:1px; border:1px solid rgb(255, 255, 0); border-width: 1px;")
					if self.lf_vals["misc"]["group_params"]["value"] == True:
						i, j = self.groupbox["rectify"]["required"]["Files"].layout().getWidgetPosition(self.gui_elms["rectify"]["output_filename"].native)
						widget_item = self.groupbox["rectify"]["required"]["Files"].layout().itemAt(i, j-1)
						widget = widget_item.widget()
						widget.setText(self.gui_elms["rectify"]["output_filename"].label + _alert_symbol)
						widget.setToolTip("A filed named '{out_file}' already exists in this folder!\nYou can continue but it will overwrite the existing file.".format(out_file = self.gui_elms["rectify"]["output_filename"].value))
				else:
					self.gui_elms["rectify"]["output_filename"].native.setStyleSheet("margin:1px; padding:1px; border:1px solid rgb(0, 0, 0); border-width: 1px;")
					if self.lf_vals["misc"]["group_params"]["value"] == True:
						i, j = self.groupbox["rectify"]["required"]["Files"].layout().getWidgetPosition(self.gui_elms["rectify"]["output_filename"].native)
						widget_item = self.groupbox["rectify"]["required"]["Files"].layout().itemAt(i, j-1)
						widget = widget_item.widget()
						widget.setText(self.gui_elms["rectify"]["output_filename"].label)
						widget.setToolTip("")
					
				
				_file_path = os.path.join(_img_folder, _dec_out)		
				path = Path(_file_path)
				if path.is_file():
					self.gui_elms["deconvolve"]["output_filename"].native.setStyleSheet("margin:1px; padding:1px; border:1px solid rgb(255, 255, 0); border-width: 1px;")
					if self.lf_vals["misc"]["group_params"]["value"] == True:
						i, j = self.groupbox["deconvolve"]["required"]["Files"].layout().getWidgetPosition(self.gui_elms["deconvolve"]["output_filename"].native)
						widget_item = self.groupbox["deconvolve"]["required"]["Files"].layout().itemAt(i, j-1)
						widget = widget_item.widget()
						widget.setText(self.gui_elms["deconvolve"]["output_filename"].label + _alert_symbol)
						widget.setToolTip("A filed named '{out_file}' already exists in this folder!\nYou can continue but it will overwrite the existing file.".format(out_file = self.gui_elms["deconvolve"]["output_filename"].value))
				else:
					self.gui_elms["deconvolve"]["output_filename"].native.setStyleSheet("margin:1px; padding:1px; border:1px solid rgb(0, 0, 0); border-width: 1px;")
					if self.lf_vals["misc"]["group_params"]["value"] == True:
						i, j = self.groupbox["deconvolve"]["required"]["Files"].layout().getWidgetPosition(self.gui_elms["deconvolve"]["output_filename"].native)
						widget_item = self.groupbox["deconvolve"]["required"]["Files"].layout().itemAt(i, j-1)
						widget = widget_item.widget()
						widget.setText(self.gui_elms["deconvolve"]["output_filename"].label)
						widget.setToolTip("")
				
			self.image_folder_changes()
		except Exception as e:
			print(e)
			print(traceback.format_exc())
			
	def verify_preset_vals(self):
		preset_sel = self.gui_elms["main"]["presets"].value
		if preset_sel is not None and preset_sel != "":
			if "preset_choices" in self.settings:
				if preset_sel in self.settings["preset_choices"]:
					loaded_preset_vals = self.settings["preset_choices"][preset_sel]
					for section in loaded_preset_vals:
						for prop in loaded_preset_vals[section]:
							try:
								if LFvals.PLUGIN_ARGS[section][prop]["type"] == "file" and (os.path.normpath(self.gui_elms[section][prop].value) in [os.path.normpath(loaded_preset_vals[section][prop])]):
									pass
								elif self.gui_elms[section][prop].value == loaded_preset_vals[section][prop]:
									pass
								else:
									#print(self.gui_elms[section][prop].value, loaded_preset_vals[section][prop])
									# self.gui_elms["main"]["presets"].native.setStyleSheet("margin:1px; padding:1px; border:1px solid rgb(255, 255, 0); border-width: 1px;")
									if "" not in self.gui_elms["main"]["presets"].choices:
										choices = self.gui_elms["main"]["presets"].choices = self.gui_elms["main"]["presets"].choices + ("",)
									self.gui_elms["main"]["presets"].value = ""
									break
							except Exception as e:
								print(e)
								print(traceback.format_exc())
		elif preset_sel == "":
			for preset_selx in self.settings["preset_choices"]:
				if preset_selx != "":
					loaded_preset_vals = self.settings["preset_choices"][preset_selx]
					for section in loaded_preset_vals:
						do_break = True
						do_exit = False
						for prop in loaded_preset_vals[section]:
							try:
								if LFvals.PLUGIN_ARGS[section][prop]["type"] == "file" and (os.path.normpath(self.gui_elms[section][prop].value) in [os.path.normpath(loaded_preset_vals[section][prop])]):
									pass
								elif self.gui_elms[section][prop].value == loaded_preset_vals[section][prop]:
									pass
								else:
									do_break = False
									do_exit = True
									break
							except Exception as e:
								print(e)
								print(traceback.format_exc())
						if do_exit:
							break
						if do_break:
							if "" in self.gui_elms["main"]["presets"].choices:
								tup_list = list(self.gui_elms["main"]["presets"].choices)
								tup_list.remove("")
								self.gui_elms["main"]["presets"].choices = tuple(tup_list)
								self.gui_elms["main"]["presets"].value = preset_selx
								# self.gui_elms["main"]["presets"].native.setStyleSheet("margin:1px; padding:1px; border:1px solid rgb(0, 0, 0); border-width: 1px;")
							break
		
	def refresh_preset_choices(self):
		preset_choices = []
		if "preset_choices" in self.settings:
			for preset in self.settings["preset_choices"]:
				preset_choices.append(preset)
		
		if len(preset_choices) > 0:
			preset_choices.sort()
		self.gui_elms["main"]["presets"].choices = preset_choices
		
	def refresh_vals(self):
		for section in LFvals.PLUGIN_ARGS:
			if section in self.lf_vals and section in self.gui_elms:
				for key in LFvals.PLUGIN_ARGS[section]:
					if key in self.lf_vals[section] and key in self.gui_elms[section]:
						dict = self.lf_vals[section][key]
						wid_elm = self.gui_elms[section][key]
						if dict["type"] in ["file","folder","str"]:
							dict["value"] = str(wid_elm.value)
						elif LFvals.PLUGIN_ARGS[section][key]["type"] == "int" and type(wid_elm.value).__name__ == "str":
							dict["value"] = self.gui_elms[section][key].native.currentIndex()
						else:
							dict["value"] = wid_elm.value
		
	def set_status_text(self, txt):
		self.cont_btn_status_label.value = txt
		self.cont_btn_status_label.native.update()
		
	def set_btns_and_status(self, btn_enab_bool, status_txt):
		self.cont_btn_status_label.value = ':STATUS: ' + status_txt
		self.btn_cal.enabled = btn_enab_bool
		self.btn_rec.enabled = btn_enab_bool
		self.btn_dec.enabled = btn_enab_bool
		
		if status_txt == LFvals.PLUGIN_ARGS['main']['status']['value_error']:
			self.cont_btn_status_label.native.setStyleSheet("border:1px solid rgb(255, 0, 0);")
		elif status_txt == LFvals.PLUGIN_ARGS['main']['status']['value_busy']:
			self.cont_btn_status_label.native.setStyleSheet("border:1px solid rgb(255, 255, 0);")
		else:
			self.cont_btn_status_label.native.setStyleSheet("border:1px solid rgb(0, 255, 0);")
		self.cont_btn_status_label.native.update()

	# ToDo - implement as directory change listener event
	def image_folder_changes(self):
		img_folder = str(self.gui_elms["main"]["img_folder"].value)
		lfc_file = str(self.gui_elms["calibrate"]["output_filename"].value)
		lfc_file_path = os.path.join(img_folder, lfc_file)
		
		path = Path(lfc_file_path)
		if path.is_file():
			self.btn_cal_prog.native.setText('✔️')
			self.btn_cal_prog.native.setStyleSheet("font-size: 16px; color: green; vertical-align: baseline;")
		else:
			self.btn_cal_prog.native.setText('')
			
		rec_file = str(self.gui_elms["rectify"]["output_filename"].value)
		rec_file_path = os.path.join(img_folder, rec_file)
		path = Path(rec_file_path)
		if path.is_file():
			self.btn_rec_prog.native.setText('✔️')
			self.btn_rec_prog.native.setStyleSheet("font-size: 16px; color: green; vertical-align: baseline;")
		else:
			self.btn_rec_prog.native.setText('')
			
		dec_file = str(self.gui_elms["deconvolve"]["output_filename"].value)
		dec_file_path = os.path.join(img_folder, dec_file)
		path = Path(dec_file_path)
		if path.is_file():
			self.btn_dec_prog.native.setText('✔️')
			self.btn_dec_prog.native.setStyleSheet("font-size: 16px; color: green; vertical-align: baseline;")
		else:
			self.btn_dec_prog.native.setText('')
		
		self.populate_img_list()
		self.populate_cal_img_list()
		
	def populate_img_list(self):
		img_folder = str(self.gui_elms["main"]["img_folder"].value)
		img_files = []
		for ext in LFvals.IMAGE_EXTS:
			files_search = "*.{file_ext}".format(file_ext=ext)
			files = glob.glob(os.path.join(img_folder, files_search))
			for file in files:
				img_files.append(ntpath.basename(file))
				
		self.gui_elms["main"]["img_list"].choices = img_files
		self.gui_elms["calibrate"]["radiometry_frame_file"].choices = img_files
		self.gui_elms["calibrate"]["dark_frame_file"].choices = img_files
		self.gui_elms["rectify"]["input_file"].choices = img_files
		self.gui_elms["deconvolve"]["input_file"].choices = img_files
		
	def populate_cal_img_list(self):
		img_folder = str(self.gui_elms["main"]["img_folder"].value)
		img_files = []
		for ext in LFvals.HDF5_EXTS:
			files_search = "*.{file_ext}".format(file_ext=ext)
			files = glob.glob(os.path.join(img_folder, files_search))
			for file in files:
				img_files.append(ntpath.basename(file))
				
		if len(img_files) == 0:
			self.gui_elms["calibrate"]["calibration_files_viewer"].value = ""
		
		self.gui_elms["calibrate"]["calibration_files"].choices = img_files
		self.gui_elms["rectify"]["calibration_file"].choices = img_files
		self.gui_elms["deconvolve"]["calibration_file"].choices = img_files
		
	def set_cal_img(self):
		cal_file = self.gui_elms["calibrate"]["output_filename"].value
		self.gui_elms["rectify"]["calibration_file"].value = cal_file
		self.gui_elms["deconvolve"]["calibration_file"].value = cal_file
		
	def openImage(self, path):
		imageViewerFromCommandLine = {'linux':'xdg-open','win32':'explorer','darwin':'open'}[sys.platform]
		subprocess.Popen([imageViewerFromCommandLine, path])
		
	def openImageExtViewer(self, path):
		imageViewerFromCommandLine = "{viewer} {cmd} {file_path}".format(viewer=self.gui_elms["misc"]["ext_viewer"].value, cmd="-file-name", file_path=path)
		subprocess.Popen(imageViewerFromCommandLine)
			
	def get_GPU(self):
		gpu_list = []
		try:
			for platform in cl.get_platforms():
				gpu_list.append(platform.name.strip('\r\n \x00\t'))
		except:
			pass
		return gpu_list
		
	def get_PlatForms(self):
		platforms_list = []
		try:
			for platform in cl.get_platforms():
				for device in platform.get_devices():
					platforms_list.append(device.name.strip('\r\n \x00\t'))
		except:
			pass
		return platforms_list
		
	def save_plugin_prefs(self):
		for section in LFvals.PLUGIN_ARGS:
			self.settings[section] = {}
			for prop in LFvals.PLUGIN_ARGS[section]:
				if "exclude_from_settings" in LFvals.PLUGIN_ARGS[section][prop] and LFvals.PLUGIN_ARGS[section][prop]["exclude_from_settings"] == True:
					pass
				else:
					if LFvals.PLUGIN_ARGS[section][prop]["type"] in ["file","folder","str"]:
						self.settings[section][prop] = str(self.gui_elms[section][prop].value)
					else:
						self.settings[section][prop] = self.gui_elms[section][prop].value
		
		settings_file_path = Path(os.path.join(self.currentdir, LFvals.SETTINGS_FILENAME))
		with open(settings_file_path, "w") as f:
			json.dump(self.settings, f, indent=4)

	def load_plugin_prefs(self, pre_init=False):
		try:
			settings_file_path = Path(os.path.join(self.currentdir, LFvals.SETTINGS_FILENAME))
			if settings_file_path.is_file() is False:
				self.save_plugin_prefs()
			else:
				with open(settings_file_path, "r") as f:
					self.settings = json.load(f)
					
				for section in LFvals.PLUGIN_ARGS:
					for prop in LFvals.PLUGIN_ARGS[section]:
						try:
							if prop in LFvals.PLUGIN_ARGS[section] and prop in self.settings[section]:
								LFvals.PLUGIN_ARGS[section][prop]["value"] = self.settings[section][prop]
							if pre_init == False and prop in self.gui_elms[section] and prop in self.settings[section]:
								try:
									if self.gui_elms[section][prop].widget_type == 'ComboBox':
										if self.settings[section][prop] in self.gui_elms[section][prop].choices:
											self.gui_elms[section][prop].value = self.settings[section][prop]
										elif len(self.gui_elms[section][prop].choices) == 0:
											#self.gui_elms[section][prop].value = ""
											pass
										else:
											self.gui_elms[section][prop].value = self.gui_elms[section][prop].choices[0]
									else:
										self.gui_elms[section][prop].value = self.settings[section][prop]
								except Exception as e:
									print(e)
									print(traceback.format_exc())
						except Exception as e:
							print(e)
							print(traceback.format_exc())
				if pre_init == False:
					bool = self.read_meta()
					if bool:
						self.refresh_vals()
					self.image_folder_changes()
					self.refresh_preset_choices()
			
		except Exception as e:
			print(e)
			print(traceback.format_exc())
			self.settings = {}
			
	def write_meta(self):
		try:
			meta_data = {}
			section = "main"
			meta_data[section] = {}
			prop = "comments"
			meta_data[section][prop] = str(self.gui_elms[section][prop].value)
			
			for section in ['calibrate','rectify','deconvolve','hw']:
				meta_data[section] = {}
				for prop in LFvals.PLUGIN_ARGS[section]:
					if "exclude_from_metadata" in LFvals.PLUGIN_ARGS[section][prop] and LFvals.PLUGIN_ARGS[section][prop]["exclude_from_metadata"] == True:
						pass
					else:
						if LFvals.PLUGIN_ARGS[section][prop]["type"] in ["file","folder","str"]:
							meta_data[section][prop] = str(self.gui_elms[section][prop].value)
						else:
							meta_data[section][prop] = self.gui_elms[section][prop].value
			
			metadata_file_path = Path(self.gui_elms["main"]["img_folder"].value, self.gui_elms["main"]["metadata_file"].value)
			with open(metadata_file_path, "w") as f:
				json.dump(meta_data, f, indent=4)
		except Exception as e:
			print(e)
			print(traceback.format_exc())
			
	def read_meta(self):
		try:
			path = Path(os.path.join(self.gui_elms["main"]["img_folder"].value, self.gui_elms["main"]["metadata_file"].value))
			if path.is_file():
				with open(os.path.join(self.gui_elms["main"]["img_folder"].value, self.gui_elms["main"]["metadata_file"].value)) as json_file:
					meta_data = json.load(json_file)
					
				for section in meta_data:
					for prop in meta_data[section]:
						if prop in self.gui_elms[section] and prop in meta_data[section]:
							try:
								if self.gui_elms[section][prop].widget_type == "ComboBox":
									if meta_data[section][prop] in self.gui_elms[section][prop].choices:
										self.gui_elms[section][prop].value = meta_data[section][prop]
									elif len(self.gui_elms[section][prop].choices) == 0:
										#self.gui_elms[section][prop].value = ""
										pass
									else:
										self.gui_elms[section][prop].value = self.gui_elms[section][prop].choices[0]
								else:
									self.gui_elms[section][prop].value = meta_data[section][prop]
							except Exception as e:
								print(self.gui_elms[section][prop].widget_type)
								print(e)
								print(traceback.format_exc())
					
				return True
			else:
				return False
		except Exception as e:
			print(e)
			print(traceback.format_exc())
			return False
			
	def get_preset_name(self):
		text, ok = QInputDialog.getText(QWidget(), 'Input Dialog', 'Enter preset name:')
		
		if ok:
			if "preset_choices" in self.settings:
				for preset in self.settings["preset_choices"]:
					if preset == text:
						qm = QMessageBox
						ret = qm.question(QWidget(),'', "Preset name already exists, overwirte ?", qm.Yes | qm.No)
						if ret == qm.Yes:
							return (str(text))
						else:
							return None
			return (str(text))
		return None
		
	def dump_errors(self, currentdir, err, traceback=False):
		t_stamp = time.strftime("%Y-%m-%d %H:%M:%S")
		contents = t_stamp + '\t' + str(err)
		err_file_name = time.strftime("%Y_%m_%d") + '.log'
		
		errorLogsDir = os.path.join(currentdir, 'errorLogs')
		if Path(errorLogsDir).is_dir() == False:
			os.mkdir(errorLogsDir)
		
		err_file_path = Path(os.path.join(errorLogsDir, err_file_name))
		if Path(err_file_path).is_file():
			with open(err_file_path, "r") as f:
				contents = f.read()
				if traceback:
					contents = t_stamp + '\t' + str(err) + contents
				else:
					contents = t_stamp + '\t' + str(err) + '\n' + contents
			
		with open(err_file_path, "w") as f:
			f.write(str(contents))

def create_widget(props):
	widget = None
	try:
		if "widget_type" in props:
			widget = create_widget(widget_type=props['widget_type'], tooltip=props['help'])
		elif props["type"] == "str":
			widget = LineEdit(label=props['label'], tooltip=props['help'])
		elif props["type"] == "text":
			widget = TextEdit(label=props['label'], tooltip=props['help'])
		elif props["type"] == "label":
			widget = Label(label=props['label'], tooltip=props['help'])
		elif props["type"] == "img_label":
			widget = Label(label=props['label'], tooltip=props['help'])
		elif props["type"] == "float":
			widget = FloatSpinBox(label=props['label'], tooltip=props['help'], step=0.01)
		elif props["type"] == "int":
			widget = SpinBox(label=props['label'], tooltip=props['help'], step=1)
		elif props["type"] == "sel":
			widget = ComboBox(label=props['label'], tooltip=props['help'], value=props["options"][0], choices=(props["options"]))
		elif props["type"] == "file":
			widget = FileEdit(label=props['label'], mode='r', tooltip=props['help'], nullable=True)
		elif props["type"] == "folder":
			widget = FileEdit(label=props['label'], mode='d', tooltip=props['help'], nullable=True)
		elif props["type"] == "bool":	
			widget = CheckBox(label=props['label'], tooltip=props['help'])
		else:
			pass
			
		if widget != None:
			# if "max" in props:
				# widget.max = props["max"]
			# if "step" in props:
				# widget.step = props["step"]
			
			if widget.widget_type == "LineEdit":
				widget.min_width = 100
				widget.native.setStyleSheet("background-color:black;")
				
			for prop in props:
				try:
					getattr(widget, prop)
					setattr(widget, prop, props[prop])
				except:
					pass
				
			widget.value = props["default"]
			
	except Exception as e:
		print(props)
		print(e)
		print(traceback.format_exc())
	return widget