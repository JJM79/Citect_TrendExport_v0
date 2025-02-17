# Exportador de CSV per Subcarpetes

Aquest projecte és una aplicació d'escriptori desenvolupada en Python amb CustomTkinter per visualitzar i processar fitxers d'un format propietari (HTS / 0xx). La interfície gràfica permet:

- Seleccionar una carpeta d'origen.
- Mostrar les subcarpetes que contenen la cadena "TR2".
- Filtrar la llista de subcarpetes en temps real (amb debounce per millorar la resposta).
- Seleccionar subcarpetes mitjançant interruptors (CTkSwitch) que, quan s'activen, canvien el color del text.
- Exportar a CSV les dades llegides dels fitxers de cada subcarpeta seleccionada.

## Característiques Principals

- **Filtrat dinàmic amb debounce**: S'actualitzen els elements mostrats a mesura que es tecleja, evitant redibuixos innecessaris i millorant la resposta.
- **Selecció amb CTkSwitch**: Cada subcarpeta es mostra amb un interruptor, i en activar-se actualitza el seu aspecte (canviant el color del text a blau) sense redibuixar tota la llista si està visible.
- **Processament de fitxers**:  
  - Els fitxers amb extensió `.hst` contenen la capçalera i nombres d'encapçalaments amb informació dels fitxers de dades.
  - Els fitxers de dades (`*.0xx`) contenen registres amb "value" i "time".  
  Les funcions `llegir_arxiu_hst` i `llegir_header_datafile` / `llegir_dades` (en els fitxers `Llegir_Fitxer_HST.py` i `Llegir_Fitxer_Dades.py`) s'encarreguen d'extreure aquesta informació i convertir els timestamps a un format de data/hora.

## Estructura del Projecte

```
/Citect
 ├── main_gui.py           # Interfície principal de l'aplicació.
 ├── Llegir_Fitxer_HST.py  # Funcions per llegir i interpretar el fitxer HST.
 └── Llegir_Fitxer_Dades.py# Funcions per llegir les capçaleres i les dades dels fitxers *.0xx.
```

## Requisits i Dependències

- Python 3.x  
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)  
- Mòduls estàndard de Python: `os`, `csv`, `struct`, `datetime`, `tkinter`

Instal·la CustomTkinter (si encara no ho has fet):

```
pip install customtkinter
```

## Ús de l'Aplicació

1. Executa `main_gui.py` per iniciar l'aplicació:
   ```
   python main_gui.py
   ```

2. **Selecciona la carpeta d'origen**:  
   Fes clic en el botó "Selecciona carpeta d'origen". L'aplicació cercarà subcarpetes que continguin "TR2" i actualitzarà la llista mostrada.

3. **Filtra i selecciona subcarpetes**:  
   Utilitza el camp de filtrat per cercar una subcarpeta específica i activa els interruptors (CTkSwitch) per seleccionar les subcarpetes que vols exportar.
   
4. **Exporta a CSV**:  
   Prem el botó "Exporta a CSV" i selecciona la carpeta on es desarà el fitxer CSV. L'aplicació processarà cada subcarpeta seleccionada, llegint el fitxer `.hst` i els fitxers de dades, generant un CSV amb les mostres ordenades per temps.

## Consideracions de Implementació

- Quan el filtre està actiu, si l'element sobre el qual es fa una selecció és visible (és present al diccionari `self.item_widgets`), es modifica directament la seva aparença per evitar redibuixos complets.  
- En cas contrari, es redibuixa la llista filtrada per garantir la coherència de la vista.
- Es fa servir el mètode `after()` per implementar un sistema de debounce en el filtrat, millorant la resposta i reduint la càrrega en la interfície.

## Contacte i Col·laboració

Si tens dubtes o suggeriments de millora, pots comentar directament al repositori o contactar amb l'autor del projecte.
