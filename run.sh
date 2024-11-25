# Opción 1: Usar variable de entorno
export NODE_OPTIONS="--max-old-space-size=4096"

# Opción 2: Modificar el script de build en package.json
{
  "scripts": {
    "build": "NODE_OPTIONS='--max-old-space-size=4096' npm run pyodide:fetch && vite build"
  }
}