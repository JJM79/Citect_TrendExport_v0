import struct
import datetime

def convert_filetime_to_datetime(filetime_ticks):
    """
    Converteix un FILETIME (ticks, intervals de 100 ns des del 1/1/1601) a un objecte datetime UTC.
    Si el càlcul resulta en un valor fora del rang, retorna None.
    """
    offset = 116444736000000000
    try:
        seconds = (filetime_ticks - offset) / 10000000
        if seconds < 0:
            return None
        return datetime.datetime.utcfromtimestamp(seconds)
    except Exception as e:
        print(f"Error convertint timestamp {filetime_ticks}: {e}")
        return None

def llegir_header_datafile(file_path):
    """
    Llegeix la capçalera 'DATAFILEHEADER' d'un fitxer binari *.0xx amb l'estructura revisada.
    
    Args:
        file_path (str): La ruta al fitxer *.0xx.
    
    Returns:
        dict: Diccionari amb els camps de la capçalera o None si hi ha error.
    """
    try:
        with open(file_path, 'rb') as f:
            header_bytes = f.read(304)
            format_string = "<112s4f8sHHq12x80sIHHHI8sIQQIIq6x"
            unpacked_header = struct.unpack(format_string, header_bytes)
            header_data = {
                "Title": unpacked_header[0].decode('latin-1').strip('\x00'),
                "scales": {
                    "RawZero": unpacked_header[1],
                    "RawFull": unpacked_header[2],
                    "EngZero": unpacked_header[3],
                    "EngFull": unpacked_header[4]
                },
                "header": {
                    "ID": unpacked_header[5].decode('latin-1').strip('\x00'),
                    "Type": unpacked_header[6],
                    "Version": unpacked_header[7],
                    "StartEvNo": unpacked_header[8],
                    "LogName": unpacked_header[9].decode('latin-1').strip('\x00'),
                    "Mode": unpacked_header[10],
                    "Area": unpacked_header[11],
                    "Priv": unpacked_header[12],
                    "FileType": unpacked_header[13],
                    "SamplePeriod": unpacked_header[14],
                    "sEngUnits": unpacked_header[15].decode('latin-1').strip('\x00'),
                    "Format": unpacked_header[16],
                    "StartTime": unpacked_header[17],
                    "EndTime": unpacked_header[18],
                    "DataLength": unpacked_header[19],
                    "FilePointer": unpacked_header[20],
                    "EndEvNo": unpacked_header[21]
                }
            }
            return header_data

    except Exception as e:
        print(f"Error al llegir la capçalera: {e}")
        return None

def llegir_dades(file_path, header_info):
    """
    Llegeix les dades del fitxer a partir de la capçalera.
    
    Args:
        file_path (str): Ruta al fitxer.
        header_info (dict): Diccionari amb les dades de la capçalera.
    
    Returns:
        list: Llista de diccionaris amb 'value' i 'time'.
    """
    try:
        with open(file_path, 'rb') as f:
            f.seek(304)
            n_samples = header_info['header']['DataLength']
            samples = []
            sample_format = "<d"
            sample_size = struct.calcsize(sample_format)
            start_dt = convert_filetime_to_datetime(header_info['header']['StartTime'])
            delta = datetime.timedelta(milliseconds=header_info['header']['SamplePeriod'])
            for i in range(n_samples):
                sample_bytes = f.read(sample_size)
                if len(sample_bytes) != sample_size:
                    print(f"Alerta: bytes insuficients a la mostra {i}")
                    break
                value = struct.unpack(sample_format, sample_bytes)[0]
                sample_time = start_dt + i * delta
                samples.append({"value": value, "time": sample_time})
            return samples
    except Exception as e:
        print(f"Error al llegir les dades: {e}")
        return None

