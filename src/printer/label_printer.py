class LabelPrinter:
    def __init__(self, printer_name):
        self.printer_name = printer_name

    def send_print_job(self, zpl_data):
        # Here you would implement the logic to send the ZPL data to the printer
        print(f"Sending print job to {self.printer_name}...")
        print(zpl_data)

    def print_label(self, label_data):
        zpl = self.generate_zpl(label_data)
        self.send_print_job(zpl)

    def generate_zpl(self, label_data):
        # This method should generate ZPL commands based on the label data
        zpl_commands = f"^XA\n^FO50,50\n^ADN,36,20\n^FD{label_data['text']}^FS\n^XZ"
        return zpl_commands