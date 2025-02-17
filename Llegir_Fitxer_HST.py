import struct
import datetime

def convert_filetime_to_datetime(filetime_ticks):
    """
    Converteix un FILETIME (ticks, 100 ns intervals des del 1/1/1601) a un objecte datetime UTC.
    """
    offset = 116444736000000000
    seconds = (filetime_ticks - offset) / 10000000
    return datetime.datetime.utcfromtimestamp(seconds)

def llegir_arxiu_hst(file_path):
    """
    Llegeix un fitxer *.hst que conté:
      - MASTERHEADER (176 bytes):
          Title      : 128 CHAR
          ID         : 8 CHAR
          Type       : 2 UINT
          Version    : 2 UINT
          Alignment  : 4 bytes (ignora)
          Mode       : 4 UINT
          History    : 2 UINT
          nFiles     : 2 UINT
          Next       : 2 UINT
          AddOn      : 2 UINT
          Alignment  : 20 bytes (ignora)
      - Seguit per tants HSTFILEHEADER com indiqui el camp "nFiles".
      
    La nova definició de cada HSTFILEHEADER és:
          Name         : 272 CHAR
          ID           : 8 CHAR
          Type         : 2 UINT
          Version      : 2 UINT
          StartEvNo    : 8 INT
          Alignment    : 12 bytes (ignora)
          LogName      : 80 CHAR
          Mode         : 4 UINT
          Area         : 2 UINT
          Priv         : 2 UINT
          FileType     : 2 UINT
          SamplePeriod : 4 UINT
          sEngUnits    : 8 CHAR
          Format       : 4 UINT
          StartTime    : 8 UINT
          EndTime      : 8 UINT
          DataLength   : 4 UINT
          FilePointer  : 4 UINT
          EndEvNo      : 8 INT
          Alignment    : 6 bytes (ignora)
    """
    try:
        with open(file_path, 'rb') as f:
            # Llegir el MASTERHEADER (176 bytes)
            master_bytes = f.read(176)
            if len(master_bytes) < 176:
                raise Exception("El fitxer és massa petit per contindre un MASTERHEADER vàlid.")
            master_format = "<128s8sHH4xIHHHH20x"
            master_unpack = struct.unpack(master_format, master_bytes)
            master_header = {
                "Title": master_unpack[0].decode('latin-1').strip('\x00'),
                "ID": master_unpack[1].decode('latin-1').strip('\x00'),
                "Type": master_unpack[2],
                "Version": master_unpack[3],
                "Mode": master_unpack[4],
                "History": master_unpack[5],
                "nFiles": master_unpack[6],
                "Next": master_unpack[7],
                "AddOn": master_unpack[8]
            }
            
            # Llegir cada HSTFILEHEADER segons el camp 'nFiles'
            nFiles = master_header["nFiles"]
            hstfile_headers = []
            hst_header_format = "<272s8sHHq12x80sIHHHI8sIQQIIq6x"
            header_size = struct.calcsize(hst_header_format)  # 448 bytes
            for i in range(nFiles):
                header_bytes = f.read(header_size)
                if len(header_bytes) != header_size:
                    raise Exception(f"Error en la lectura del HSTFILEHEADER {i+1}.")
                unpacked = struct.unpack(hst_header_format, header_bytes)
                header_dict = {
                    "Name":         unpacked[0].decode('latin-1').strip('\x00'),
                    "ID":           unpacked[1].decode('latin-1').strip('\x00'),
                    "Type":         unpacked[2],
                    "Version":      unpacked[3],
                    "StartEvNo":    unpacked[4],
                    "LogName":      unpacked[5].decode('latin-1').strip('\x00'),
                    "Mode":         unpacked[6],
                    "Area":         unpacked[7],
                    "Priv":         unpacked[8],
                    "FileType":     unpacked[9],
                    "SamplePeriod": unpacked[10],
                    "sEngUnits":    unpacked[11].decode('latin-1').strip('\x00'),
                    "Format":       unpacked[12],
                    "StartTime":    convert_filetime_to_datetime(unpacked[13]),
                    "EndTime":      convert_filetime_to_datetime(unpacked[14]),
                    "DataLength":   unpacked[15],
                    "FilePointer":  unpacked[16],
                    "EndEvNo":      unpacked[17]
                }
                hstfile_headers.append(header_dict)
                
            return master_header, hstfile_headers
    except Exception as e:
        print(f"Error al llegir el fitxer HST: {e}")
        return None, None

