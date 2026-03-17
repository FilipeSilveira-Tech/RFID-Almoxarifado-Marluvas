import win32print

def listar_impressoras():
    flags = win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS
    printers = win32print.EnumPrinters(flags)
    nomes = [p[2] for p in printers]

    return nomes if nomes else ["Sem impressoras"]

def imprimir(printer_name, zpl):
    h = win32print.OpenPrinter(printer_name)

    win32print.StartDocPrinter(h, 1, ("RFID-Marluvas", None, "RAW"))
    win32print.WritePrinter(h, zpl.encode("utf-8"))
    win32print.EndDocPrinter(h)

    win32print.ClosePrinter(h)