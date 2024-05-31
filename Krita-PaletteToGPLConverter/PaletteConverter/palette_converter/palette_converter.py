import xml.etree.ElementTree as ET
from krita import *
from PyQt5.QtWidgets import QFileDialog, QDialog, QHBoxLayout , QVBoxLayout , QPushButton, QLabel, QMessageBox, QComboBox


class PaletteConverter(Extension):
    # setup
    def __init__(self, parent):
        super().__init__(parent)
        self.resources : dict = Application.resources("palette")
        self.window = None

    def setup(self):
        pass
    
    def createActions(self, window) -> None:
        self.window = window
        action = self.window.createAction("PaletteConverter", "PaletteConverter", "tools/scripts/PaletteConverter")
        action.triggered.connect(self.show_dialog)
        
    
    # Helper functions  
    def parse_XML(self,xml: str) -> tuple:
        
        # parse XML string
        root = ET.fromstring(xml)
    
        # find RGB element
        rgb = root.find(".//RGB")
        r = float(rgb.get("r"))
        g = float(rgb.get("g"))
        b = float(rgb.get("b"))
    
        return r,g,b

    def float_to_int(self,value: float) -> int:
        return int(value * 255)

    def get_palette(self,title : str) -> list:
        """Will return a dictionary representation of the given palette
    
        Keyword arguments:
        @title -- Name of the palette
        Return: list of every colors in the palette each as a dictionnary containing the name and rgb values
        """
        color_lst = []
        palette = self.resources.get(title,None)
    
        if palette:
            palette = Palette(palette)
            num_entries = palette.numberOfEntries()
            for x in range(num_entries):
            
                # entry represent a "Swatch" object that is a single color 
                entry = palette.colorSetEntryByIndex(x)
                name = entry.name()
                (r,g,b) = self.parse_XML(entry.color().toXML())
                # quick conversion of r,g and b to int
                (r,g,b) = tuple(map(lambda x: self.float_to_int(x), (r,g,b)))
                color_lst.append({"name": name, "r" : r, "g": g, "b": b})
            
            return color_lst
        
    def create_gpl_file(self,palette: list,filename: str,title: str) -> None:
        num_value = len(palette)
        with open(filename, "w") as file:
            # header
            file.write(f"GIMP Palette\nName: {title}\nColumns: {num_value}\n#\n")
        
            # color entry
            for color_data in palette:
                name = color_data["name"]
                r = color_data["r"]
                g = color_data["g"]
                b = color_data["b"]
            
                file.write(f"{r} {g} {b} {name}\n")
                
    def convert_palette(self) -> None:
        name = self.palette_list.currentText()
        color_lst = self.get_palette(name)
        if len(color_lst) > 0:
            file_path, _ = QFileDialog.getSaveFileName(None, "Save Palette File", "", "GIMP Palette (*.gpl)")
            
            if file_path:
                # check if the file has the correct file extension
                if not file_path.endswith(".gpl"):
                    file_path += ".gpl"
                
                try:
                    # create a .gpl file
                    self.create_gpl_file(color_lst,file_path,name)
                    QMessageBox.information(None, "Success","Palette successfully generated")
                except Exception as e:
                    QMessageBox.critical(None, "Error",f"An error occured {str(e)}")
                    
     
    def populate_list(self) -> None:
        lst = list(self.resources.keys())
        self.palette_list.addItems(lst)
        
        
    # setting up the UI
    
    def show_dialog(self) -> None:
        # layout
        main_layout = QVBoxLayout()
        layout = QHBoxLayout() 
        
        # list view
        self.palette_list = QComboBox()
        self.populate_list()
        
        main_layout.addWidget(QLabel("Select a palette:"))
        main_layout.addWidget(self.palette_list)
        
        # search button
        search_btn = QPushButton("Convert")
        search_btn.clicked.connect(self.convert_palette)
        
        layout.addWidget(search_btn)
        
        # output stuff
        self.output_label = QLabel()
        # add sub layout to main
        main_layout.addLayout(layout)
        main_layout.addWidget(self.output_label)
        
        # Create dialog  
        dialog = QDialog()
        dialog.setWindowTitle("Palette Converter")
        dialog.setLayout(main_layout)
        
        # Set dialog size
        dialog.setMinimumSize(300, 200)  # Set minimum size (width, height)

        dialog.exec()
        