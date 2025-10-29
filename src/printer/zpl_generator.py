class ZplGenerator:
    def __init__(self):
        self.zpl_commands = []

    def add_text(self, x, y, text, font='0', rotation='0', width='1', height='1'):
        command = f'^FO{x},{y}^A{font},{height},{width}^FD{text}^FS'
        self.zpl_commands.append(command)

    def add_barcode(self, x, y, barcode_type, data, height='50', width='2'):
        command = f'^FO{x},{y}^BY{width}^B{barcode_type},{height},Y,N^FD{data}^FS'
        self.zpl_commands.append(command)

    def add_graphic(self, x, y, graphic_data):
        command = f'^FO{x},{y}^GFA,{len(graphic_data)},{len(graphic_data) // 2},{len(graphic_data) // 8},{graphic_data}^FS'
        self.zpl_commands.append(command)

    def generate_zpl(self):
        return '\n'.join(self.zpl_commands)

    def clear_commands(self):
        self.zpl_commands = []