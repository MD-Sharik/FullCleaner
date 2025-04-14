import dearpygui.dearpygui as dpg

def on_click():
    print("Button clicked!")

dpg.create_context()
dpg.create_viewport(title='Example', width=400, height=300)
dpg.setup_dearpygui()

with dpg.window(label="Main Window",width=400,height=300):
    dpg.add_button(label="Click Me", callback=on_click)

dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()