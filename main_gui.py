import os
import csv
import customtkinter as ctk
from tkinter import filedialog, messagebox, BooleanVar

from Llegir_Fitxer_HST import llegir_arxiu_hst
from Llegir_Fitxer_Dades import llegir_header_datafile, llegir_dades


class FilterableItemFrame(ctk.CTkFrame):
    """
    Widget que mostra una llista filtrable d'elements amb un CTkSwitch per a cada element.
    Permet seleccionar i deseleccionar elements amb feedback visual canviant el color del text.
    """

    def __init__(self, master, item_list=None, command=None, **kwargs):
        item_list = item_list or []
        super().__init__(master, **kwargs)
        self.command = command  # Funció opcional a executar en canviar la selecció
        self.full_item_list = item_list  # Llista completa d'elements
        self.selected_items = set()  # Conjunt d'elements seleccionats
        self.item_widgets = {}  # Diccionari per emmagatzemar els widgets per a cada element

        # Entrada per filtrar amb text per defecte en negre
        self.filter_entry = ctk.CTkEntry(self, placeholder_text="Filtra...", text_color="black")
        self.filter_entry.pack(pady=(5, 10), padx=5, fill="x")
        self.filter_entry.bind("<KeyRelease>", self._on_filter_change)

        # Marc scrollable per mostrar els elements
        self.scrollable_frame = ctk.CTkScrollableFrame(self)
        self.scrollable_frame.pack(padx=5, pady=5, fill="both", expand=True)

        # Dibuixa la llista inicial
        self._draw_items(self.full_item_list)

    def _draw_items(self, items):
        """
        Dibuixa tots els elements de la llista 'items' en el scrollable_frame.
        Esborra primer els widgets existents i omple el diccionari item_widgets.
        """
        # Esborrem els widgets existents
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.item_widgets = {}
        # Dibuixem cada element com a CTkSwitch
        for i, item in enumerate(items):
            var = BooleanVar(value=(item in self.selected_items))
            color = "blue" if item in self.selected_items else "black"
            switch = ctk.CTkSwitch(
                self.scrollable_frame,
                text=item,
                text_color=color,
                variable=var,
                command=lambda item=item, var=var: self._toggle_item(item, var)
            )
            switch.grid(row=i, column=0, pady=(0, 10), padx=5, sticky="w")
            self.item_widgets[item] = switch

    def _toggle_item(self, item, var):
        """
        Alterna la selecció d'un element.
        Actualitza directament l'aspecte del widget si aquest és visible (existeix a self.item_widgets)
        i, en cas contrari, redibuixa la llista filtrada.
        """
        if var.get():
            self.selected_items.add(item)
        else:
            self.selected_items.discard(item)

        # Comprovem si el widget de l'element és visible en la llista actual
        widget = self.item_widgets.get(item)
        if widget is not None:
            new_color = "blue" if item in self.selected_items else "black"
            widget.configure(text=item, text_color=new_color)
        else:
            # Si no és visible, redibuixem la llista filtrada
            current_filter = self.filter_entry.get().strip().lower()
            filtered = [it for it in self.full_item_list if current_filter in it.lower()]
            self._draw_items(filtered)

        if self.command:
            self.command()

    def _on_filter_change(self, event):
        """Aplicació d'un debounce per evitar redibuixar la llista en cada tecla."""
        if hasattr(self, "_filter_job"):
            self.after_cancel(self._filter_job)
        self._filter_job = self.after(300, self._apply_filter)

    def _apply_filter(self):
        """Aplica el filtre segons el text introduït i redibuixa la llista."""
        filter_text = self.filter_entry.get().lower()
        filtered = [item for item in self.full_item_list if filter_text in item.lower()]
        self._draw_items(filtered)

    def update_items(self, item_list):
        """Actualitza la llista completa d'elements i reinicia la selecció."""
        self.full_item_list = item_list
        self.selected_items.clear()
        self.filter_entry.delete(0, "end")
        self._draw_items(item_list)

    def get_selected_items(self):
        """Retorna una llista dels elements seleccionats."""
        return list(self.selected_items)


def process_subfolder(source_folder, export_folder):
    """
    Processa una subcarpeta que conté:
      - Un fitxer *.hst (capçalera del fitxer)
      - Diversos fitxers de dades (*.0xx)
    Exporta tots els samples (time, value) a un CSV amb el nom de la subcarpeta.
    """
    hst_files = [f for f in os.listdir(source_folder) if f.lower().endswith(".hst")]
    if not hst_files:
        print(f"[!] No s'ha trobat fitxer .hst a {source_folder}")
        return

    hst_file = os.path.join(source_folder, hst_files[0])
    master_header, hst_headers = llegir_arxiu_hst(hst_file)
    if not master_header:
        print(f"[!] Error llegint el HST header a {source_folder}")
        return

    all_samples = []
    for header in hst_headers:
        data_filename = os.path.basename(header["Name"])
        data_file_path = os.path.join(source_folder, data_filename)
        if not os.path.exists(data_file_path):
            print(f"[!] Fitxer de dades no trobat: {data_file_path}")
            continue
        header_info = llegir_header_datafile(data_file_path)
        if not header_info:
            print(f"[!] Error llegint la capçalera del fitxer: {data_file_path}")
            continue
        samples = llegir_dades(data_file_path, header_info)
        if samples:
            all_samples.extend(samples)

    if not all_samples:
        print(f"[!] No s'han trobat samples a {source_folder}")
        return

    # Ordenem les mostres per temps
    all_samples.sort(key=lambda s: s["time"])

    # Es genera el CSV amb el nom de la subcarpeta
    csv_filename = os.path.join(export_folder, os.path.basename(source_folder) + ".csv")
    try:
        with open(csv_filename, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Time", "Value"])
            for sample in all_samples:
                writer.writerow([sample["time"].strftime('%Y-%m-%d %H:%M:%S.%f'), sample["value"]])
        print(f"[OK] Exportació completada: {csv_filename}")
    except Exception as e:
        print(f"[!] Error exportant CSV per {source_folder}: {e}")


class App(ctk.CTk):
    """Aplicació principal per exportar CSV des de subcarpetes."""

    def __init__(self):
        super().__init__()
        self.title("Exportador de CSV")
        self.geometry("400x400")

        # Marc superior amb botons
        top_frame = ctk.CTkFrame(self)
        top_frame.pack(pady=20, padx=20, fill="x")

        source_btn = ctk.CTkButton(
            top_frame,
            text="Selecciona carpeta d'origen",
            command=self.select_source_folder
        )
        source_btn.pack(side="left", padx=10)

        export_btn = ctk.CTkButton(
            top_frame,
            text="Exporta a CSV",
            command=self.export_selected_folders
        )
        export_btn.pack(side="left", padx=10)

        # Widget filtrable per mostrar el llistat de subcarpetes
        self.item_frame = FilterableItemFrame(self, item_list=[], width=650, height=300)
        self.item_frame.pack(padx=20, pady=20, fill="both", expand=True)

        # Diccionari per mantenir el mapping {nom_subcarpeta: ruta_completa}
        self.subfolder_mapping = {}

    def select_source_folder(self):
        """Permet seleccionar la carpeta d'origen i actualitza la llista de subcarpetes."""
        source_folder = filedialog.askdirectory(title="Selecciona carpeta d'origen")
        if not source_folder:
            messagebox.showinfo("Informació", "No s'ha seleccionat cap carpeta.")
            return

        try:
            subdirs = [
                os.path.join(source_folder, name)
                for name in os.listdir(source_folder)
                if os.path.isdir(os.path.join(source_folder, name)) and "TR2" in name
            ]
        except Exception as e:
            messagebox.showerror("Error", f"No s'ha pogut llegir la carpeta.\n{e}")
            return

        if not subdirs:
            messagebox.showinfo("Informació", "La carpeta seleccionada no conté subcarpetes amb 'TR2'.")
            return

        # Crear un mapping {nom_subcarpeta: ruta_completa}
        self.subfolder_mapping = {os.path.basename(subdir): subdir for subdir in subdirs}
        items = list(self.subfolder_mapping.keys())
        # Actualitzem el widget filtrable
        self.item_frame.update_items(items)

    def export_selected_folders(self):
        """Exporta a CSV les subcarpetes seleccionades."""
        selected_items = self.item_frame.get_selected_items()
        if not selected_items:
            messagebox.showinfo("Informació", "No s'han seleccionat subcarpetes.")
            return

        export_folder = filedialog.askdirectory(title="Selecciona carpeta d'exportació")
        if not export_folder:
            return

        total = len(selected_items)
        progress_bar = ctk.CTkProgressBar(self, width=650)
        progress_bar.pack(pady=(0, 20))
        self.update()

        for i, item in enumerate(selected_items, start=1):
            folder_path = self.subfolder_mapping.get(item)
            if folder_path:
                process_subfolder(folder_path, export_folder)
            progress_bar.set(i / total)
            self.update_idletasks()

        messagebox.showinfo("Exportació CSV", "Exportació completada.")
        progress_bar.destroy()


if __name__ == "__main__":
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")
    app = App()
    app.mainloop()