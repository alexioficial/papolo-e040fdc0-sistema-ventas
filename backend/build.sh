#!/bin/bash
# Script para construir el frontend y copiarlo al backend
set -e

echo "📦 Instalando dependencias del frontend..."
cd frontend
npm install

echo "🔨 Construyendo frontend..."
npm run build

echo "📁 Copiando build al backend..."
rm -rf ../backend/static
cp -r build ../backend/static

echo "✅ Build completado. Frontend disponible en backend/static/"
