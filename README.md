Aplicación de análisis de países del mundo

Descripción: 
Esta aplicación web permite explorar información actualizada de distintos países del mundo obtenida desde la API pública RestCountries, una API gratuita que no requiere claves ni autenticación. La aplicación organiza los datos y los muestra mediante gráficos y tablas fáciles de interpretar, permitiendo analizar población, área territorial, continentes, capitales, idiomas y otros datos generales, ofreciendo una forma simple y rápida de visualizar esta información directamente desde el navegador.

Requisitos: 
- Tener la versión de Python 3.10 o superior instalado en tu computador.
- Contar con conexión a internet, ya que, los datos se descargan en tiempo real.
- Instalar algunas librerías que la aplicación necesita para funcionar (Streamlit, Pandas, Requests y Matplotlib).
- No se requieren cuentas, claves, pagos ni configuraciones avanzadas.

Instalación: 
Descarga o copia todos los archivos del proyecto dentro de una misma carpeta.
- Paso 1: Abre la terminal de tu computador.
- Paso 2: Ingresa a la carpeta donde guardaste el proyecto.
- Paso 3: Instala las librerías necesarias mediante el siguiente comando:
                pip install streamlit pandas requests matplotlib
Cómo ejecutar la aplicación: 
- Abre nuevamente la terminal.
- Entra a la carpeta donde está el archivo principal del proyecto.
- Ejecuta Streamlit con el siguiente comando:
                      streamlit run app.py
- Finalmente la aplicación se abrirá automáticamente en tu navegador. Desde ahí se podrán usar todas las funciones (elegir gráficos, filtrar continentes, revisar la tabla completa, descargar los datos y navegar entre las distintas secciones).

Importante: 
- La aplicación requiere internet para poder cargar los datos, ya que, se obtienen directamente desde la API pública RestCountries.
- Si en algún momento no aparece la información, puede deberse a problemas de conexión o a que la API no esté disponible temporalmente.
