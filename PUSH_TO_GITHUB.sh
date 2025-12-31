#!/bin/bash

echo "╔════════════════════════════════════════════════════════════════════════╗"
echo "║                                                                        ║"
echo "║           JARVISCO - PUSH TO GITHUB (sanchezsase1991-sys)              ║"
echo "║                                                                        ║"
echo "╚════════════════════════════════════════════════════════════════════════╝"

cd ~/JarvisCO

echo ""
echo "📝 Configuración actual:"
git config user.name
git config user.email
echo "🔗 Remote: $(git config --get remote.origin.url)"
echo ""

echo "⚠️  REQUISITO: GitHub Personal Access Token"
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""
echo "Necesitas crear un token en GitHub si no lo tienes:"
echo "1. Ir a: https://github.com/settings/tokens"
echo "2. Click 'Generate new token (classic)'"
echo "3. Nombre: JarvisCO Push"
echo "4. Permisos: seleccionar 'repo' (full control)"
echo "5. Copiar el token generado"
echo ""
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""

read -sp "🔐 Ingresa tu GitHub Personal Access Token: " GITHUB_TOKEN
echo ""
echo ""

if [ -z "$GITHUB_TOKEN" ]; then
    echo "❌ Token vacío. Operación cancelada."
    exit 1
fi

echo "🚀 Pushing to GitHub..."
echo ""

# Crear URL con token
REPO_URL="https://sanchezsase1991-sys:${GITHUB_TOKEN}@github.com/sanchezsase1991-sys/JarvisCO.git"

# Push
git push -u origin main --force 2>&1 | tail -20

echo ""
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""

if [ $? -eq 0 ]; then
    echo "✅ PUSH EXITOSO!"
    echo ""
    echo "🎉 Tu repositorio JarvisCO está ahora público en GitHub:"
    echo ""
    echo "   https://github.com/sanchezsase1991-sys/JarvisCO"
    echo ""
    echo "═══════════════════════════════════════════════════════════════════════════"
    echo ""
    echo "📋 Próximos pasos recomendados:"
    echo ""
    echo "1. Ir a GitHub y verificar que todo esté correcto"
    echo "2. (Opcional) Crear una Release:"
    echo "   - Tag: v1.0.0"
    echo "   - Título: JarvisCO 1.0.0 - Copilot-Level"
    echo ""
    echo "3. (Opcional) Agregar topics:"
    echo "   - code-analysis, copilot, mistral, code-generation, python"
    echo ""
    echo "4. (Opcional) Publicar en PyPI cuando esté listo:"
    echo "   - python setup.py sdist bdist_wheel"
    echo "   - twine upload dist/*"
    echo ""
else
    echo "❌ PUSH FALLÓ"
    echo ""
    echo "Verifica:"
    echo "1. Token es válido"
    echo "2. Repositorio existe en GitHub"
    echo "3. Tienes permisos de escritura"
    echo ""
fi

echo "═══════════════════════════════════════════════════════════════════════════"
