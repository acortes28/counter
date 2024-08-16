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


