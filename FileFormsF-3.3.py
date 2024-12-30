import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox

# Función para intentar diferentes codificaciones al leer el archivo
def leer_archivo(ruta_archivo):
    codificaciones = ['utf-16', 'utf-8', 'latin-1']
    for cod in codificaciones:
        try:
            with open(ruta_archivo, 'r', encoding=cod) as f:
                contenido = f.read()
            print(f"Archivo leído con éxito usando codificación: {cod}")
            return contenido
        except UnicodeDecodeError:
            print(f"Error leyendo archivo con codificación {cod}. Probando con otra codificación...")
    return None

# Contadores globales
reemplazos_totales_global = 0
sin_reemplazos_totales_global = 0  # Contador para líneas no reemplazadas global
total_archivos = 0

# Inicializar la interfaz de selección de carpeta
def seleccionar_y_reemplazar():
    global reemplazos_totales_global, sin_reemplazos_totales_global, total_archivos

    # Selección de directorio
    directorio = filedialog.askdirectory(title="Selecciona la carpeta con los archivos .srd a modificar")
    if not directorio:
        messagebox.showinfo("Información", "No se seleccionó ninguna carpeta. Finalizando el script.")
        return

    # Limpiar la terminal en la interfaz
    terminal.delete(1.0, tk.END)
    terminal.insert(tk.END, "Iniciando el proceso de reemplazo...\n")

    # Patrones de dbname a verificar
    patrones_dbname = [
        r'fac_vta_det\.nombre',
        r'fac_proforma_det\.nombre',
        r'nota_det\.nombre',
        r'rem_vta_det\.nombre',
        r'articulos\.descripcion_camara',
        r'descripcion_camara',
        r'cotiza\.pie',
        r'cotiza\.obs_extra',
        r'nota_vta\.nota_cond_pag',
        r'nota_vta\.obs_produccion',
        r'orden_trab\.obs',
        r'PROGRAMACION\.obs',
        r'nota_vta\.obs_produccion',
        r'cotiza\.recepcion',
        r'orden_trab_det\.descrip_proceso',
        r'orden_trab_det\.descrip_proceso_largo',
        r'lab',
        r'ing',
        r'DescLAb',
        r'artic_estructura\.descrip_proceso',
        r'fac_vta_det_bc\.nombre',
        r'articulos\.obs',
        r'orden_cpa\.nota_interna',
        r'CAL_instrucciones_atrib\.instrucciones_control',
        r'CAL_atributos_ctrl\.instr_generales',
        r'CAL_control_resultados_det\.conclusiones',

    ]

    # Parámetro para decidir si se mostrarán las líneas no reemplazadas
    verificar_no_reemplazados = var_no_reemplazados.get()  # Usar el valor del checkbox

    # Iterar sobre cada archivo en la carpeta seleccionada
    for archivo in os.listdir(directorio):
        ruta_archivo = os.path.join(directorio, archivo)
        if archivo.endswith(".srd") and os.path.isfile(ruta_archivo):
            total_archivos += 1
            try:
                # Reiniciar los contadores para cada archivo
                reemplazos_totales = 0
                sin_reemplazos_totales = 0

                # Intentar leer el archivo con diferentes codificaciones
                contenido = leer_archivo(ruta_archivo)
                if not contenido:
                    terminal.insert(tk.END, f"No se pudo leer el archivo {archivo} con las codificaciones probadas. Saltando archivo.\n")
                    continue

                # Buscar todas las líneas con 'column=' que contengan 'char()' y coincidan con el dbname
                for patron_dbname in patrones_dbname:
                    # Este patrón buscará líneas de 'char()' y verificará que el dbname coincida con los patrones
                    patron_busqueda = rf'column=\(type=char\(\d+\)\s*updatewhereclause=[a-z]+\s*name=\S+\s*dbname="{patron_dbname}"\s*\)'
                    lineas = re.findall(patron_busqueda, contenido)

                    # Procesar cada línea encontrada
                    for linea in lineas:
                        # Verificar si la línea necesita ser reemplazada
                        nuevo_contenido = re.sub(r'char\(\d+\)', 'char(32766)', linea)
                        
                        # Si la línea ha cambiado, reemplazarla
                        if nuevo_contenido != linea:
                            contenido = contenido.replace(linea, nuevo_contenido)
                            reemplazos_totales += 1
                            reemplazos_totales_global += 1  # Sumar a global
                        else:
                            sin_reemplazos_totales += 1
                            sin_reemplazos_totales_global += 1  # Sumar a global

                # Si hubo cambios, sobrescribir el archivo con los nuevos contenidos
                with open(ruta_archivo, "w", encoding="utf-16") as f:
                    f.write(contenido)

                # Mostrar el conteo de reemplazos para el archivo actual
                terminal.insert(tk.END, f"\nReemplazos en {archivo}: {reemplazos_totales} reemplazos realizados.")
                
                # Mostrar feedback sobre las líneas no reemplazadas si está habilitado
                if verificar_no_reemplazados:
                    terminal.insert(tk.END, f"Líneas no reemplazadas en {archivo}: {sin_reemplazos_totales}\n")

                # Hacer scroll hacia abajo después de cada archivo
                terminal.yview(tk.END)

            except Exception as e:
                terminal.insert(tk.END, f"Error procesando el archivo {archivo}: {e}\n")
                terminal.yview(tk.END)

    # Mostrar conteo total de reemplazos al finalizar el proceso
    terminal.insert(tk.END, f"\nProceso completado.\nTotal de archivos procesados: {total_archivos}\n")
    terminal.insert(tk.END, f"Total de reemplazos realizados: {reemplazos_totales_global}\n")
    terminal.insert(tk.END, f"Total de líneas no modificadas: {sin_reemplazos_totales_global}\n")

    # Mostrar mensaje final de éxito
    messagebox.showinfo("Proceso completado", f"Se realizaron {reemplazos_totales_global} reemplazos en total.")

# Crear ventana principal
ventana = tk.Tk()
ventana.title("Reemplazo de Archivos .srd")
ventana.geometry("600x400")

# Cambiar el color de fondo de la ventana
ventana.configure(bg="#2f2f2f")  # Gris oscuro

# Crear la terminal simulada (widget Text)
terminal = tk.Text(ventana, wrap=tk.WORD, height=10, width=70, bg="black", fg="white", font=("Courier", 10))
terminal.pack(padx=10, pady=10)

# Agregar un borde blanco y un borde más oscuro para la terminal
terminal.config(borderwidth=2, relief="solid", bd=1, highlightbackground="white", highlightthickness=1)

# Crear el checkbox para habilitar/deshabilitar líneas no modificadas
var_no_reemplazados = tk.BooleanVar(value=True)  # Por defecto está habilitado
checkbox = tk.Checkbutton(ventana, text="Mostrar líneas no modificadas", variable=var_no_reemplazados, bg="#2f2f2f", fg="white", font=("Arial", 10))
checkbox.pack(pady=5)

# Crear botón para iniciar el reemplazo
boton = tk.Button(ventana, text="Realizar Reemplazos", command=seleccionar_y_reemplazar, font=("Arial", 12), bg="#4a4a4a", fg="white")
boton.pack(pady=20)

# Ejecutar la interfaz
ventana.mainloop()
