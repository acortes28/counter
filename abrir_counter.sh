#!/bin/bash

# Directorio del entorno virtual
VENV_DIR="env"

# Verifica si el directorio del entorno virtual existe
if [ ! -d "$VENV_DIR" ]; then
  echo "El entorno virtual no existe. Creándolo..."
  python3 -m venv "$VENV_DIR"
  
  # Activar el entorno virtual
  source "$VENV_DIR/bin/activate"
  
  # Instalar las dependencias desde requirements.txt si el archivo existe
  if [ -f "requirements.txt" ]; then
    echo "Instalando dependencias desde requirements.txt..."
    pip install -r requirements.txt
  else
    echo "El archivo requirements.txt no se encontró. No se instalarán dependencias."
  fi
  
  # Desactivar el entorno virtual
  deactivate
fi

# Activar el entorno virtual
source "$VENV_DIR/bin/activate"


# Ruta al intérprete de Python en el entorno virtual
PYTHON_INTERPRETER="$VENV_DIR/bin/python"

# Verifica si Tkinter está instalado
echo "Verificando si Tkinter está instalado..."
if python -c "import tkinter" &> /dev/null; then
  echo "Tkinter está instalado."
else
  echo "Tkinter no está instalado. Por favor, instala Tkinter según tu sistema operativo:"
  echo "- En Ubuntu/Debian: sudo apt-get install python3-tk"
  echo "- En Fedora: sudo dnf install python3-tkinter"
  echo "- En Arch Linux: sudo pacman -S tk"
  echo "Luego, ejecuta este script nuevamente."
  deactivate
  exit 1
fi

# Archivo Python a ejecutar
PYTHON_SCRIPT="abrir_counter.py"

# Verifica si el archivo Python existe
if [ ! -f "$PYTHON_SCRIPT" ]; then
  echo "El archivo $PYTHON_SCRIPT no existe."
  deactivate
  exit 1
fi

# Ejecutar el archivo Python
$PYTHON_INTERPRETER "$PYTHON_SCRIPT"

# Desactivar el entorno virtual
deactivate


