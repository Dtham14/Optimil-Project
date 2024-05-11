import barcode
from barcode.writer import ImageWriter

def generate_bcode(employee_num): 
    # Generate barcode
    barcode_data = employee_num
    code128 = barcode.get_barcode_class('code128')
    barcode_instance = code128(barcode_data, writer=ImageWriter())

    path = f'./barcodes/{barcode_data}'
    # Save barcode image
    barcode_instance.save(path)