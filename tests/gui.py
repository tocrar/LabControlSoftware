
	#!/usr/bin/env python
	 
import pygtk
pygtk.require('2.0')
import gtk
class MyProgram:


	def button_a_callback(self, widget, data_a):
		# function arguments
		first_fn_arg  = data_a[0]
		second_fn_arg = data_a[1]
		third_fn_arg  = data_a[2]
		fourth_fn_arg = data_a[3]
		print data_a


	def enter_callback_b(self, widget, entry_b):
		entry_text_b = entry_b.get_text()
		print "Text entry: %s\n" % entry_text_b
		return


	def __init__(self):
		 # create a new window
		 app_window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		 app_window.set_size_request(500, 350)
		 app_window.set_border_width(10)
		 app_window.set_title("MyProgram title")
		 app_window.connect("delete_event", lambda w,e: gtk.main_quit())
		 vbox_app = gtk.VBox(False, 0)
		 app_window.add(vbox_app)
		 vbox_app.show()
		 label_app = gtk.Label("Application name: ")
		 label_app.show()
		 vbox_app.pack_start(label_app, False, False, 6)


		 hbox_close = gtk.HBox(False, 0)
        	 #app_window.add(hbox_close) # attach HBox to window
		 label_close = gtk.Label("Close aplication: ")
		 hbox_close.pack_start(label_close, True, True, 0)
		 label_close.show()	 
		 button_close = gtk.Button(stock=gtk.STOCK_CLOSE)
		 button_a_data = (1,2,3,4)
		 button_close.connect("clicked",  self.button_a_callback, button_a_data)
		 button_close.set_flags(gtk.CAN_DEFAULT)
		 hbox_close.pack_start(button_close, True, True, 0)
		 button_close.show


		 # Set default text in text entry box
		 entry_checker_default_b = "abc def default text"
	        # Generate text entry box
		 entry_b = gtk.Entry()
		 entry_b.set_max_length(80)
		 entry_b.set_width_chars(50)
		 entry_b.connect("changed", self.enter_callback_b, entry_b)
		 entry_b.set_text(entry_checker_default_b)
		 entry_b.select_region(0, len(entry_b.get_text()))
		 entry_b.show()
		 hbox_close.pack_start(entry_b, False, False, 0) 



		 vbox_app.add(hbox_close)
	        # Place after association to hbox/vbox to avoid the following error:
	        # GtkWarning: gtkwidget.c:5460: widget not within a GtkWindow
		 button_close.grab_default()


		 # Program goes here  ...
		 app_window.show()
		 return
def main():
	gtk.main()
	return 0
if __name__ == "__main__":
	MyProgram()
	main()
