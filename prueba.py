#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk, messagebox, filedialog,scrolledtext
import csv
import os
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import sqlite3
import pandas as pd

class BasedeDatos:
    def __init__(self):
        
        self.db = 'time_tracking.db'
        self.tabla_entradas = 'time_entries'
        self.tabla_tracking = 'app_state'
        self.tabla_activity = 'activity'
        self.create_entry_table()
        self.create_state_table()
        self.create_activity_table()
        self.insert_code_activities()
        
    def create_entry_table(self):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS {} (
                id INTEGER PRIMARY KEY,
                date TEXT,
                activity_code TEXT,                
                comment TEXT,
                ticket INTEGER,
                initial_hour REAL,
                final_hour REAL,
                var_time REAL,
                var_hours FLOAT

            )
        '''.format(self.tabla_entradas))
        conn.commit()
        conn.close()
        
    def create_state_table(self):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS {} (
                id INTEGER PRIMARY KEY,
                last_activity TEXT,
                last_ticket TEXT,
                last_detail TEXT,
                last_time TEXT
            )
        '''.format(self.tabla_tracking))
        conn.commit()
        conn.close()
        
    def create_activity_table(self):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS {} (
                id INTEGER PRIMARY KEY,
                activity_code INTEGER,
                description TEXT,
                FOREIGN KEY (activity_code) REFERENCES {}(activity_code)
            )
        '''.format(self.tabla_activity, self.tabla_entradas))
        conn.commit()
        conn.close()
        
    def insert_code_activities(self):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM {}'.format(self.tabla_activity))
        if cursor.fetchone()[0] == 0:
            cursor.execute('''INSERT INTO {} (activity_code, description) 
                VALUES 
                (8,'Diseño'),
                (9,'Desarrollo'),
                (11,'Gestión de tickets'),
                (12,'Capacitación'),
                (13,'Reunión'),
                (14,'Documentación'),
                (10,'Otros'),
                (25,'Análisis')'''.format(self.tabla_activity))
            conn.commit()
            conn.close()

    def save_app_state(self, activity, ticket, detail, last_time):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM {}'.format(self.tabla_tracking))  # Eliminar estado anterior
        cursor.execute('INSERT INTO {} (last_activity, last_ticket, last_detail, last_time) VALUES (?, ?, ?, ?)'.format(self.tabla_tracking),
                       (activity, ticket, detail, last_time))
        conn.commit()
        conn.close()

    def load_app_state(self):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()
        cursor.execute('SELECT last_activity, last_ticket, last_detail, last_time FROM {}'.format(self.tabla_tracking))
        state = cursor.fetchone()
        conn.close()
        return state if state else (None, None, None, None)
        
    def load_today_entries(self):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()
        today = datetime.now().strftime('%Y-%m-%d')
        cursor.execute('SELECT * FROM {} WHERE date = ? ORDER BY initial_hour'.format(self.tabla_entradas), (today,))
        rows = cursor.fetchall()
        conn.close()
        return rows        
        
    def save_time_entry(self, date, activity_code, comment, ticket, initial_hour, final_hour, var_time, var_hours):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO {} (activity_code, comment, ticket, initial_hour, final_hour, var_time, var_hours, date) VALUES (?, ?, ?, ?, ?, ?, ?, ?)'.format(self.tabla_entradas), (activity_code, comment, ticket, initial_hour, final_hour, var_time, var_hours, date))
        conn.commit()
        conn.close()
        
    def load_time_entries(self, date):
        #date = datetime.now().strftime('%Y-%m-%d')
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM {} WHERE date = '{}'".format(self.tabla_entradas, date))
        rows = cursor.fetchall()
        conn.close()
        return rows 
        
    def load_logbook(self):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()
        #cursor.execute('SELECT * FROM {} ORDER BY date DESC, initial_hour DESC'.format(self.tabla_entradas))
        cursor.execute('''SELECT 
            	te.id,
            	te.date,
            	at.description, 
            	te.comment ,
            	te.ticket ,
            	te.initial_hour ,
            	te.final_hour ,
            	te.var_time ,
            	te.var_hours 
            FROM {} te
            INNER JOIN {} at ON te.activity_code = at.activity_code 
            ORDER BY te.date DESC, te.initial_hour '''.format(self.tabla_entradas, self.tabla_activity))
        rows = cursor.fetchall()
        conn.close()
        return rows      
        
    def get_id(self, date, activity_code, comment, ticket,initial_hour):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM {} WHERE date=? AND activity_code=? AND comment=? AND ticket=? AND initial_hour=?'.format(self.tabla_entradas), (date, activity_code, comment, ticket,initial_hour))
        id = cursor.fetchone()
        conn.close()
        return id
        
    def update_time_entry(self, id, date, activity_code, comment, ticket, initial_hour, final_hour, var_time, var_hours):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()
        cursor.execute('UPDATE {} SET date=?, activity_code=?, comment=?, ticket=?, initial_hour=?, final_hour=?, var_time=?, var_hours=? WHERE id = ?'.format(self.tabla_entradas), (date, activity_code, comment, ticket, initial_hour, final_hour, var_time, var_hours, id))
        conn.commit()
        conn.close()

    def get_dates_from_db(self):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()
        query = "SELECT DISTINCT date FROM {} ORDER BY date DESC".format(self.tabla_entradas)
        cursor.execute(query)
        dates = [row[0] for row in cursor.fetchall()]
        dates.insert(0, datetime.now().strftime('%Y-%m-%d'))
        conn.close()
        return dates
            
    def load_time_entries_for_date(self, date):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM {} WHERE date = ?".format(self.tabla_entradas), (date,))
        rows = cursor.fetchall()
        conn.close()
        return rows

class Cronometro:
    def __init__(self, root):
        self.root = root
        self.root.title("Registro de horas de jornada")

        self.init_variables()
        self.configure_root()
        self.create_widgets()
        self.setup_initial_values()
        self.load_today_tasks()
        self.load_app_state()
        self.update_detail_label()

    def init_variables(self):
        self.running = False
        self.start_time = None
        self.time_elapsed = 0
        self.last_registered_time = None
        self.current_time = None
        self.actividad = None
        self.detalle = None
        self.ticket = None
        self.iniciado = False
        self.record_window_open = False
        self.entry_usuario = None
        self.entry_contrasena = None
        self.end_journey_status = False
        self.record_id = None
        self.fecha = None
        self.fecha_seleccionada = datetime.now().strftime('%Y-%m-%d')  # Establecer la fecha de hoy por defecto
        self.lst_detalle = []

    def configure_root(self):
        self.root.attributes('-topmost', 1)
        self.root.geometry("+0+0")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_widgets(self):
        self.label = ttk.Label(self.root, text=self.format_time(0), font=("Helvetica", 48))
        self.label.pack(pady=20)

        self.detail_label = ttk.Label(self.root, text="", font=("Helvetica", 24))
        self.detail_label.pack(pady=10)

        self.total_hours_label = ttk.Label(self.root, text="Horas trabajadas: 0", font=("Helvetica", 24))
        self.total_hours_label.pack(pady=10)

        self.create_buttons()
        self.create_listbox()
        self.fecha_combobox = self.create_date_dropdown()
        self.create_load_button()

    def create_buttons(self):
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=10)
    
        self.record_button = ttk.Button(button_frame, text="Registrar Actividad", command=self.open_record_window)
        self.record_button.grid(row=0, column=0, padx=10, pady=10)
    
        self.end_journey_button = ttk.Button(button_frame, text="Terminar jornada", command=self.end_journey)
        self.end_journey_button.grid(row=0, column=1, padx=10, pady=10)
    
        self.lunch_button = ttk.Button(button_frame, text="Iniciar almuerzo", command=self.start_lunch)
        self.lunch_button.grid(row=1, column=1, padx=10, pady=10)
    
        self.export_button = ttk.Button(button_frame, text="Exportar CSV", command=self.export_to_csv)
        self.export_button.grid(row=2, column=0, padx=10, pady=10)
    
        redmine = RedmineTimeLoggerApp()
        print(self.fecha_seleccionada)
        self.upload_button = ttk.Button(button_frame, text="Subir a Redmine", command=lambda:redmine.run_script(self.fecha_seleccionada))
        self.upload_button.grid(row=1, column=0, padx=10, pady=10) 
        
        self.bitacora_button = ttk.Button(button_frame, text="Ver Bitácora", command=self.show_bitacora)
        self.bitacora_button.grid(row=2, column=1, padx=10, pady=10)
        
    def show_bitacora(self):
        bitacora_window = tk.Toplevel(self.root)
        bitacora_window.title("Bitácora")
        bitacora_window.geometry("1200x600")
        bitacora_window.attributes('-topmost', 1)
    
        # Frame para la búsqueda
        search_frame = ttk.Frame(bitacora_window)
        search_frame.pack(pady=10, padx=10, fill='x')
    
        ttk.Label(search_frame, text="Buscar:").pack(side='left', padx=(0, 5))
        search_entry = ttk.Entry(search_frame, width=40)
        search_entry.pack(side='left', padx=(0, 5))
        search_button = ttk.Button(search_frame, text="Buscar", command=lambda: self.search_bitacora(tree, search_entry.get()))
        search_button.pack(side='left')
    
        # Crear un Treeview para mostrar los datos
        columns = ("Fecha", "Código Actividad", "Comentario", "Ticket", "Hora Inicio", "Hora Fin", "Tiempo", "Horas")
        tree = ttk.Treeview(bitacora_window, columns=columns, show='headings')
        
        column_widths = {
            "Fecha": 80,
            "Código Actividad": 100,
            "Comentario": 400,
            "Ticket": 80,
            "Hora Inicio": 100,
            "Hora Fin": 100,
            "Tiempo": 100,
            "Horas": 80
        }
    
        # Definir los encabezados
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=column_widths[col])
    
        # Obtener los datos de la base de datos
        records = basededatos.load_logbook()
    
        # Insertar los datos en el Treeview
        for record in records:
            tree.insert('', 'end', values=record[1:])  # Omitimos el ID que está en la posición 0
    
        # Añadir scrollbars
        vsb = ttk.Scrollbar(bitacora_window, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(bitacora_window, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    
        # Posicionar el Treeview y los scrollbars
        tree.pack(expand=True, fill='both', padx=10, pady=10)
        vsb.pack(side='right', fill='y')
        hsb.pack(side='bottom', fill='x')
    
        # Botón para cerrar la ventana
        close_button = ttk.Button(bitacora_window, text="Cerrar", command=bitacora_window.destroy)
        close_button.pack(pady=10)
        
    def search_bitacora(self, tree, search_term):
        # Limpiar la búsqueda anterior
        for item in tree.get_children():
            tree.delete(item)
    
        # Obtener todos los registros
        records = basededatos.load_logbook()
    
        # Filtrar los registros que coincidan con el término de búsqueda
        filtered_records = [record for record in records if any(search_term.lower() in str(field).lower() for field in record)]
    
        # Insertar los registros filtrados en el Treeview
        for record in filtered_records:
            tree.insert('', 'end', values=record[1:])  # Omitimos el ID que está en la posición 0
    
        if not filtered_records:
            messagebox.showinfo("Búsqueda", "No se encontraron resultados.")    
        
    def start_lunch(self):
        
        if self.end_journey_status == True:
            messagebox.showerror(title='Error', message='No puedes iniciar el almuerzo, tu jornada terminó')
            return
        
        now = datetime.now()
        lunch_start = now
        lunch_end = now + timedelta(hours=1)
        date = datetime.now().strftime('%Y-%m-%d')
        lunch_start_formatted = lunch_start.strftime('%H:%M:%S')
        lunch_end_formatted = lunch_end.strftime('%H:%M:%S')
        self.record_time(date, 
                         self.last_registered_time or self.get_initial_time(), 
                         lunch_start_formatted, 
                         self.actividad, 
                         self.detalle, 
                         self.ticket)        
        self.time_listbox.insert(tk.END, f"{lunch_start_formatted} - {lunch_end_formatted} - Almuerzo - Ticket: N/A - Tiempo de almuerzo")
        
        # Actualizar la etiqueta de detalle
        self.detail_label.config(text="Almuerzo")
        
        # Resetear variables para la próxima actividad
        self.last_registered_time = lunch_end_formatted
        self.iniciado = False
        
        
        
        messagebox.showinfo("Almuerzo", f"Se ha registrado el tiempo de almuerzo de {lunch_start_formatted} a {lunch_end_formatted}.")
    
    def load_app_state(self):
        self.actividad, self.ticket, self.detalle, self.last_registered_time = basededatos.load_app_state()
        if self.actividad:
            self.iniciado = True
        else:
            self.iniciado = False

    def update_detail_label(self):
        #self.detail_label.config(text=f'{self.ticket} : {self.actividad} - {self.detalle}')
        if self.ticket:
            self.detail_label.config(text=f'{self.ticket} : {self.actividad} - {self.detalle}')
        else:
            self.detail_label.config(text="")
    
    def load_today_tasks(self):
        today_entries = basededatos.load_today_entries()
        for entry in today_entries:
            self.add_entry_to_listbox(entry)

    def add_entry_to_listbox(self, entry):
        _, date, activity_code, comment, ticket, initial_hour, final_hour, var_time, var_hours = entry
        activity = self.get_activity_name(activity_code)
        entry_text = f"{initial_hour} - {final_hour} - {activity} - Ticket: {ticket} - {comment}"
        self.time_listbox.insert(tk.END, entry_text)
        self.update_total_hours()  # Actualizar horas trabajadas al agregar una entrada

    def get_activity_name(self, activity_code):
        activity_names = {
            '8': 'Diseño',
            '9': 'Desarrollo',
            '11': 'Gestión de tickets',
            '12': 'Capacitación',
            '13': 'Reunión',
            '14': 'Documentación',
            '10': 'Otros',
            '25': 'Análisis'
        }
        return activity_names.get(activity_code, 'Error')
    
    def create_listbox(self):
        self.time_listbox = tk.Listbox(self.root, height=10, width=100)
        self.time_listbox.pack(pady=20)
        self.time_listbox.bind('<Double-1>', self.edit_record)

    def setup_initial_values(self):
        self.update_start_time()
        self.update_clock()
        self.update_current_time()
        self.open_record_window()

    def on_closing(self):
        if messagebox.askyesno("Confirmar salida", "¿Estás seguro de que deseas salir?"):
            if self.iniciado:
                basededatos.save_app_state(self.actividad, self.ticket, self.detalle, self.last_registered_time)
            self.root.destroy()
            
    def end_journey(self):
        if messagebox.askyesno("Confirmar", "¿Estás seguro de que deseas terminar la jornada?"):
            now = datetime.now()
            date = datetime.now().strftime('%Y-%m-%d')
            current_time = now.strftime('%H:%M:%S')
            
            # Registrar la última tarea en espera si existe
            if self.iniciado:
                self.record_time(date,
                                 self.last_registered_time or self.get_initial_time(), 
                                 current_time, 
                                 self.actividad, 
                                 self.detalle, 
                                 self.ticket)
            
            # Resetear variables
            self.iniciado = False
            self.last_registered_time = None
            self.actividad = None
            self.detalle = None
            self.ticket = None
            self.end_journey_status = True
            
            # Actualizar la etiqueta de detalle
            self.detail_label.config(text="Jornada finalizada")
            basededatos.save_app_state(None, None, None, None)
            messagebox.showinfo("Jornada finalizada", "La jornada ha sido finalizada correctamente.")            

    def update_start_time(self):
        self.start_time = datetime.now()
        self.time_elapsed = 0
        self.label.config(text=self.format_time(self.time_elapsed))

    def get_initial_time(self):
        now = datetime.now()
        ahora = self.format_time(now.hour * 3600 + now.minute * 60 + now.second)
        print(ahora)
        return ahora

    def update_clock(self):
        if self.running:
            now = datetime.now()
            elapsed_time = now - self.start_time
            self.time_elapsed = int(elapsed_time.total_seconds())
            self.label.config(text=self.format_time(self.time_elapsed))
        self.root.after(1000, self.update_clock)

    def update_current_time(self):
        now = datetime.now()
        self.label.config(text=self.format_time(now.hour * 3600 + now.minute * 60 + now.second))
        self.root.after(1000, self.update_current_time)

    def format_time(self, seconds):
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        return f"{hours:02}:{minutes:02}:{seconds:02}"

    def reset(self):
        self.update_start_time()
        self.time_listbox.delete(0, tk.END)
        self.last_registered_time = None  

    def open_record_window(self):
        # if self.record_window_open:
        #     return
        self.record_window_open = True
        record_window = self.create_record_window()
        self.setup_record_window(record_window)

    def create_record_window(self):
        record_window = tk.Toplevel(self.root)
        record_window.title("Registrar Actividad")
        record_window.geometry("500x350")
        record_window.attributes('-topmost', 1)
        record_window.protocol("WM_DELETE_WINDOW", lambda: self.close_record_window(record_window))
        return record_window

    def setup_record_window(self, record_window):
        self.create_record_window_widgets(record_window)

    def create_record_window_widgets(self, record_window):
        tk.Label(record_window, text="Fecha:").pack(pady=5)
        fecha_combobox = ttk.Combobox(record_window, values=basededatos.get_dates_from_db(), state='readonly')
        fecha_combobox.set(self.fecha_seleccionada)  # Establecer la fecha de hoy como seleccionada
        fecha_combobox.pack(pady=5)

        tk.Label(record_window, text="Actividad:").pack(pady=5)
        actividad_combobox = ttk.Combobox(record_window, values=[
            'Análisis', 'Desarrollo', 'Capacitación', 'Diseño',
            'Documentación', 'Gestión de tickets', 'Reunión', 'Otros'
        ], state='readonly', width=50)
        actividad_combobox.pack(pady=5)

        # tk.Label(record_window, text="Detalle:").pack(pady=5)
        # detalle_entry = tk.Entry(record_window, width=50, validate="key", validatecommand=(record_window.register(self.validate_detalle), '%P'))
        # detalle_entry.pack(pady=5)

        tk.Label(record_window, text="Detalle:").pack(pady=5)
        detalle_entry = ttk.Combobox(record_window, width=50, values=self.lst_detalle, validatecommand=(record_window.register(self.validate_detalle), '%P'))
        detalle_entry.pack(pady=5)

        tk.Label(record_window, text="Ticket:").pack(pady=5)
        ticket_entry = tk.Entry(record_window, validate="key", validatecommand=(record_window.register(self.validate_ticket), '%P'), width=50)
        ticket_entry.pack(pady=5)

        submit_button = ttk.Button(record_window, text="Aceptar", command=lambda: self.submit_record_window(fecha_combobox, actividad_combobox, detalle_entry, ticket_entry, record_window))
        submit_button.pack(pady=10)
        record_window.bind('<Return>', lambda event: self.submit_record_window(fecha_combobox, actividad_combobox, detalle_entry, ticket_entry, record_window))
        

    def close_record_window(self, record_window):
        self.record_window_open = False
        record_window.destroy()

    def submit_record_window(self, fecha_combobox, actividad_combobox, detalle_entry, ticket_entry, record_window):
        
        print(ticket_entry.get())

        fecha_hoy = datetime.now().strftime('%Y-%m-%d')

        self.current_time = datetime.now().strftime('%H:%M:%S')

        print(self.iniciado)


        #FIXME: Se actualiza la etiqueta y después hace las validaciones del ticket 
        if self.iniciado and self.fecha:
            if self.fecha == fecha_hoy :
                self.record_time(fecha_hoy,self.last_registered_time or self.get_initial_time(), self.current_time, self.actividad, self.detalle, self.ticket)

        self.fecha = fecha_combobox.get()  # Obtener la fecha seleccionada
        self.actividad = actividad_combobox.get()
        self.detalle = detalle_entry.get()
        self.ticket = ticket_entry.get()
        self.current_time = datetime.now().strftime('%H:%M:%S')

        if self.detalle not in self.lst_detalle:
            print('No existe valor del detalle en la lista. Se agrega')
            self.lst_detalle.append(self.detalle)
        else:
            print('Ya existe el detalle en su listado')

        if self.fecha != fecha_hoy:
            print('Se grabó registro fuera de fecha')
            self.record_time(self.fecha, '09:00:00', '09:00:00', self.actividad, self.detalle, self.ticket)
            record_window.destroy()
            self.record_window_open = False
            return

        if not self.iniciado and self.actividad and self.ticket.isdigit():
            self.update_detail_label()
            record_window.destroy()
            self.iniciado  = True
            print('Se grabó primer registro dentro de fecha')
        elif self.actividad and self.ticket.isdigit() and self.iniciado and self.fecha == fecha_hoy:
            print('Se grabó registro dentro de fecha')
            self.last_registered_time = self.current_time
            self.iniciado = True
            self.record_window_open = False
            self.update_detail_label()
            basededatos.save_app_state(self.actividad, self.ticket, self.detalle, self.last_registered_time)
            record_window.destroy()
            messagebox.showinfo(title='Hora inicio', message=f'La hora de inicio es : {self.last_registered_time or self.get_initial_time()}')
            self.update_total_hours()  # Actualizar horas trabajadas al agregar una entrada
        else:
            messagebox.showwarning("Advertencia", "Debes seleccionar una actividad y proporcionar un ticket numérico.")


    def validate_ticket(self, value):
        return value.isdigit() or value == ""

    def validate_detalle(self, value):
        # No permitir caracteres ':' ni '-'
        return not any(char in value for char in ':-') or value == ""

    def record_time(self, date, last_time, current_time, actividad, detalle, ticket):
        print(self.fecha_seleccionada)
        print(date)
        if date == self.fecha_seleccionada: 
            self.time_listbox.insert(tk.END, f"{last_time} - {current_time} - {actividad} - Ticket: {ticket} - {detalle}")
        #date = datetime.now().strftime('%Y-%m-%d')
        hours = self.calcular_var_time(last_time, current_time) / 3600
        actividad_code = self.obtener_codigo_opcion(actividad)
        try:
            basededatos.save_time_entry(
                date=date, 
                activity_code=actividad_code, 
                comment=detalle, 
                ticket=ticket, 
                initial_hour=last_time, 
                final_hour=current_time, 
                var_time=self.calcular_var_horas(last_time, current_time), 
                var_hours=hours
            )
            print('Se grabó registro en la base de datos')
        except Exception as e:
            print(f"Error al guardar el registro: {e}")

    def export_to_csv(self):
        
        #ubicacion = filedialog.asksaveasfilename(filetypes=[('CSV files', '*.csv')])
        ubicacion = 'tareas.csv'
        #self.record_time(self.last_registered_time or self.get_initial_time(), datetime.now().strftime('%H:%M:%S'), self.actividad, self.detalle, self.ticket)
        
        if not ubicacion:
            return

        today_date = datetime.now().strftime('%Y-%m-%d')
        items = self.time_listbox.get(0, tk.END)
    
        if not items:
            messagebox.showwarning("Advertencia", "No hay datos para exportar.")
            return
    
        file_path = os.path.join(os.getcwd(), ubicacion)
        
        print(file_path)
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(['Ticket', 'Fecha', 'Horas', 'Comentario', 'Opcion'])
            for item in items:
                last_time, current_time, actividad, ticket, detalle = item.split(' - ')
                ticket = ticket.split(':')[1].strip()
                
                # Excluir los registros de almuerzo
                if actividad.lower() != 'almuerzo':
                    var_time = self.calcular_var_time(last_time, current_time) / 3600
                    actividad_code = self.obtener_codigo_opcion(actividad)
                    csv_writer.writerow([ticket, today_date, var_time, detalle, actividad_code])
                    var_horas = self.calcular_var_horas(last_time,current_time)
                    record = [
                        [self.transformar_fecha(today_date), actividad, detalle, ticket, last_time, current_time, var_horas, var_time]
                    ]
    
        messagebox.showinfo("Éxito", f"Datos exportados a {file_path}")
    
    def transformar_fecha(self,fecha):
        formato_entrada = '%Y-%m-%d'
        formato_salida = '%d-%m-%Y'
        fecha_obj = datetime.strptime(fecha, formato_entrada)
        fecha_transformada = fecha_obj.strftime(formato_salida)
        return fecha_transformada    
    
    def calcular_var_horas(self,inicio, fin):
        formato = '%H:%M:%S'
        tiempo_inicio = datetime.strptime(inicio, formato)
        tiempo_fin = datetime.strptime(fin, formato)
        diferencia = tiempo_fin - tiempo_inicio
        diferencia_segundos = diferencia.total_seconds()
        horas = int(diferencia_segundos // 3600)
        minutos = int((diferencia_segundos % 3600) // 60)
        segundos = int(diferencia_segundos % 60)
        
        return f"{horas:02}:{minutos:02}:{segundos:02}"
    
    def calcular_var_time(self, inicio_str, fin_str):
        formato = '%H:%M:%S'
        inicio = datetime.strptime(inicio_str, formato)
        fin = datetime.strptime(fin_str, formato)
        var_time = (fin - inicio).total_seconds()
        
        return var_time

    def obtener_codigo_opcion(self, actividad):
        opciones = {
            'Diseño': 8,
            'Desarrollo': 9,
            'Gestión de tickets': 11,
            'Capacitación': 12,
            'Reunión': 13,
            'Documentación': 14,
            'Otros': 10,
            'Análisis': 25
        }
        return opciones.get(actividad, 'error')

    def edit_record(self, event):
        index = self.time_listbox.curselection()[0]
        selected_item = self.time_listbox.get(index)
        last_time, current_time, actividad, ticket, detalle = selected_item.split(' - ')
        ticket = ticket.split(': ')[1]
        date = self.fecha_seleccionada
        self.record_id = basededatos.get_id(
            date=date, 
            activity_code=self.obtener_codigo_opcion(actividad), 
            comment=detalle, 
            ticket=ticket,
            initial_hour=last_time
        )
        print(self.record_id)
        edit_window = self.create_edit_window()
        self.setup_edit_window(edit_window, index, last_time, current_time, actividad, ticket, detalle)

    def create_edit_window(self):
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Editar Registro")
        edit_window.attributes('-topmost', 1)
        return edit_window

    def setup_edit_window(self, edit_window, index, last_time, current_time, actividad, ticket, detalle):
        tk.Label(edit_window, text="Hora inicio:").pack(pady=5)
        last_time_entry = tk.Entry(edit_window)
        last_time_entry.insert(0, last_time)
        last_time_entry.pack(pady=5)

        tk.Label(edit_window, text="Hora fin:").pack(pady=5)
        current_time_entry = tk.Entry(edit_window)
        current_time_entry.insert(0, current_time)
        current_time_entry.pack(pady=5)

        tk.Label(edit_window, text="Actividad:").pack(pady=5)
        actividad_combobox = ttk.Combobox(edit_window, values=[
            'Análisis', 'Desarrollo', 'Capacitación', 'Diseño',
            'Documentación', 'Gestión de tickets', 'Reunión', 'Otros'
        ], state='readonly')
        actividad_combobox.set(actividad)
        actividad_combobox.pack(pady=5)
        
        

        tk.Label(edit_window, text="Detalle:").pack(pady=5)
        detalle_entry = tk.Entry(edit_window, validate="key", validatecommand=(edit_window.register(self.validate_detalle), '%P'))
        detalle_entry.insert(0, detalle)
        detalle_entry.pack(pady=5)

        tk.Label(edit_window, text="Ticket:").pack(pady=5)
        ticket_entry = tk.Entry(edit_window, validate="key", validatecommand=(edit_window.register(self.validate_ticket), '%P'))
        ticket_entry.insert(0, ticket)
        ticket_entry.pack(pady=5)

        submit_button = ttk.Button(edit_window, text="Aceptar", command=lambda: self.submit_edit_window(edit_window, index, last_time_entry, current_time_entry, actividad_combobox, detalle_entry, ticket_entry))
        submit_button.pack(pady=10)

        edit_window.bind('<Return>', lambda event: self.submit_edit_window(edit_window, index, last_time_entry, current_time_entry, actividad_combobox, detalle_entry, ticket_entry))

    def submit_edit_window(self, edit_window, index, last_time_entry, current_time_entry, actividad_combobox, detalle_entry, ticket_entry):
        new_last_time = last_time_entry.get()
        new_current_time = current_time_entry.get()
        new_actividad = actividad_combobox.get()
        new_detalle = detalle_entry.get()
        new_ticket = ticket_entry.get()

        if new_actividad and new_ticket.isdigit():
            self.time_listbox.delete(index)
            self.time_listbox.insert(index, f"{new_last_time} - {new_current_time} - {new_actividad} - Ticket: {new_ticket} - {new_detalle}")
            date = self.fecha_seleccionada
            actividad_code = self.obtener_codigo_opcion(new_actividad)
            detalle = new_detalle
            ticket = new_ticket
            last_time = new_last_time
            current_time = new_current_time
            var_time = self.calcular_var_horas(last_time, current_time)
            var_hours = self.calcular_var_time(last_time, current_time) / 3600
            try:
                basededatos.update_time_entry(
                    id=self.record_id[0], 
                    date=date, 
                    activity_code=actividad_code, 
                    comment=detalle, 
                    ticket=ticket, 
                    initial_hour=last_time, 
                    final_hour=current_time, 
                    var_time=var_time, 
                    var_hours=var_hours
                )
            except Exception as e:
                print(f"Error al actualizar el registro: {e}")
            edit_window.destroy()
            self.update_total_hours()  # Actualizar horas trabajadas al editar una entrada
        else:
            messagebox.showwarning("Advertencia", "Debes seleccionar una actividad y proporcionar un ticket numérico.")
            
    def anexar_a_csv(self,nombre_archivo, nuevos_registros):
        with open(nombre_archivo, 'a', newline='', encoding='utf-8') as archivo_csv:
            escritor_csv = csv.writer(archivo_csv)
            for registro in nuevos_registros:
                escritor_csv.writerow(registro)

    def update_total_hours(self):
        total_seconds = 0
        for item in self.time_listbox.get(0, tk.END):
            last_time, current_time, _, _, _ = item.split(' - ')
            var_time = self.calcular_var_time(last_time, current_time)
            total_seconds += var_time

        total_hours = total_seconds / 3600
        self.total_hours_label.config(text=f"Horas trabajadas: {total_hours:.2f}")

    def create_date_dropdown(self):
        self.fecha_combobox = ttk.Combobox(self.root, values=basededatos.get_dates_from_db(), state='readonly')
        self.fecha_combobox.pack(pady=5)
        self.fecha_combobox.bind("<<ComboboxSelected>>", self.on_date_selected)
        return self.fecha_combobox.get()

    def create_load_button(self):
        load_button = ttk.Button(self.root, text="Cargar Tareas", command=self.load_tasks_for_selected_date)
        load_button.pack(pady=5)

    def on_date_selected(self, event):
        self.fecha_seleccionada = self.fecha_combobox.get()

    def load_tasks_for_selected_date(self):
        if self.fecha_seleccionada:
            self.time_listbox.delete(0, tk.END)  # Limpiar la listbox antes de cargar nuevas tareas
            entries = basededatos.load_time_entries_for_date(self.fecha_seleccionada)  # Cargar tareas de la fecha seleccionada
            for entry in entries:
                self.add_entry_to_listbox(entry)

class RedmineTimeLoggerApp:
    def __init__(self):
        self.url = 'https://redmine.anachronics.com'
        self.url_new = 'https://redmine.anachronics.com/issues/{0}/time_entries/new'
        self.url_time_entries = 'https://redmine.anachronics.com/time_entries'
        self.ticket = 57551
        self.archivo_csv = ''
        self.usuario = None
        self.contrasena = None
        self.login_bool = False
        self.login_response = None
        self.in_redmine = None
        self.parametro = None
        self.token = None
        self.session = None

    def get_option_by_id(self, option_id):
        options = {
            '8': 'Diseño',
            '9': 'Desarrollo',
            '11': 'Gestión de tickets',
            '12': 'Capacitación',
            '13': 'Reunión',
            '14': 'Documentación',
            '10': 'Otros',
            '25': 'Análisis'
        }
        return options.get(option_id, 'error')

    def build_task(self, token, ticket, date, hours, comments, activity_id):
        task = {
            "authenticity_token": token,
            "back_url": self.url_new.format(ticket),
            "issue_id": ticket,
            "commit": 'Crear',
            "time_entry[issue_id]": ticket,
            "time_entry[spent_on]": date,
            "time_entry[hours]": hours,
            "time_entry[comments]": comments,
            "time_entry[activity_id]": activity_id
        }
        return task

    def login(self):
        if not self.usuario or not self.contrasena:
            messagebox.showerror("Error", "Usuario o contraseña no proporcionados.")
            return

        self.authenticate()
        
        if self.login_response:
            soup = BeautifulSoup(self.login_response.text, 'html.parser')
            flash_error = soup.find('div', class_='flash error')

            if not flash_error:
                messagebox.showinfo(title='Éxito', message='Login exitoso')
                self.login_bool = True
            else:
                messagebox.showerror(title='Error en el login', message=f'Las credenciales ingresadas no son válidas. {flash_error.get_text()}')
                self.login_bool = False
        else:
            messagebox.showerror(title='Error en el login', message='No se pudo conectar con el servidor')
            self.login_bool = False

    def window_login(self):

        login_window = tk.Toplevel()
        login_window.title("Inicio de Sesión")
        login_window.geometry("300x150")
        
        tk.Label(login_window, text="Usuario:").pack()
        username_entry = tk.Entry(login_window)
        username_entry.pack()
        
        tk.Label(login_window, text="Contraseña:").pack()
        password_entry = tk.Entry(login_window, show="*")
        password_entry.pack()
        
        def on_login():
            self.usuario = username_entry.get()
            self.contrasena = password_entry.get()
            login_window.destroy()
            self.login()  # Intenta iniciar sesión
        
        tk.Button(login_window, text="Iniciar Sesión", command=on_login).pack()
        
        login_window.transient(app.root)  # Hace que la ventana sea modal
        login_window.grab_set()  # Previene interacciones con otras ventanas
        app.root.wait_window(login_window)  # Espera hasta que la ventana de login se cierre
        
    def process_login(self, usuario, contrasena, ventana):
        self.usuario = usuario
        self.contrasena = contrasena
        self.login()
        ventana.destroy()

    def agg_entries(self, data):
        columns = ['ID', 'Fecha', 'Código', 'Descripción', 'Número', 'Hora Inicio', 'Hora Fin', 'var_time', 'var_hours']
        df = pd.DataFrame(data, columns=columns)
        df_grouped = df.groupby(['Fecha', 'Código', 'Número', 'Descripción'], as_index=False)['var_hours'].sum()
        result = list(df_grouped.itertuples(index=False, name=None))
        return result

    def entry_page(self):
        with requests.Session() as session:
            print("Entrando a Redmine ... ")
            self.in_redmine = session.get(self.url)
            if self.in_redmine.status_code == 200:
                print("Tiempo de respuesta:", self.in_redmine.elapsed)
                soup = BeautifulSoup(self.in_redmine.text, 'html.parser')
                print("Obteniendo tokens para inicio de sesión")
                csrf_param = soup.find('meta', attrs={'name': 'csrf-param'})
                csrf_token = soup.find('meta', attrs={'name': 'csrf-token'})
                if csrf_param and csrf_token:
                    print("Tokens encontrados")
                    return csrf_param.get('content'), csrf_token.get('content'), session
                else:
                    print("No se encontraron los tokens")
                    return None, None
            else:
                print("Error al entrar a Redmine")
                return None, None

    def authenticate(self):
        if not self.usuario or not self.contrasena or not self.parametro or not self.token:
            messagebox.showerror("Error", "Faltan datos necesarios para la autenticación.")
            return
        
        login_data = {
            'login': 'Acceder',
            'username': self.usuario,
            'password': self.contrasena,
            self.parametro: self.token
        }
        
        self.login_response = self.session.post(self.in_redmine.url, data=login_data)
        
    def upload_data(self, session, date):
        print("Iniciando carga de datos")
        records = basededatos.load_time_entries(date=date)
        print(f'datos cargados : {records}')
        records = self.agg_entries(data=records)
        print(f'datos procesados : {records}')

        for record in records:
            
            issue_id = record[2]
            activity_id = str(record[1])
            comments = record[3]
            hours = record[4]
            spent_on = record[0]
            print('ticket: {} - actividad : {} - comentario : {} - tiempo: {} - fecha : {}'.format(issue_id, activity_id, comments, hours, spent_on))
            url_new_response = session.get(self.url_new.format(record[2]))
            print(url_new_response)
            if url_new_response.status_code == 200:
                soup = BeautifulSoup(url_new_response.text, 'html.parser')
                csrf_token = soup.find('meta', attrs={'name': 'csrf-token'})
                option = self.get_option_by_id(record[1])
                print(option)
                if option != 'error':
                
                    payload = self.build_task(
                        token       = csrf_token.get('content'),
                        ticket      = issue_id,
                        date        = spent_on,
                        hours       = hours,
                        comments    = comments,
                        activity_id = activity_id
                    )
                    task_register = session.post(self.url_time_entries, data=payload)
                    if task_register.status_code == 200:
                        print("Registrado con exito")
                    else:
                        print("No se registró")
            else:
                print('Error en el status de url_new_record : {}'.format(url_new_response.status_code))
                messagebox.showinfo(message='la tarea {} no se registró. Asegurese que el ticket {} es correcto y tiene acceso'.format(comments, issue_id))

        messagebox.showinfo(title='Carga completa', message='Información actualizada en Redmine')
        
    def run_script(self, date):
        if app.end_journey_status == False:
            messagebox.showerror(title='Error', message='No se puede correr el script, debes terminar la jornada')
            return
        ready = messagebox.askquestion("Continuar", "Empezará a correr el Script, presione 'Sí' para continuar 'No' para cancelar")
        if ready == 'yes':
            self.parametro, self.token, self.session = self.entry_page()
            if self.parametro and self.token:
                self.window_login()
                print(self.login_bool)
                if self.login_bool == True:
                    self.upload_data(self.session, date)
                else:
                    messagebox.showerror("Error", "No se pudo iniciar sesión en Redmine.")
            else:
                messagebox.showerror("Error", "No se pudieron obtener los tokens necesarios.")
        else:
            print("Script cancelado por el usuario.")   

if __name__ == "__main__":
    basededatos = BasedeDatos()
    root = tk.Tk()
    app = Cronometro(root)
    root.mainloop()
        
          