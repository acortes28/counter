# counter


## Importar horas desde redmine

### Importación manual

Lo primero que se debe hacer es acceder a redmine con la cuenta propia e ir a 'Tiempo dedicado. Luego filtrar por usuario para que aparezca el propio.

![Paso 1](./img/step_1.png)

Entonces bajar al final y presionar en 'Exportar' a csv y hacer click en 'CSV'

![Paso 1](./img/step_2.png)

Aquí preguntará las propiedades de exportación. Se debe elegir:
* Columnas seleccionadas
* UTF-8

![Paso 1](./img/step_3.png)


## Diagrama de clases


```mermaid

classDiagram

class BasedeDatos {
    - db: str
    - tabla_entradas: str
    - tabla_tracking: str
    - tabla_activity: str
    - tabla_fechas: str
    + __init__()
    + create_entry_table()
    + create_state_table()
    + create_activity_table()
    + create_working_day_table()
    + insert_working_days()
    + insert_code_activities()
    + save_app_state(activity, ticket, detail, last_time)
    + load_app_state() : tuple
    + load_today_entries() : list
    + save_time_entry(date, activity_code, comment, ticket, initial_hour, final_hour, var_time, var_hours)
    + load_time_entries(date) : list
    + load_logbook() : list
    + get_id(date, activity_code, comment, ticket, initial_hour) : int
    + update_time_entry(id, date, activity_code, comment, ticket, initial_hour, final_hour, var_time, var_hours)
    + get_dates_from_db() : list
    + load_time_entries_for_date(date) : list
}

class Cronometro {
    - root: Tk
    - running: bool
    - start_time: datetime
    - time_elapsed: int
    - last_registered_time: str
    - current_time: str
    - actividad: str
    - detalle: str
    - ticket: str
    - iniciado: bool
    - record_window_open: bool
    - entry_usuario: Entry
    - entry_contrasena: Entry
    - end_journey_status: bool
    - record_id: int
    - fecha: str
    - fecha_seleccionada: str
    - lst_detalle: list
    + __init__(root: Tk)
    + init_variables()
    + configure_root()
    + create_widgets()
    + create_date_dropdown()
    + create_load_button()
    + load_today_tasks()
    + add_entry_to_listbox(entry)
    + update_total_hours()
    + on_date_selected(event)
    + load_tasks_for_selected_date()
    + open_record_window()
    + create_record_window()
    + submit_record_window(fecha_combobox, actividad_combobox, detalle_combobox, ticket_entry, record_window)
}

class RedmineTimeLoggerApp {
    - url: str
    - url_new: str
    - url_time_entries: str
    - ticket: int
    - archivo_csv: str
    - usuario: str
    - contrasena: str
    - login_bool: bool
    - login_response: Response
    - in_redmine: Response
    - parametro: str
    - token: str
    - session: Session
    + __init__()
    + get_option_by_id(option_id: str) : str
    + build_task(token: str, ticket: int, date: str, hours: float, comments: str, activity_id: int) : dict
    + login()
    + window_login()
    + process_login(usuario: str, contrasena: str, ventana: Toplevel)
    + agg_entries(data: list) : list
    + entry_page()
    + authenticate()
    + upload_data(session: Session, date: str)
    + run_script(date: str)
}

class WorkingDays {
    + obtener_feriados(anio: str) : list
    + es_dia_habil(fecha: datetime, feriados: list) : bool
    + obtener_dias_habiles(inicio: datetime, fin: datetime, feriados: list) : list
    + orquestacion(anio: str, inicio: datetime, fin: datetime) : list
}

BasedeDatos --> Cronometro : "utiliza"
Cronometro --> RedmineTimeLoggerApp : "utiliza"
Cronometro --> WorkingDays : "utiliza"

```